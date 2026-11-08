# Run a Good Meeting

A plain-English manual for running small-business and club meetings, written by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — AI education explained like a friend would: warm, step by step, never condescending.

**What's inside:**

- **Agendas that fit on a card** — three sections, five fields, a parking lot. One index card, zero homework.
- **Minutes people actually read** — minutes are a receipt, not a transcript: decisions, action items, tabled items, done.
- **Keeping the meeting on track (kindly)** — seven common situations with word-for-word lines that redirect without embarrassing anyone, including the talkative person and the quiet one.
- **A gentle AI assist for recaps** — copy-paste prompts for readable recaps. Humans decide; AI tidies; privacy first.
- **Templates** — an agenda card, a minutes template, and filled-in samples for both (fictional "Purple Lens Photography Club").

## Who it's for

Anyone who runs meetings with roughly 5–15 people: a small business, a club, a co-op, a committee, a board. No special software needed — read it in about 20 minutes, or grab the templates tonight.

## Where everything lives

| Path | What it is |
|---|---|
| `docs/` | The handbook, chapter by chapter, in Markdown |
| `docs/templates/` | Copy-paste templates + filled-in samples |
| `site/` | Polished static HTML version (open `site/index.html`) |
| `site/handbook.html` | Every chapter and template on one printable page |
| `scripts/build.py` | Regenerates `site/handbook.html` from `docs/` |
| `scripts/check.py` | Verification: links, tag balance, license lines, secret scan |

## Run it

This is a static site — there's nothing to install.

```bash
# read the handbook as a website: open in your browser
site/index.html            # start here
site/handbook.html         # or the full single-page version

# regenerate site/handbook.html after editing docs/
python3 scripts/build.py

# run verification (links, HTML balance, license, secret scan)
python3 scripts/check.py
```

Optional local preview server with Python:

```bash
python3 -m http.server 8000 --directory site
# then visit http://localhost:8000
```

## Distinct from `meeting-notes-summarizer-cli`

That other project is a *tool* that summarizes notes. This one is a *manual*: it teaches meeting craft (agendas, minutes, facilitation) and leaves the summarizing to whatever tool you already use — including that one.

## License

MIT — free to use, copy, adapt, and republish. See [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC. This handbook is part of the plain-English guide family at [dylanasdale.github.io](https://dylanasdale.github.io). Not legal, financial, or medical advice.
