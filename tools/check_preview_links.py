"""Check that a complete versioned manual is self-contained."""

import argparse
from functools import cache
from hashlib import file_digest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = set()
        self.anchors = set()
        self.navigation = set()
        self.canonical = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if anchor := attrs.get("id"):
            self.anchors.add(anchor)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])
            return
        if "md-nav__link" in attrs.get("class", "").split() and attrs.get("href"):
            self.navigation.add(attrs["href"])
        for key in ("href", "src", "poster"):
            if attrs.get(key):
                self.links.add(attrs[key])


@cache
def read_page(path):
    return Page(path)


def read_hash(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def check(preview, stable, site_url):
    url = site_url.rstrip("/") + "/"
    base = urlsplit(url)
    if base.scheme not in {"http", "https"} or not base.netloc:
        raise ValueError(f"Expected an absolute versioned site URL: {site_url!r}")
    version_path = base.path
    pages = set(preview.rglob("index.html"))
    assembled = preview.is_relative_to(stable / "manual")
    shared_files = [
        path for path in stable.rglob("*")
        if path.is_file() and not (assembled and path.is_relative_to(stable / "manual"))
    ]
    stable_routes = {page.relative_to(stable) for page in shared_files if page.name == "index.html"}
    routes = {page.relative_to(preview) for page in pages}
    if not stable_routes or not {Path("index.html"), Path("quickstart/index.html")} <= routes:
        raise ValueError("expected shared and versioned manuals with home and quickstart routes")
    if missing := stable_routes - routes:
        raise ValueError(f"Missing shared routes: {sorted(missing)}")

    stable_nav = {
        href for href in read_page(stable / "index.html").navigation
        if not urlsplit(href).netloc
    }
    version_nav = read_page(preview / "index.html").navigation
    if missing := stable_nav - version_nav:
        raise ValueError(f"Missing shared navigation: {sorted(missing)}")

    # Compare the version-independent output of MkDocs, including example decks,
    # images, stylesheets, JavaScript, and downloadable data.
    generated = {"search/search_index.json", "sitemap.xml", "sitemap.xml.gz", "404.html"}
    assets = [
        path for path in shared_files
        if path.relative_to(stable).as_posix() not in generated
        and path.name != "index.html"
    ]
    for source in assets:
        target = preview / source.relative_to(stable)
        if not target.is_file() or read_hash(source) != read_hash(target):
            raise ValueError(f"Missing or changed shared asset: {source.relative_to(stable)}")

    checked = set()
    broken = []
    for page in sorted(pages):
        route = page.relative_to(preview).as_posix().removesuffix("index.html")
        page_url = url + route
        rendered = read_page(page)
        if rendered.canonical != [page_url]:
            raise ValueError(f"{route}: wrong canonical URL: {rendered.canonical}")
        for href in sorted(rendered.links):
            target = urlsplit(urljoin(page_url, href))
            if href == "../" and not route:
                # The home-page version switch deliberately returns to the
                # version list. All other local links must stay in this manual.
                continue
            original = urlsplit(href)
            if target.netloc != base.netloc or target.scheme not in ("http", "https"):
                if target.hostname in {"www.openqp.org", "openqp.org"} and target.path.startswith("/manual"):
                    raise ValueError(f"{route}: escaped to the public manual: {href}")
                if target.hostname == "open-quantum-platform.github.io" and target.path.startswith("/openqp-docs"):
                    raise ValueError(f"{route}: escaped to the GitHub manual: {href}")
                continue
            if original.netloc or href.startswith("/") or not target.path.startswith(version_path):
                raise ValueError(f"{route}: non-relative or out-of-version link: {href}")
            relative = unquote(target.path.removeprefix(version_path))
            destination = (preview / relative).resolve()
            if not destination.is_relative_to(preview):
                raise ValueError(f"{route}: link escapes the manual: {href}")
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                broken.append(f"{route}: missing link or asset: {href}")
                continue
            if target.fragment and unquote(target.fragment) not in read_page(destination).anchors:
                broken.append(f"{route}: missing anchor: {href}")
                continue
            checked.add((target.path, target.fragment))
    if broken:
        raise ValueError("\n".join(broken))
    print(f"{len(routes)} versioned pages, {len(stable_routes)} shared routes, "
          f"{len(stable_nav)} shared navigation links, {len(assets)} unchanged assets, "
          f"{len(checked)} relative link and anchor targets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview", type=Path)
    parser.add_argument("stable", type=Path)
    parser.add_argument("site_url")
    args = parser.parse_args()
    check(args.preview.resolve(), args.stable.resolve(), args.site_url)
