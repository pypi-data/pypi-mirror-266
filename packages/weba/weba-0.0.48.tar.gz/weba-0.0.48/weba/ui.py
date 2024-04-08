from typing import TYPE_CHECKING, Any, Callable, cast  # noqa: I001
from .component import Component, weba_html_context
from .tag.context_manager import TagContextManager

if TYPE_CHECKING:
    from bs4 import Tag


class UIFactory:
    """
    A factory class for creating UI elements dynamically based on tag names.
    """

    # _html: Component

    # def _tag_context_manager(self, tag: Any):
    #     return TagContextManager(tag, self._html)  # type: ignore

    def __getattr__(self, tag_name: str) -> Callable[..., TagContextManager]:
        def create_tag(*args: Any, **kwargs: Any) -> TagContextManager:
            html_context = weba_html_context.get(None)

            if html_context is None or not callable(html_context.new_tag):
                html_context = Component()
                weba_html_context.set(html_context)

            # self._html = html_context

            tag: Tag = html_context.new_tag(tag_name, **kwargs)  # type: ignore

            if args:
                tag.string = str(args[0])

            # tag = tag if hasattr(tag, "_tag") else TagContextManager(tag, html_context)

            if html_context._context_stack:  # type:ignore
                html_context._append_to_context(tag._tag)  # type:ignore

            if html_context._last_component is None:  # type:ignore
                html_context._last_component = tag  # type:ignore

            return cast(
                TagContextManager,
                tag,
            )

        return create_tag


ui = UIFactory()
