import json
import pathlib
from typing import TYPE_CHECKING, Any, NotRequired, Optional, Unpack

from bs4 import NavigableString

from weba import HTML, HTMLKwargs, env, ui

from .tag.context_manager import TagContextManager as Tag

if TYPE_CHECKING:
    from .component import Component


def load_manifest(name: str) -> dict[str, Any]:
    if not env.is_prd:
        return {}

    manifest = pathlib.Path(f"dist/manifest-{name}.json").read_text()

    return json.loads(manifest)


class LayoutKwargs(HTMLKwargs):
    header: NotRequired["Component"]
    main: NotRequired["Component"]
    footer: NotRequired["Component"]


class Layout(HTML):
    src = """--html
        <!doctype html>
        <html lang="en-US">

        <head>
            <title>Weba</title>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        </head>

        <body>
            <header/>
            <main />
            <footer />
        </body>

        </html>
    """

    main: Tag
    footer: Tag

    manifest: dict[str, Any] = load_manifest("main")

    title = "Weba"

    lang = "en-US"

    def __init__(self, *_args: Any, **kwargs: Unpack[LayoutKwargs]):
        self.lang = kwargs.get("lang", self.__class__.lang)
        self.title = kwargs.get("title", self.__class__.title)
        self._last_component: Optional["Component"] = None

    def set_script_and_link_tags(self):
        if env.is_prd:
            self.remove_tags("script")
            self.remove_tags("link")

            # loop over key value pairs in manifest and append to head
            for _, info in self.manifest.items():
                js_file = info["file"]
                css_files = info.get("css", [])

                self.body.append(ui.script(src=f"/{js_file}", type="module", defer="defer"))

                for css_file in css_files:
                    self.head.append(ui.link(href=f"/{css_file}", rel="stylesheet", type="text/css"))

                # NOTE: Until we have proper critical css detection this will slow down the page load using hx-boost
                # for css_file in css_files:
                #     css = pathlib.Path(f"dist/{css_file}").read_text()
                #     self.head.append(ui.style(css))
        else:
            for script in self.select("script"):
                script["src"] = f"{env.script_dev_url_prefix}/{script['src']}"
                script["defer"] = "defer"

    def remove_tags(self, tag_name: str):
        for tag in self.select(tag_name):
            tag.decompose()

    def add(self, page: "Component"):
        # NOTE: If we have already called #add, then we don't need to add it again with #_last_component
        self._last_component = None

        header = page.find("header", recursive=False)
        footer = page.find("footer", recursive=False)
        main = page.find("main", recursive=False) or page

        if self.header and header:
            self.add_content(self.header, "header", header.extract())  # type: ignore

        if self.footer and footer:
            self.add_content(self.footer, "footer", footer.extract())  # type: ignore

        self.add_content(self.main, "main", main)  # type: ignore

    def add_content(self, tag: "Tag", tag_name: str, content: "NavigableString | Tag"):
        if not tag:
            return

        if isinstance(content, NavigableString):
            content = ui.div(content).find().extract()  # type: ignore

        if content.name == tag_name:
            classes = tag["class"]
            attrs = tag.attrs or {}

            self.replace_content(tag_name, tag, content, classes, attrs)  # type: ignore
        else:
            tag.append(content)

    def replace_content(self, tag_name: str, tag: "Tag", content: "Tag", classes: Any, attrs: dict[str, Any]):
        classes = content["class"] if content.has_attr("class") else []
        tag_classes = tag["class"] or []

        if classes:
            for class_ in classes:
                if class_ not in tag_classes:
                    tag_classes.append(class_)

        child_main_attrs = content.attrs

        setattr(self, tag_name, tag.replace_with(content))

        content.attrs = attrs
        content.attrs.update(child_main_attrs)
        content["class"] = tag_classes

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        # Automatically add the last component if it exists
        if self._last_component:
            if self._last_component._render_cache:
                if (
                    hasattr(self._last_component._render_cache, "_content")
                    and self._last_component._render_cache._content is not None
                ):
                    self.add(self._last_component._render_cache._content)  # type: ignore
                else:
                    self.add(self._last_component._render_cache)  # type: ignore
            else:
                self.add(self._last_component)  # type: ignore

            self._last_component = None

        self.set_script_and_link_tags()

        super().__exit__(exc_type, exc_value, traceback)
