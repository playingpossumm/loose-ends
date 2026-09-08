"""Report the synthesis pages the vault should have and does not.

THE PROBLEM THIS EXISTS FOR
---------------------------
On 2026-09-07 the vault held 57 source pages, 1 entity page and 1 concept page. The source
pages were good — real claims, properly attributed. Nothing connected them. Asking "what do
I know about GMAP SEA" meant re-reading 28 pages and learning nothing that persisted.

`/ingest` is instructed to promote a mention to its own page at three independent sources,
and that rule had never once fired. It cannot: `/ingest` compiles one source at a time and
has no way to see the mention counts in the other 56. The rule was correct and unreachable.

So the counting happens here, deterministically, over files that already exist:

  entities   names the vault already knows from mem/people.md and mem/projects.md, counted
             across wiki/sources/. No proper-noun extraction, no guessing — if a name
             matters enough to be in mem/, it is a candidate.

  concepts   the `category:` field the compiler already writes on every source. A category
             carrying three or more sources is a subject the vault has accumulated real
             knowledge about, and it is labelled as such at compile time by the thing that
             read the material.

Reporting only. This writes nothing to the vault; /ingest and /lint act on the output.

    python scripts/synthesis.py            # human-readable gaps
    python scripts/synthesis.py --brief    # one line, or nothing, for the brief prompt
    python scripts/synthesis.py --json     # for a skill to consume
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()

# Three independent sources. Below that a "pattern" is usually one thing mentioned twice,
# and a page built from it says less than the two sources it came from.
THRESHOLD = 3

# Headings in mem/ that introduce a name rather than a topic. `## Kyara` is an entity;
# `## Unanswered` is a section of the file about its own bookkeeping.
NOT_A_NAME = {
    "unanswered", "scope", "open questions", "notes", "rules", "sequencing",
    "key friends", "background", "status", "summary", "overview", "index",
}

# A heading in mem/ is a name only if it reads like one. These reject the two things that
# otherwise slip through: a heading that is really a date ("September 2026", which matched
# seven sources and means nothing as a page), and a heading that is really a sentence.
MONTHS = ("january february march april may june july august september october november "
          "december").split()
MAX_NAME_WORDS = 4


def looks_like_a_name(text: str) -> bool:
    words = text.split()
    if not words or len(words) > MAX_NAME_WORDS:
        return False
    if text.lower() in NOT_A_NAME:
        return False
    # "September 2026", "6 September" — a date, not a subject.
    if any(w.lower().strip(",") in MONTHS for w in words) and any(
            w.strip(",").isdigit() for w in words):
        return False
    return not text.lower().startswith(("a ", "an ", "how ", "what ", "why ", "when "))


def slug(text: str) -> str:
    """Match the naming already used: 'Kyara' -> kyara, 'Personal Website' -> personal-website."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def known_names() -> list[str]:
    """Names the vault has already committed to caring about, from mem/."""
    names = []
    for f in ("people.md", "projects.md"):
        p = VAULT / "mem" / f
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^#{2,3}\s+(?:\d+\.\s*)?(.+?)\s*$", line)
            if not m:
                continue
            # Headings carry trailing commentary after a dash: "RAG — the retrieval project".
            name = re.split(r"\s+[–—-]\s+", m.group(1))[0].strip(" *_`")
            name = re.sub(r"^[Tt]he\s+", "", name)   # "The portfolio" is the portfolio
            if len(name) > 2 and looks_like_a_name(name):
                names.append(name)
    return sorted(set(names))


def sources() -> list[tuple[str, str]]:
    d = VAULT / "wiki" / "sources"
    if not d.is_dir():
        return []
    return [(p.stem, p.read_text(encoding="utf-8", errors="replace")) for p in sorted(d.glob("*.md"))]


def existing(kind: str) -> set[str]:
    d = VAULT / "wiki" / kind
    return {p.stem for p in d.glob("*.md")} if d.is_dir() else set()


def entity_gaps(srcs: list[tuple[str, str]]) -> list[dict]:
    """Names mentioned in THRESHOLD or more sources with no page of their own."""
    have = existing("entities")
    out = []
    for name in known_names():
        # Word-boundary match without a regex escape that has to survive a shell: compare
        # against a lowercased copy and check the characters either side are not letters.
        hits = [sid for sid, text in srcs if _mentions(text, name)]
        if len(hits) >= THRESHOLD and slug(name) not in have:
            out.append({"name": name, "count": len(hits), "slug": slug(name),
                        "sources": hits[:6]})
    return sorted(out, key=lambda e: -e["count"])


def _mentions(text: str, name: str) -> bool:
    lo, target = text.lower(), name.lower()
    start = 0
    while True:
        i = lo.find(target, start)
        if i == -1:
            return False
        before = lo[i - 1] if i else " "
        after = lo[i + len(target)] if i + len(target) < len(lo) else " "
        if not before.isalnum() and not after.isalnum():
            return True
        start = i + 1


def concept_gaps(srcs: list[tuple[str, str]]) -> list[dict]:
    """Categories carrying THRESHOLD or more sources with no concept page."""
    have = existing("concepts")
    counts: dict[str, list[str]] = {}
    for sid, text in srcs:
        m = re.search(r"^category:\s*(.+?)\s*$", text, re.M)
        if not m:
            continue
        cat = m.group(1).strip()
        if cat.lower() in ("unknown", "none", ""):
            continue
        counts.setdefault(cat, []).append(sid)
    return sorted(
        ({"name": c, "count": len(ids), "slug": slug(c), "sources": ids[:6]}
         for c, ids in counts.items() if len(ids) >= THRESHOLD and slug(c) not in have),
        key=lambda e: -e["count"],
    )


def report() -> dict:
    srcs = sources()
    return {
        "sources": len(srcs),
        "entities": len(existing("entities")),
        "concepts": len(existing("concepts")),
        "entity_gaps": entity_gaps(srcs),
        "concept_gaps": concept_gaps(srcs),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true", help="machine-readable, for a skill")
    g.add_argument("--brief", action="store_true",
                   help="one line for the brief prompt, or nothing when there are no gaps")
    args = ap.parse_args()

    r = report()
    gaps = r["entity_gaps"] + r["concept_gaps"]

    if args.json:
        print(json.dumps(r, indent=2))
        return

    if args.brief:
        if not gaps:
            return
        top = ", ".join(f"{g['name']} ({g['count']} sources)" for g in gaps[:3])
        print(f"{len(gaps)} subjects have reached {THRESHOLD} sources with no page of their "
              f"own: {top}.")
        return

    print(f"{r['sources']} sources, {r['entities']} entity pages, {r['concepts']} concept pages.\n")
    if not gaps:
        print(f"No subject has reached {THRESHOLD} sources without a page. Nothing to promote.")
        return

    for label, items, folder in (("Entities", r["entity_gaps"], "wiki/entities"),
                                 ("Concepts", r["concept_gaps"], "wiki/concepts")):
        if not items:
            continue
        print(f"{label} to promote ({folder}/):")
        for e in items:
            print(f"  {e['count']:3}  {e['name']}  ->  {e['slug']}.md")
            print(f"       {', '.join(e['sources'][:3])}"
                  + (f", +{e['count'] - 3} more" if e["count"] > 3 else ""))
        print()
    print("Run /ingest-all, or /lint, to write these.")


if __name__ == "__main__":
    main()
