"""Create an empty vault.

The repository holds the system — skills, server, scripts, docs — and is public. Your
content lives in `vault/`, which the repository ignores. Run this once after cloning, then
make `vault/` its own private git repo so your notes get history and a backup:

    python scripts/init_vault.py
    cd vault && git init && git add -A && git commit -m "empty vault"
    gh repo create my-brain --private --source=. --push

Safe to re-run — it never overwrites anything that already exists.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault"))

DIRS = [
    "raw/inbox", "raw/articles", "raw/pdfs", "raw/images", "raw/transcripts", "raw/notes",
    "wiki/sources", "wiki/entities", "wiki/concepts", "wiki/synthesis",
    "loops/open", "loops/closed", "loops/dates",
    "mem", "briefs",
]

MEM = {
    "profile": "who you are, what you do, how you work, how you want to be talked to",
    "goals": "what you are trying to achieve, why it matters, what done looks like",
    "projects": "what is active — current state, next action, blocker, deadline",
    "people": "who materially affects your work, and only what you choose to store",
    "rules": "decision rules, standards, and what must never happen without asking",
}

INDEX = """# index

Catalogue of every page in `wiki/` and `loops/`. Read this first when answering a question,
then drill into the pages it points at. `/ingest` updates it on every compile; `/lint`
checks it for drift.

One line per page: link, one-sentence summary, source count.

---

## Sources

*(none yet)*

## Entities

*(none yet)*

## Concepts

*(none yet)*

## Synthesis

*(none yet)*

## Open loops

*(none yet)*

## Dates

*(none yet)*
"""

LOG = """# log

Append-only, chronological. Every ingest, query filed, lint pass, brief, and unsource lands
here. Newest at the bottom.

Entries keep this prefix exactly so the log stays greppable:

```
## [YYYY-MM-DD] <op> | <title>
```

`grep "^## \\[" log.md | tail -5` gives the last five operations.

---

## [{today}] init | vault created

Empty. Nothing compiled yet. Run /bootstrap to fill mem/, then /capture and /ingest.
"""


def main() -> None:
    made, skipped = [], []
    today = date.today().isoformat()

    for d in DIRS:
        p = VAULT / d
        if p.is_dir():
            skipped.append(d)
        else:
            p.mkdir(parents=True)
            (p / ".gitkeep").touch()
            made.append(d)

    for name, hint in MEM.items():
        p = VAULT / "mem" / f"{name}.md"
        if p.exists():
            skipped.append(f"mem/{name}.md")
            continue
        p.write_text(
            f"---\ntype: mem\nfolder: mem\ncreated: {today}\nupdated: {today}\n"
            f"status: empty\n---\n\n# {name}\n\n"
            f"_{hint}_\n\n"
            "Not yet filled. Run /bootstrap to populate this through an interview.\n\n"
            "This file is human-authoritative. The compiler may propose changes to it and\n"
            "must never write it unasked.\n",
            encoding="utf-8",
        )
        made.append(f"mem/{name}.md")

    for name, body in (("index.md", INDEX), ("log.md", LOG.format(today=today))):
        p = VAULT / name
        if p.exists():
            skipped.append(name)
        else:
            p.write_text(body, encoding="utf-8")
            made.append(name)

    print(f"Vault: {VAULT}")
    print(f"  created {len(made)} item(s)" + (f", {len(skipped)} already existed" if skipped else ""))
    if made:
        print("\nNext:")
        print("  1. cd vault && git init && git add -A && git commit -m 'empty vault'")
        print("     then push it to a PRIVATE repo — this is your notes, not the system")
        print("  2. Open Claude Code in the repository root and run /bootstrap")
    else:
        print("\nNothing to do — vault already set up.")


if __name__ == "__main__":
    if not ROOT.joinpath("CLAUDE.md").is_file():
        sys.exit(f"Run this from the loose-ends repo. Expected CLAUDE.md at {ROOT}")
    main()
