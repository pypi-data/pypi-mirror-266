import contextvars
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

# from bs4.element import Tag
from .context_manager import TagContextManager as Tag

weba_html_context: contextvars.ContextVar[Any] = contextvars.ContextVar("current_weba_html_context")

if TYPE_CHECKING:
    from ..component import Component

# Define a type variable with an upper bound of `Component`
T = TypeVar("T", bound="Component")


class WebaTagError(Exception):
    pass


class TagDescriptor(Generic[T]):
    def __init__(
        self,
        method: Callable[[T], Tag],
        selector: Optional[str] = None,
        extract: bool = False,
        clear: bool = False,
        strict: bool = True,
    ):
        self._method = method
        self._method_name = method.__name__
        self._selector = selector
        self._extract = extract
        self._clear = clear
        self._strict = strict

    def __get__(self, instance: Union[T, None], owner: Type[T]) -> Tag:
        if instance is None:
            class_path = f"{instance.__class__.__module__}.{instance.__class__.__qualname__}"
            raise WebaTagError(f"{self._method_name} is only accessible on instances of {class_path}")

        tag = instance._tags.get(self._method_name)  # type: ignore (we need to access private property)

        if tag is None:
            if self._selector:
                found_tag = instance.select_one(self._selector)

                if not self._strict:
                    return found_tag  # type: ignore

                if found_tag is None:
                    class_path = f"{instance.__class__.__module__}.{instance.__class__.__qualname__}"
                    # show backtrace to instance file
                    raise WebaTagError(f"No tag with selector {self._selector} found in {class_path}")

                if self._extract:
                    tag = found_tag.extract()

                if self._clear:
                    [t.decompose() for t in instance.select(self._selector)]

                # check if method takes a tag as an argument
                if len(self._method.__code__.co_varnames) > 1:
                    tag = self._method(instance, found_tag)  # type: ignore
                # else:
                #     tag = self._method(instance)
                #
                if tag is None:
                    tag = found_tag

            else:
                tag = self._method(instance)

            if not isinstance(tag, Tag):
                tag = Tag(tag, instance._html)  # type: ignore (we need to access private property)

            instance._tags[self._method_name] = tag  # type: ignore (we need to access private property)

            if self._method_name not in instance._tags_called:  # type: ignore (we need to access private property)
                instance._tags_called.add(self._method_name)  # type: ignore (we need to access private property)

        return tag
