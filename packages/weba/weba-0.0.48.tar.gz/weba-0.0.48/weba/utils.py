import inspect
import os
import re
from copy import copy
from pathlib import Path
from typing import (
    IO,
    Any,
    Optional,
)

from bs4 import BeautifulSoup

from .env import env

# html_regex = r"<!-{1,3}.*?-{1,3}>|^--html"
html_regex = r"^--html"
comment_regex = r"<!-{1,3}.*?-{1,3}>"

project_root = os.getcwd()

_cached_html: dict[str, Any] = {}


def clean_html(html: str) -> str:
    """
    Clean an HTML string by removing comments and extra whitespace.
    :param html: The HTML string to clean.
    :return: The cleaned HTML string.
    """
    # Remove comments
    html = re.sub(html_regex, "", html, flags=re.DOTALL)

    # remove extra returns
    html = re.sub(r"\n{1,}", "\n", html)

    return html.strip()


def clean_comments(html: str) -> str:
    """
    Clean an HTML string by removing comments and extra whitespace.
    :param html: The HTML string to clean.
    :return: The cleaned HTML string.
    """

    # Remove comments
    html = re.sub(comment_regex, "", html, flags=re.DOTALL)

    # remove extra returns
    html = re.sub(r"\n{1,}", "\n", html)

    return html.strip()


def load_html_to_soup(
    path: str | Path | BeautifulSoup, parser: str = "html.parser", base_dir: Optional[str] = None
) -> BeautifulSoup:
    """
    Load an HTML file from a specified path and return a BeautifulSoup object.
    The function automatically determines the base path using the caller's file path.

    :param path: The path to the HTML file.
    :return: A BeautifulSoup object of the loaded HTML file.
    """
    if isinstance(path, BeautifulSoup):
        return copy(path)

    # If the path is multiple lines or starts with --html, it contains the HTML
    if isinstance(path, str) and ("\n" in path or path.startswith("--html")):
        file_contents = clean_html(path)

        first_line = file_contents.split("\n")[0]

        if "<?xml" in first_line:
            parser = "xml"

        return BeautifulSoup(file_contents, parser)

    if "~/" in str(path) or bool(re.match(r"^[a-zA-Z]", str(path))):
        path = Path(str(path).replace("~/", ""))

        base_path = project_root
    else:
        # Convert the path to a `Path` object if necessary
        if not isinstance(path, Path):
            path = Path(path)

        # Traverse the stack to find the first frame outside of the 'weba' package
        for frame_info in inspect.stack():
            frame_file = Path(frame_info.filename)

            if "weba" not in frame_file.parts:
                # Use the caller's file path to determine the base path
                base_path = frame_file.parent
                break
            else:
                base_path = None
        else:
            # If no caller is found outside of 'weba', default to the current working directory
            base_path = Path.cwd()

    base_path = Path(base_path)

    resolved_path = (base_path / path).resolve()

    # Ensure the file exists
    if not resolved_path.exists():
        if not base_dir:
            raise FileNotFoundError(f"The file at {resolved_path} does not exist.")

        resolved_path = (Path(base_dir) / path).resolve()

        if not resolved_path.exists():
            resolved_path = path.resolve()

            if not resolved_path.exists():
                raise FileNotFoundError(f"The file at {resolved_path} does not exist.")

    global _cached_html

    if env.is_prd:
        if cached_html := _cached_html.get(str(resolved_path)):
            return BeautifulSoup(cached_html, parser)

    # Read the file and parse it with BeautifulSoup
    with open(resolved_path, "r", encoding="utf-8") as file:
        return _load_file_contents_to_bs4(file, parser, resolved_path)


def _load_file_contents_to_bs4(file: IO[str], parser: str, resolved_path: Path) -> BeautifulSoup:
    global _cached_html

    file_contents = clean_html(file.read())

    first_line = file_contents.split("\n")[0]

    if "<?xml" in first_line:
        parser = "xml"

    _cached_html[str(resolved_path)] = file_contents

    return BeautifulSoup(file_contents, parser)


def update_kwargs(kwargs: dict[str, Any]) -> None:
    """
    Update the kwargs dictionary in place to handle special cases:
    - Converts class variants to 'class'.
    - Converts 'hx_' prefixed keys to 'hx-'.
    - Converts 'for_' to 'for'.
    """
    # Handle different variations of the class attribute
    class_variants = ["_class", "class_", "klass", "cls"]

    for variant in class_variants:
        if variant in kwargs:
            kwargs["class"] = kwargs.pop(variant)
            break

    # Convert 'hx_' prefix to 'hx-' and 'for_' to 'for'
    for key in list(kwargs.keys()):
        if key == "for_":
            kwargs["for"] = kwargs.pop(key)

        if env.ui_attrs_to_dash and key in kwargs:
            new_key = key.replace("_", "-")
            kwargs[new_key] = kwargs.pop(key)
