"""Assemble the private GitLab Pages site from versioned MkDocs manuals."""

import argparse
import html
import os
import re
from pathlib import Path

from build_versioned_manual import VERSION, build_version
from check_preview_links import check
from stage_manual_version_switch import VERSION_ROW


ROOT = Path(__file__).resolve().parents[1]


def main(site):
    site = site.resolve()
    if not (site / "index.html").is_file():
        raise SystemExit("Shared manual was not built at site/index.html")

    manuals = {}
    for path in ROOT.glob("mkdocs-*.yml"):
        match = re.fullmatch(rf"mkdocs-({VERSION})\.yml", path.name)
        if match:
            manuals[match[1]] = path
    if not manuals:
        raise SystemExit("No versioned MkDocs manual configurations found")

    release_ref = os.environ.get("OQP_MANUAL_RELEASE_REF", "")
    if release_ref:
        match = re.fullmatch(rf"release/({VERSION})", release_ref)
        if not match or match[1] not in manuals:
            raise SystemExit(f"No matching manual configuration for {release_ref!r}")

    public_path = site / "manual"
    pages_url = os.environ.get("CI_PAGES_URL", "").rstrip("/")
    if os.environ.get("CI_PROJECT_ID") == "34" and not pages_url:
        raise SystemExit("Private GitLab Pages did not set CI_PAGES_URL")

    versions = sorted(manuals, key=lambda value: tuple(map(int, value.split("."))), reverse=True)
    for version in versions:
        destination = public_path / version
        site_url = f"{pages_url or 'http://localhost:8000'}/manual/{version}/"
        build_version(version, destination, site_url)
        check(destination, site, site_url)

    home = site / "index.html"
    data = home.read_bytes()
    switch = b'<p><a href="manual/">Switch manual version</a></p>'
    if data.count(VERSION_ROW) != 1 or switch in data:
        raise SystemExit("Expected the original shared manual home")
    home.write_bytes(data.replace(VERSION_ROW, VERSION_ROW + b"\n" + switch, 1))

    links = "\n".join(
        f'<li><a href="{html.escape(version)}/">OpenQP {html.escape(version)}</a></li>'
        for version in versions
    )
    (public_path / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
        '<title>OpenQP manuals</title>\n<h1>OpenQP manuals</h1>\n'
        '<ul><li><a href="../">OpenQP 1.3</a></li>\n'
        f"{links}\n</ul>\n</html>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, nargs="?", default=ROOT / "site")
    main(parser.parse_args().site)
