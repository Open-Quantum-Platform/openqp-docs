"""Build a complete versioned manual from common sources and release changes."""

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config


ROOT = Path(__file__).resolve().parents[1]
VERSION = r"[0-9]+\.[0-9]+(?:\.[0-9]+)?"


def stage_sources(version, destination):
    common = ROOT / "docs"
    changes = ROOT / "release-notes" / version
    shutil.copytree(common, destination)
    delta = json.loads((changes / "overlay.json").read_text(encoding="utf-8"))

    for name, replacements in delta["replace"].items():
        target = destination / name
        text = target.read_text(encoding="utf-8")
        for old, new in replacements:
            if text.count(old) != 1:
                raise ValueError(f"{version}: expected one match in {name}: {old!r}")
            text = text.replace(old, new, 1)
        target.write_text(text, encoding="utf-8")

    append = set(delta["append"])
    for source in sorted(changes.rglob("*")):
        if not source.is_file() or source == changes / "overlay.json":
            continue
        name = source.relative_to(changes)
        target = destination / name
        if name.as_posix() in append:
            # Preserve the common page title and section anchors.
            heading, _, body = source.read_text(encoding="utf-8").partition("\n")
            if not heading.startswith("# ") or not body.strip():
                raise ValueError(f"{version}: expected a titled supplement: {name}")
            text = target.read_text(encoding="utf-8")
            target.write_text(text.rstrip() + "\n\n" + body.lstrip(), encoding="utf-8")
            append.remove(name.as_posix())
        else:
            if target.exists():
                raise ValueError(f"{version}: undeclared overlay collision: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    if append:
        raise ValueError(f"{version}: missing supplements: {sorted(append)}")
    return delta["nav"]


def build_version(version, destination, site_url):
    if not re.fullmatch(VERSION, version):
        raise ValueError(f"Invalid manual version: {version!r}")
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="manual-source-", dir=destination.parent) as work:
        sources = Path(work) / "docs"
        release_nav = stage_sources(version, sources)
        config = load_config(
            config_file=str(ROOT / f"mkdocs-{version}.yml"),
            docs_dir=str(sources),
            site_dir=str(destination),
            site_url=site_url,
            strict=True,
        )
        config.nav.append({"Release notes": release_nav})
        build(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("site_dir", type=Path)
    parser.add_argument("--site-url", required=True, help="Canonical URL including the version path")
    args = parser.parse_args()
    build_version(args.version, args.site_dir, args.site_url)
