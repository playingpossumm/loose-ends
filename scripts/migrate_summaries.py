"""One-time: move the one-line summaries out of index.md and onto the pages they describe.

index.md was hand-maintained, which is why /lint had to check it for drift. The summaries in
it are good — better than anything a script would write — but they lived nowhere else, so
the index could not be regenerated without losing them.

This reads each `- [slug](path) — summary (N sources)` line and writes the summary into that
page's frontmatter as `summary:`. After it runs, scripts/index.py can rebuild index.md from
the vault at any time and the summaries survive.

Idempotent: a page that already has `summary:` is left alone.

    python scripts/migrate_summaries.py --dry-run
    python scripts/migrate_summaries.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()

DASH = chr(8212)
# - [slug](relative/path.md) — the summary text (N sources)
LINE = re.compile(r"^-\s+\[[^\]]*\]\(([^)]+\.md)\)\s*" + DASH + r"\s*(.+?)\s*$")
TRAILING_COUNT = re.compile(r"\s*\(\d+\s+sources?\)\s*$")


def summaries() -> dict[Path, str]:
    index = VAULT / "index.md"
    if not index.is_file():
        sys.exit("No index.md to migrate from.")
    out: dict[Path, str] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        m = LINE.match(line.strip())
        if not m:
            continue
        target = (VAULT / m.group(1)).resolve()
        text = TRAILING_COUNT.sub("", m.group(2)).strip()
        if target.is_file() and text:
            out[target] = text
    return out


def insert(text: str, summary: str) -> str | None:
    """Put `summary:` immediately after `type:`. Returns None if one is already there."""
    if re.search(r"^summary:", text, re.M):
        return None
    m = re.search(r"^type:\s*\S+\s*$", text, re.M)
    if not m:
        return None
    # Quote it: these summaries contain colons, which would break the YAML otherwise.
    value = summary.replace('"', "'")
    return text[:m.end()] + f'\nsummary: "{value}"' + text[m.end():]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    args = ap.parse_args()

    found = summaries()
    written = skipped = 0
    for path, text in sorted(found.items()):
        body = path.read_text(encoding="utf-8")
        updated = insert(body, text)
        if updated is None:
            skipped += 1
            continue
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")
        written += 1
        if args.dry_run:
            print(f"  {path.relative_to(VAULT).as_posix()}\n      {text[:100]}")

    verb = "would write" if args.dry_run else "wrote"
    print(f"\n{len(found)} index entries resolved to real files. "
          f"{verb} {written}, skipped {skipped} that already had one.")

    missing = [p for p in VAULT.glob("wiki/sources/*.md") if p not in found]
    if missing:
        print(f"\n{len(missing)} source pages had no index entry and so have no summary:")
        for p in missing[:10]:
            print(f"  {p.name}")


if __name__ == "__main__":
    main()
