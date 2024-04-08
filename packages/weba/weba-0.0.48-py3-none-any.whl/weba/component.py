import asyncio
import contextvars
import inspect
import os
from typing import (
    Any,
    Callable,
    Coroutine,
    Iterable,
    Optional,
    Pattern,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

from bs4 import BeautifulSoup
from bs4.element import Tag

from .env import env
from .tag import TagContextManager, TagDescriptor, TagMixins
from .types import TypedDictClass
from .utils import clean_comments, load_html_to_soup

weba_html_context: contextvars.ContextVar[Any] = contextvars.ContextVar("current_weba_html_context")


Incomplete: TypeAlias = Any
_SimpleStrainable: TypeAlias = str | bool | None | bytes | Pattern[str] | Callable[[str], bool] | Callable[[Tag], bool]
_Strainable: TypeAlias = _SimpleStrainable | Iterable[_SimpleStrainable]
_SimpleNormalizedStrainable: TypeAlias = (
    str | bool | None | Pattern[str] | Callable[[str], bool] | Callable[[Tag], bool]
)
_NormalizedStrainable: TypeAlias = _SimpleNormalizedStrainable | Iterable[_SimpleNormalizedStrainable]

Render = None | Coroutine[Any, Any, None]

T = TypeVar("T", bound="Component")
Y = TypeVar("Y")


# Define the tag decorator with overloads to handle different usage patterns
@overload
def tag(method: Callable[[T], Tag | TagContextManager]) -> TagDescriptor[T]:
    ...


@overload
def tag(
    selector: str, *, extract: Optional[bool] = False, clear: Optional[bool] = False, strict: Optional[bool] = True
) -> Callable[
    [Callable[[T, TagContextManager], None | Tag | TagContextManager] | Callable[[T], None | Tag | TagContextManager]],
    TagDescriptor[T],
]:
    ...


def tag(*args: Any, **kwargs: Any) -> Union[TagDescriptor[T], Callable[[Callable[[T], Any]], TagDescriptor[T]]]:  # type: ignore
    if len(args) == 1 and callable(args[0]):
        method = args[0]
        Component._tag_methods.append(method.__name__)  # type: ignore (we need to access private property)
        # This is the decorator usage without arguments
        return TagDescriptor(method)
    else:
        # This is the decorator usage with arguments
        selector = args[0] if args else None
        extract = kwargs.get("extract", False)
        clear = kwargs.get("clear", False)
        strict = kwargs.get("strict", True)

        def decorator(method: Callable[[T], None]) -> TagDescriptor[T]:
            Component._tag_methods.append(method.__name__)  # type: ignore (we need to access private property)

            return TagDescriptor(method, selector=selector, extract=extract, clear=clear, strict=strict)  # type: ignore

        return decorator


class ComponentContext(TypedDictClass):
    pass


# HACK: We are using a metaclass to ensure __init__ only gets called once
class Meta(type):
    def __call__(cls: Type[Y], *args: Any, **kwargs: Any) -> Y:
        # sourcery skip: instance-method-first-arg-name
        return cls.__new__(cls, *args, **kwargs)  # type: ignore


_component_loaded_src: dict[str, str] = {}


class Component(TagMixins, metaclass=Meta):
    _render_coro: Union[
        None,
        Coroutine[Any, Any, BeautifulSoup],
    ]
    _content: TagContextManager
    _component_content: TagContextManager
    _content_to_append: Union[BeautifulSoup, TagContextManager, list[Tag], "Component"]
    _tag_methods: list[str] = []  # Declare the class attribute
    _tags: dict[str, TagContextManager] = {}
    _tags_called: set[str] = set()
    _context_stack: list[Tag]
    _context_token: Optional[contextvars.Token[Any]]
    _render_cache: Optional[TagContextManager]
    _is_component = True
    _is_rendering = False
    _last_component: Optional["Component"]

    src: Optional[str] | BeautifulSoup
    src_cache_key: Optional[str] = ""

    def __new__(cls, *args: Any, **kwargs: Any):
        instance = super().__new__(cls)

        instance.src = None
        instance.src_cache_key = cls.__name__
        instance._render_cache = None
        instance._context_stack = []
        instance._last_component = None
        instance._is_rendering = False
        instance._render_coro = None

        # Define a function to cache the result of the render method
        def cache_render_result(func: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not instance._render_cache:
                    instance._render_cache = func(*args, **kwargs)

                return instance._render_cache

            return wrapper

        # Wrap the render method with the caching function
        instance.render = cache_render_result(instance.render)

        # Check if the html context is set, otherwise create a new one
        html_context = weba_html_context.get(None)

        if html_context is None:
            # Create a new HTML context for this component
            html_context = instance
            # Set the new HTML context in the context variable
            instance._context_token = weba_html_context.set(html_context)

        instance._html = html_context
        instance.context = html_context  # type: ignore

        # check if __init__ takes any arguments
        if inspect.signature(instance.__init__).parameters:
            instance.__init__(*args, **kwargs)

        cls_path = inspect.getfile(cls)
        cls_dir = os.path.dirname(cls_path)

        if env.is_prd:
            global _component_loaded_src

            loaded_src_key = f"{cls.__name__}_{cls_path}_{instance.src_cache_key}"

            content = _component_loaded_src.get(loaded_src_key)

            if not content:
                src = instance.src or (cls.src if hasattr(cls, "src") else "--html")

                if src:
                    content = _component_loaded_src[loaded_src_key] = str(src)
                else:
                    content = "--html"
        else:
            content = instance.src or (cls.src if hasattr(cls, "src") else "--html")

        instance._content = load_html_to_soup(content, base_dir=cls_dir)  # type: ignore (we need to access private property)
        instance._tags = {}
        instance._tags_called = set()

        # Call the subclass's render method to modify the content
        render_result = instance.render()

        # loop through the _tags that are set and just call them to make sure they get added to the content
        for tag_method in instance.__class__._tag_methods:
            getattr(instance, tag_method)

        if render_result is None:
            render_result = instance._content
            instance._render_cache = render_result  # type: ignore

        # If render_result is a coroutine, store it for later execution
        if asyncio.iscoroutine(render_result):
            instance._render_coro = render_result
        else:
            # If render_result is not None, use it as the content to append
            # Otherwise, use instance._content if it's not None
            instance._content_to_append = render_result if render_result is not None else instance.content  # type: ignore

            instance._append_contexts()

        instance.reset_context()

        if not instance.__class__.__name__.endswith("Layout") and not html_context._is_rendering:
            html_context._last_component = instance

        return instance

    def __init__(self):
        pass

    def render(
        self,
    ) -> Union[
        BeautifulSoup,
        Coroutine[Any, Any, Union[None, TagContextManager, Tag, BeautifulSoup]],
        TagContextManager,
        Tag,
        None,
    ]:
        # This method should be overridden by subclasses to modify self._content
        # It can return a BeautifulSoup object, a coroutine, or None
        return self.content

    def _append_contexts(self):
        if isinstance(self._content_to_append, Tag):
            self._append_to_context(self._content_to_append)  # type: ignore
        elif self._content_to_append is not None and isinstance(self._content_to_append, list):  # type: ignore
            [self._append_to_context(tag) for tag in self._content_to_append]  # type: ignore

    def _append_to_context(self, content: Union[BeautifulSoup, TagContextManager]):
        if self._html._context_stack:  # type: ignore (we need to access private property)
            self._html._context_stack[-1].append(content)  # type: ignore (we need to access private property)

    def __await__(self):  # type: ignore
        yield from self._execute_render().__await__()

        return self  # type: ignore

    def __enter__(self):
        if not weba_html_context.get(None):
            self._context_token = weba_html_context.set(self)

        # NOTE: this makes sure the content is available in the context manager
        if self._html._context_stack:  # type: ignore (we need to access private property)
            self._content = self._content_to_append = self._html._context_stack.pop()  # type: ignore (we need to access private property)

        return self

    def __aenter__(self):
        return self.__enter__()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._reset_weba_context()

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._reset_weba_context()

    def _reset_weba_context(self) -> None:
        if hasattr(self, "_context_token") and self._context_token is not None:
            weba_html_context.reset(self._context_token)
            self._context_token = None

    def reset_context(self) -> None:
        self._reset_weba_context()

    def reset(self) -> None:
        self._reset_weba_context()

    def output_ready(self, _):
        return str(self.content)

    # if a method doesn't exist try calling it on self._content
    def __getattr__(self, name: str):
        if name not in ["_content", "context"] and hasattr(self.content, name):
            response = getattr(self.content, name)

            if isinstance(response, Tag):
                return self._tag_context_manager(response)

            return response

        # raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _tag_context_manager(self, tag: Tag):
        return TagContextManager(tag, self._html, self)  # type: ignore

    def __str__(self):
        return clean_comments(str(self._render_cache)) if self._render_cache else clean_comments(str(self.content))

    async def _execute_render(self):
        self.context._is_rendering = True  # type: ignore

        if self._render_coro is None:
            return

        if callable(self._render_coro):
            content_to_append = await self._render_coro()  # type: ignore
        else:
            content_to_append = await self._render_coro

        if content_to_append is None:
            content_to_append = self._content

        self._render_cache = content_to_append  # type: ignore

        self._append_to_context(content_to_append)  # type: ignore

    @property
    def content(self) -> TagContextManager:
        return self._render_cache or self._content

    @property
    def html(self) -> TagContextManager:
        return self.content
