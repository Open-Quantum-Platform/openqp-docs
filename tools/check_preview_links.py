"""Validate rendered 1.4 navigation and references to the built 1.3 manual."""

import argparse
from functools import cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


HOST = "www.openqp.org"
STABLE = "/manual/"
PREVIEW = "/manual/1.4/"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = set()
        self.anchors = set()
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if anchor := attributes.get("id"):
            self.anchors.add(anchor)
        if tag == "a" and (href := attributes.get("href")):
            self.links.add(href)


@cache
def read_page(path):
    return Page(path)


def check(preview, stable):
    pages = sorted(preview.rglob("index.html"))
    if preview / "index.html" not in pages:
        raise ValueError("the 1.4 preview home was not built")

    checked = set()
    for page in pages:
        route = PREVIEW + page.relative_to(preview).as_posix().removesuffix("index.html")
        base = f"https://{HOST}{route}"
        for href in sorted(read_page(page).links):
            target = urlsplit(urljoin(base, href))
            if target.hostname != HOST or not target.path.startswith(STABLE):
                continue
            if target.path.startswith(PREVIEW):
                root, prefix = preview, PREVIEW
            else:
                root, prefix = stable, STABLE
            relative = unquote(target.path.removeprefix(prefix))
            destination = (root / relative).resolve()
            if not destination.is_relative_to(root):
                raise ValueError(f"{route}: link escapes its manual: {href}")
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                raise ValueError(f"{route}: missing link target: {href}")
            if target.fragment and unquote(target.fragment) not in read_page(destination).anchors:
                raise ValueError(f"{route}: missing anchor: {href}")
            checked.add((target.path, target.fragment))
    print(f"Checked {len(checked)} link and anchor targets in {len(pages)} preview pages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview", type=Path)
    parser.add_argument("stable", type=Path)
    args = parser.parse_args()
    check(args.preview.resolve(), args.stable.resolve())
