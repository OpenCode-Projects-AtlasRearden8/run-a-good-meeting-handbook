# STATUS — Run a Good Meeting

Last verified: 2026-11-08

## What was built

A plain-English handbook for running small-business and club meetings, plus a polished static HTML site with sample agenda and minutes templates. Built as a *manual* (not a tool) — deliberately distinct from the `meeting-notes-summarizer-cli` project, which it complements rather than duplicates.

**Handbook chapters (`docs/`, Markdown):**

| File | Content |
|---|---|
| `docs/00-read-me-first.md` | Orientation: who it's for, the one rule, what this is *not* |
| `docs/01-agendas-that-fit-on-a-card.md` | Card test, three-section structure, five fields, parking lot, failure modes |
| `docs/02-minutes-people-actually-read.md` | Receipt-not-transcript philosophy, four questions minutes answer, five-minute rule |
| `docs/03-keeping-the-meeting-on-track.md` | Seven facilitation situations with word-for-word gentle redirects |
| `docs/04-a-gentle-ai-assist.md` | Rule of thumbs, four copy-paste prompts, privacy-first guardrails |
| `docs/templates/agenda-card-template.md` | Agenda card template + filled-in sample (fictional "Purple Lens Photography Club") |
| `docs/templates/minutes-template.md` | Minutes template + formatting rules |
| `docs/templates/minutes-sample.md` | Fully filled-in minutes sample |

**Static site (`site/`, hand-authored HTML/CSS, no frameworks, no network fonts):**

- `site/index.html` — warm landing page with chapter cards
- `site/agendas.html`, `site/minutes.html`, `site/facilitation.html`, `site/ai-assist.html` — chapter pages; agenda and minutes pages include the templates and filled-in samples
- `site/styles.css` — warm print-friendly design (cream paper, terracotta accent)
- `site/handbook.html` — *generated* single printable page compiling every chapter and template

**Tooling (`scripts/`):**

- `scripts/build.py` — minimal Markdown→HTML converter; regenerates `site/handbook.html` from `docs/`
- `scripts/check.py` — verification suite (details below)

**Housekeeping:** `README.md`, `LICENSE` (MIT, exact line `Copyright (c) 2026 Asdale Dynamics, LLC`), `.gitignore`, `STATUS.md` (this file).

## How to run it

Nothing to install — it's static.

```bash
# read the handbook
open site/index.html            # or just double-click in a file manager
open site/handbook.html         # full single-page version

# optional local preview
python3 -m http.server 8000 --directory site    # http://localhost:8000

# regenerate site/handbook.html after editing docs/
python3 scripts/build.py

# run verification
python3 scripts/check.py
```

## Verification results (all passing)

Ran `python3 scripts/build.py` and `python3 scripts/check.py`:

- `build.py` → wrote `site/handbook.html` (27,260 bytes), all 8 compiled sections present
- `check.py`:
  - required files: 19 checked — all present
  - HTML parse + tag balance: 6 pages, 8+14 internal links checked, 0 broken, 0 unbalanced
  - handbook compilation cross-check: all chapters compile into `handbook.html`
  - LICENSE contains the exact required copyright line
  - README credits Asdale Dynamics, LLC
  - footer credit "© 2026 Asdale Dynamics, LLC" present on every site page
  - secret/API-key scan over 18 text files: clean
- HTTP smoke test: all 7 site files served with status 200 from a local preview server
- No runtime dependencies: Python 3 standard library only

## Known gaps

- `handbook.html` is generated and must be rebuilt after editing `docs/` (`check.py` flags stale builds).
- Site pages are hand-authored HTML; if you edit a chapter in `docs/`, the corresponding chapter page under `site/` must be edited by hand (only `handbook.html` auto-syncs).
- The Markdown converter in `build.py` intentionally covers only the constructs used in this book (headings, lists, bold/italic/code, blockquotes, fenced blocks, links) — it is not a general-purpose renderer.
- Samples use invented names/figures (fictional club); no real persons or financial data included.
- No automated visual/browser testing; layout was verified by HTML parsing and serving checks, not screenshots.
- Not legal/parliamentary advice: groups requiring formal Robert's Rules procedures should layer this on top, not replace it.
