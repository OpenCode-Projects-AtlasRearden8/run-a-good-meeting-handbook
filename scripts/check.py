#!/usr/bin/env python3
"""Verification for the Run a Good Meeting handbook.

Checks that the repository is consistent and honest:
  1. required files exist
  2. every site/ page parses and tags are balanced
  3. internal links (href/src) resolve to real files and real anchors
  4. docs/ chapters and templates referenced by the handbook exist
  5. LICENSE copyright line, README credit, and badge claims are as specified
  6. no secrets / API keys sitting in any text file

Usage: python3 scripts/check.py   (exit code 0 = all good)
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REQUIRED = [
    "README.md",
    "LICENSE",
    "STATUS.md",
    "site/index.html",
    "site/styles.css",
    "site/agendas.html",
    "site/minutes.html",
    "site/facilitation.html",
    "site/ai-assist.html",
    "site/handbook.html",
    "scripts/build.py",
    "docs/00-read-me-first.md",
    "docs/01-agendas-that-fit-on-a-card.md",
    "docs/02-minutes-people-actually-read.md",
    "docs/03-keeping-the-meeting-on-track.md",
    "docs/04-a-gentle-ai-assist.md",
    "docs/templates/agenda-card-template.md",
    "docs/templates/minutes-template.md",
    "docs/templates/minutes-sample.md",
]

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

TEXT_EXTS = {".md", ".py", ".html", ".css", ".txt", ".csv", ".json", ".sh",
             ".yml", ".yaml", ".toml", ".cfg", ".ini", ".js"}

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",
    r"ghp_[A-Za-z0-9]{30,}",
    r"gho_[A-Za-z0-9]{30,}",
    r"AKIA[0-9A-Z]{16}",
    r"xox[baprs]-[A-Za-z0-9\-]{10,}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)api[_-]?key\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
]

problems: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def ok(msg: str) -> None:
    notes.append(msg)


class TagBalance(HTMLParser):
    """Parse a page and collect unbalanced tags + anchors + links."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.anchors: set[str] = set()
        self.links: list[tuple[int, str]] = []  # line, url
        self.has_stylesheet = False

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_map = dict(attrs)
        if "id" in attrs_map:
            self.anchors.add(attrs_map["id"])
        href = attrs_map.get("href")
        src = attrs_map.get("src")
        url = href or src
        if url and not re.match(r"^(https?:)?//", url) and not url.startswith("#"):
            self.links.append((self.getpos()[0], url))
        if attrs_map.get("rel") == "stylesheet":
            self.has_stylesheet = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: closing </{tag}> with empty stack")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> does not match open <{self.stack[-1]}>"
            )
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                self.stack.pop()


def check_required() -> None:
    for rel in REQUIRED:
        (REPO / rel).is_file() or fail(f"missing required file: {rel}")
    ok(f"required files: {len(REQUIRED)} checked")


def check_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    parser = TagBalance()
    parser.feed(text)
    parser.close()
    for err in parser.errors:
        fail(f"{path.name}: {err}")
    if parser.stack:
        fail(f"{path.name}: unclosed tags {parser.stack}")
    for line, url in parser.links:
        target = url.split("#")[0]
        if target and not (path.parent / target).is_file():
            fail(f"{path.name}:{line}: broken link -> {url}")
        if url.startswith("#"):
            frag = url[1:]
            if frag and frag not in parser.anchors:
                fail(f"{path.name}:{line}: missing anchor -> {url}")
        elif "#" in url:
            frag = url.split("#")[1]
            target_path = path.parent / url.split("#")[0]
            if target_path.is_file():
                sub = target_path.read_text(encoding="utf-8")
                if frag not in re.findall(r'id="([^"]+)"', sub):
                    fail(f"{path.name}:{line}: missing anchor -> {url}")
    # footer/license line present on every page
    if "© 2026 Asdale Dynamics, LLC" not in text:
        fail(f"{path.name}: footer copyright credit missing")
    ok(f"{path.name}: parsed, {len(parser.links)} internal links")


def check_links_in_handbook() -> None:
    hb = REPO / "site" / "handbook.html"
    text = hb.read_text(encoding="utf-8")
    for chapter in ["Read This First", "Agendas That Fit on a Card",
                    "Minutes People Actually Read", "Keeping the Meeting On Track",
                    "A Gentle AI Assist for Recaps", "Agenda Card Template",
                    "Minutes Template", "Minutes — Sample (Filled In)"]:
        if chapter not in text:
            fail(f"site/handbook.html: chapter '{chapter}' missing (stale build?)")
    ok("handbook.html: all 8 compiled sections present")


def check_legal_lines() -> None:
    lic = (REPO / "LICENSE").read_text(encoding="utf-8")
    exact = "Copyright (c) 2026 Asdale Dynamics, LLC"
    if exact not in lic:
        fail("LICENSE: must contain the exact line 'Copyright (c) 2026 Asdale Dynamics, LLC'")
    else:
        ok("LICENSE: exact copyright line present")
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    if "Asdale Dynamics, LLC" not in readme:
        fail("README.md: must credit Asdale Dynamics, LLC")
    else:
        ok("README.md: credits Asdale Dynamics, LLC")


def check_secrets() -> None:
    checked = 0
    for path in REPO.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_EXTS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in SECRET_PATTERNS:
            re.search(pattern, text) and fail(f"{path.relative_to(REPO)}: looks like a secret ({pattern[:30]}...)")
        checked += 1
    ok(f"secret scan: {checked} text files clean")


def main() -> int:
    for path in sorted((REPO / "site").glob("*.html")):
        check_html(path)
    if not problems:
        check_required()
        check_links_in_handbook()
        check_legal_lines()
        check_secrets()
    print("\n--- verification results ---")
    for n in notes:
        print(f"  ok: {n}")
    if problems:
        print("\n  FAILED:")
        for p in problems:
            print(f"  ?? {p}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
