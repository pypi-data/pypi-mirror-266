import contextvars
from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from bs4 import PageElement
from bs4.element import Tag

from .mixins import TagMixins

if TYPE_CHECKING:
    from ..component import Component

weba_html_context: contextvars.ContextVar[Any] = contextvars.ContextVar("current_weba_html_context")


class TagContextManager(TagMixins):
    _html: "Component"
    _tag: Tag
    _component: Optional["Component"]

    def __init__(self, tag: Tag, html: "Component", component: Optional["Component"] = None):
        self._tag = tag
        self._html = html
        self._component = component
        self._content = None

    def __enter__(self) -> Tag:  # Push the tag onto the instance's context stack
        self._html._context_stack.append(self._tag)  # type: ignore (we need to access private property

        return self._tag

    def __exit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any):
        # Pop the tag from the instance's context stack
        if hasattr(self._html, "_context_stack") and self._html._context_stack:  # type: ignore (we need to access private property
            self._html._context_stack.pop()  # type: ignore (we need to access private property)

    def __getitem__(self, key: str) -> Union[Any, list[str]]:
        if key == "class":
            attr = self._tag.get(key)

            if not isinstance(attr, list):
                attr = [attr] if attr else []
                self._tag[key] = attr  # Update the attribute to be a list

        return self._tag.__getitem__(key)

    def __getattr__(self, name: str) -> "TagContextManager":
        response = getattr(self._tag, name)

        if response.__class__.__name__ == "Tag":
            return self._tag_context_manager(response)

        return response

    def __copy__(self) -> "TagContextManager":
        return self._tag_context_manager(copy(self._tag))

    def insert(self, position: int, new_child: PageElement | str) -> None:
        if hasattr(new_child, "content") and new_child.content is not None:  # type: ignore
            self._tag.insert(position, new_child.content)  # type: ignore
        elif hasattr(new_child, "_tag") and new_child._tag is not None:  # type: ignore
            self._tag.insert(position, new_child._tag)  # type: ignore
        else:
            self._tag.insert(position, new_child)

    def extract(self, self_index: Optional[int] = None):
        return self._tag_context_manager(self._tag.extract(self_index))

    def _tag_context_manager(self, tag: Tag) -> "TagContextManager":
        return tag if self._html._context_stack else TagContextManager(tag, self._html, self._component)  # type: ignore (we need to access private property)

    # TODO: Fix typing
    def replace_with(self, tag: Any, *args: Any):  # type: ignore
        new_tag = tag

        if new_tag._is_component:
            new_tag = copy(tag.content)  # type: ignore

            if self._component and tag._content_to_append:  # type: ignore
                tag._content_to_append.extract(-1)
            elif self._html._tags_to_remove:  # type: ignore
                self._html._tags_to_remove.append(tag)  # type: ignore

        new_args = [new_tag] + list(args[1:]) if args.__len__() > 1 else [new_tag]

        self._tag.replace_with(*new_args)

        # NOTE: bs4 returns self, we return the new tag to make it easier to modify after the fact
        return new_tag
