"""Assemble the private GitLab Pages site from versioned MkDocs manuals."""

import html
import os
import re
import subprocess
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config


ROOT = Path(__file__).resolve().parents[1]
VERSION = r"[0-9]+\.[0-9]+(?:\.[0-9]+)?"


def main():
    site = ROOT / "site"
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
        config = load_config(
            config_file=str(manuals[version]),
            site_dir=str(destination),
            site_url=f"{pages_url}/manual/{version}/" if pages_url else None,
            strict=True,
        )
        expected = ROOT / "release-notes" / version
        if Path(config.docs_dir).resolve() != expected:
            raise SystemExit(f"Manual {version} must read {expected.relative_to(ROOT)}")
        build(config)
        if not (destination / "index.html").is_file():
            raise SystemExit(f"Manual {version} did not produce index.html")
        subprocess.run(
            ["python3", str(ROOT / "tools/check_preview_links.py"), str(destination), str(site)],
            check=True,
        )

    links = "\n".join(
        f'<li><a href="{html.escape(version)}/">OpenQP {html.escape(version)}</a></li>'
        for version in versions
    )
    (public_path / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
        '<title>OpenQP manuals</title>\n<h1>OpenQP manuals</h1>\n'
        '<p><a href="../">Shared manual</a></p>\n<ul>\n'
        f"{links}\n</ul>\n</html>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
