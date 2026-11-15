"""Stage just the approved 1.3 home page with a link to the 1.4 changes."""

import argparse
import hashlib
from pathlib import Path


VERSION_ROW = (
    b"<p><strong>Manual version:</strong> 1.3.0; "
    b"<strong>OpenQP version:</strong> 1.3.0</p>"
)
SWITCH = (
    b'\n<nav aria-label="Manual version"><ul>'
    b'<li><a href="/manual/" aria-current="page">1.3 manual</a></li>'
    b'<li><a href="/manual/1.4/">1.4 changes</a></li>'
    b"</ul></nav>"
)


def add_switch(home, expected_sha256):
    if hashlib.sha256(home).hexdigest() != expected_sha256:
        raise ValueError("the 1.3 home page differs from the reviewed source")
    if home.count(VERSION_ROW) != 1 or b'href="/manual/1.4/"' in home:
        raise ValueError("expected one 1.3 version row and no existing 1.4 link")
    return home.replace(VERSION_ROW, VERSION_ROW + SWITCH, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("home", type=Path, help="an approved copy of the live 1.3 HTML")
    parser.add_argument("expected_sha256")
    parser.add_argument("output", type=Path, help="new staging file")
    args = parser.parse_args()
    staged = add_switch(args.home.read_bytes(), args.expected_sha256)
    with args.output.open("xb") as stream:
        stream.write(staged)


if __name__ == "__main__":
    main()
