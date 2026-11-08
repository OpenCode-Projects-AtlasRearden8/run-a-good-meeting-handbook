#!/usr/bin/env python3
"""Build site/handbook.html — a single printable page containing every
docs/ chapter and template — from the markdown sources in docs/.

Usage: python3 scripts/build.py
Run from the repository root (or anywhere; paths are repo-relative).
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
OUT = REPO / "site" / "handbook.html"

CHAPTERS = [
    "docs/00-read-me-first.md",
    "docs/01-agendas-that-fit-on-a-card.md",
    "docs/02-minutes-people-actually-read.md",
    "docs/03-keeping-the-meeting-on-track.md",
    "docs/04-a-gentle-ai-assist.md",
    "docs/templates/agenda-card-template.md",
    "docs/templates/minutes-template.md",
    "docs/templates/minutes-sample.md",
]

# docs/*.md cross-links are rendered as plain emphasized text (all content
# is inline on this page) except external http links, which stay links.
INTERNAL_MD = re.compile(r"\[([^\]]+)\]\((?!https?://)[^)]+\.md\)")


def md_to_html(md: str) -> str:
    """Minimal markdown renderer for the constructs used in docs/."""
    out: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_stack: list[str] = []  # 'ul' | 'ol'

    def close_list():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    def inline(text: str) -> str:
        text = html.escape(text, quote=True)
        text = INTERNAL_MD.sub(lambda m: m.group(1), text)
        text = re.sub(r"\[([^[\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        return text

    def flush_code():
        if code_lines:
            out.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
            code_lines.clear()

    for raw in md.splitlines():
        if raw.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                close_list()
                flush_code()
                in_code = True
            continue
        if in_code:
            code_lines.append(html.escape(raw, quote=False))
            continue

        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            close_list()
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1)) + 1  # # -> h2 on this page
            slug = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append(f'<h{level} id="{slug}">{inline(m.group(2))}</h{level}>')
            continue

        if re.match(r"^-{3,}$", stripped):
            close_list()
            out.append("<hr>")
            continue

        m = re.match(r"^>\s?(.*)$", stripped)
        if m:
            close_list()
            out.append(f"<blockquote>{inline(m.group(1))}</blockquote>")
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if not list_stack or list_stack[-1] != "ul":
                close_list()
                out.append("<ul>")
                list_stack.append("ul")
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        m = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m:
            if not list_stack or list_stack[-1] != "ol":
                close_list()
                out.append("<ol>")
                list_stack.append("ol")
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        close_list()
        out.append(f"<p>{inline(stripped)}</p>")

    flush_code()
    close_list()
    return "\n".join(out)


def page_shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="Every chapter and template of the Run a Good Meeting handbook on one printable page.">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site">
    <div class="wrap">
      <p class="kicker">Asdale Dynamics, LLC · Free Handbook</p>
      <h1>Run a Good Meeting</h1>
      <p class="tagline">The full handbook — every chapter and template, one page, ready to print.</p>
    </div>
  </header>

  <nav class="top" aria-label="Main pages">
    <div class="wrap">
      <ul>
        <li><a href="index.html">Home</a></li>
        <li><a href="agendas.html">Agendas</a></li>
        <li><a href="minutes.html">Minutes</a></li>
        <li><a href="facilitation.html">On Track</a></li>
        <li><a href="ai-assist.html">AI Assist</a></li>
        <li><a href="handbook.html" aria-current="page">Full Handbook</a></li>
      </ul>
    </div>
  </nav>

  <main>
    <div class="wrap">
{body}
      <hr>
      <p style="color: var(--muted); font-size: 0.9rem;">© 2026 Asdale Dynamics, LLC · MIT License · Generated from the <code>docs/</code> markdown sources by <code>scripts/build.py</code>.</p>
    </div>
  </main>

  <footer class="site">
    <div class="wrap">
      <p>Run a Good Meeting · © 2026 Asdale Dynamics, LLC · MIT License · <a href="index.html">Back to home</a></p>
    </div>
  </footer>
</body>
</html>
"""


def main() -> int:
    parts: list[str] = []
    for rel in CHAPTERS:
        path = REPO / rel
        if not path.is_file():
            print(f"error: missing source {rel}", file=sys.stderr)
            return 1
        parts.append(f'<!-- source: {rel} -->\n{md_to_html(path.read_text(encoding="utf-8"))}')

    OUT.write_text(page_shell("Run a Good Meeting — Full Handbook", "\n".join(parts)), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
