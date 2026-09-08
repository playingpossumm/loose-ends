"""Render the vault as a single HTML document, for reading in Google Docs.

WHY THIS EXISTS
---------------
The vault is ninety markdown files. Reading it needs either a text editor, Claude Code, or a
markdown app — and the whole point of asking for a Google Doc is not installing a markdown
app. Google Docs converts uploaded HTML into a native document, and its outline pane (the
left sidebar, View > Show outline) turns the heading structure into persistent navigation.
So the heading hierarchy here is the interface: h1 for the document, h2 per subject, h3 per
page.

WHAT GOES IN, AND WHAT DOES NOT
-------------------------------
Knowledge first, because that is the half you cannot currently see. Each subject leads with
its concept page — the synthesis — and the sources that feed it sit under it with their
summaries. Entities follow. Open loops are an appendix rather than the body: they already
arrive by email twice a day, and putting them first would reproduce in a document the exact
imbalance this is meant to correct.

Raw captures are excluded. They are the input, not the knowledge.

This is a read-only view. Editing the doc changes nothing in the vault; the vault is the
source of truth and regenerating overwrites the doc.

    python scripts/build_doc.py                  # write the html next to the vault
    python scripts/build_doc.py --out PATH.html
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import (  # noqa: E402
    MIN_SUBJECT, VAULT, Page, humanise, load, plural,
)

DASH = chr(8212)


def md_to_html(text: str) -> str:
    """Enough markdown for the page bodies: bold, italic, code, links, lists, paragraphs.

    A full markdown library is available, but the vault's page bodies also carry vault paths
    in backticks and citation lines that mean nothing in a document. Those are stripped here
    rather than rendered, so the reader sees the claim and not the filing system.
    """
    # Drop the frontmatter.
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    # Drop the h1; the caller supplies its own heading.
    text = re.sub(r"\A\s*#\s+.*\n", "", text)

    out: list[str] = []
    para: list[str] = []          # accumulates a hard-wrapped paragraph
    item: list[str] = []          # accumulates a hard-wrapped list item
    in_list = False

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def flush_item() -> None:
        if item:
            out.append(f"<li>{inline(' '.join(item))}</li>")
            item.clear()

    def close_list() -> None:
        nonlocal in_list
        flush_item()
        if in_list:
            out.append("</ul>")
            in_list = False

    for raw in text.splitlines():
        line = raw.rstrip()

        # A blank line is the only thing that ends a paragraph. The vault is hard-wrapped at
        # 90 characters, so treating every newline as a break splits sentences mid-clause —
        # the same fault the brief email had before nl2br was removed.
        if not line.strip():
            flush_para()
            close_list()
            continue

        if line.startswith("#"):
            flush_para()
            close_list()
            depth = len(line) - len(line.lstrip("#"))
            tag = f"h{min(depth + 2, 6)}"        # page ## becomes h4, under the h3 title
            out.append(f"<{tag}>{inline(line.lstrip('# '))}</{tag}>")
            continue

        if line.lstrip().startswith(("- ", "* ")):
            flush_para()
            flush_item()
            if not in_list:
                out.append("<ul>")
                in_list = True
            item.append(line.lstrip()[2:])
            continue

        if in_list and raw.startswith(("  ", "\t")):
            item.append(line.strip())            # continuation of the current bullet
            continue

        if line.startswith("|") or line.startswith(">"):
            line = line.strip("|> ").replace("|", " " + DASH + " ")
            if set(line) <= set("- "):
                continue

        close_list()
        para.append(line)

    flush_para()
    close_list()
    return "\n".join(out)


CODE_PATH = re.compile(r"`([a-z]+/[^`]*?\.md)`")
BARE_ID = re.compile(r"`(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)`")
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# slug -> human title, filled in by build(). A citation is the point of this vault, so a
# path is resolved to the name of what it cites rather than deleted: deleting it leaves
# sentences like "the goal is recorded in §2" with nothing in front of the section number.
TITLES: dict[str, str] = {}


def name_for(path_or_id: str) -> str:
    stem = path_or_id.rsplit("/", 1)[-1].removesuffix(".md")
    if stem in TITLES:
        return TITLES[stem]
    # mem/goals.md and the like have no page object; use the filename.
    return stem.replace("-", " ")


def inline(s: str) -> str:
    s = CODE_PATH.sub(lambda m: name_for(m.group(1)), s)
    s = BARE_ID.sub(lambda m: name_for(m.group(1)), s)
    s = html.escape(s)
    s = MD_LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>'
                    if m.group(2).startswith("http") else m.group(1), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\s{2,}", " ", s).strip()


CSS = """
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; }
h1 { font-size: 22pt; }
h2 { font-size: 16pt; margin-top: 28pt; }
h3 { font-size: 12pt; margin-top: 16pt; margin-bottom: 2pt; }
h4 { font-size: 11pt; font-style: italic; margin-top: 12pt; margin-bottom: 2pt; }
.meta { color: #666; font-size: 9pt; }
.summary { color: #333; margin-top: 0; }
code { font-family: Consolas, monospace; font-size: 10pt; }
"""


def build() -> str:
    sources = load("wiki/sources/*.md")
    concepts = {p.category: p for p in load("wiki/concepts/*.md")}
    entities = load("wiki/entities/*.md")
    open_loops = [p for p in load("loops/open/*.md") if p.status == "open"]
    dates = load("loops/dates/*.md")

    for p in sources + list(concepts.values()) + entities + open_loops + dates:
        TITLES[p.slug] = p.title

    by_cat: dict[str, list[Page]] = {}
    for s in sources:
        by_cat.setdefault(s.category, []).append(s)
    ranked = sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    major = [(c, i) for c, i in ranked if len(i) >= MIN_SUBJECT]
    minor = [(c, i) for c, i in ranked if len(i) < MIN_SUBJECT]

    H = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>",
         "<h1>What the vault knows</h1>",
         f"<p class='meta'>Generated from the loose-ends vault on {date.today().isoformat()}. "
         f"{plural(len(sources), 'source')}, {plural(len(concepts), 'concept')}, "
         f"{len(entities)} {'entity' if len(entities) == 1 else 'entities'}. "
         f"This is a read-only view {DASH} editing it changes nothing in the vault, and "
         f"regenerating replaces it. Use View &gt; Show outline for navigation.</p>"]

    for cat, items in major:
        H.append(f"<h2>{humanise(cat)}</h2>")
        if cat in concepts:
            c = concepts[cat]
            H.append(f"<p class='meta'>Synthesis of {plural(len(items), 'source')}.</p>")
            H.append(md_to_html(c.text))
            H.append("<h3>Sources</h3>")
        # Sources are paragraphs, not headings. Google Docs builds its outline pane from
        # headings, and eighty-seven of them makes the pane as unnavigable as the flat list
        # this document replaced. Only subjects, concepts and entities earn a heading.
        for s in sorted(items, key=lambda p: p.slug):
            H.append(f"<p><b>{html.escape(s.title)}</b>"
                     + (f" {DASH} {inline(s.summary)}" if s.summary else "") + "</p>")

    if minor:
        H.append("<h2>Other subjects</h2>")
        H.append(f"<p class='meta'>Fewer than {MIN_SUBJECT} sources each, so nothing has "
                 f"been synthesised yet.</p>")
        for cat, items in minor:
            for s in sorted(items, key=lambda p: p.slug):
                H.append(f"<p><b>{html.escape(s.title)}</b> <i>({humanise(cat)})</i>"
                         + (f" {DASH} {inline(s.summary)}" if s.summary else "") + "</p>")

    if entities:
        H.append("<h2>People and projects</h2>")
        for e in entities:
            H.append(f"<h3>{html.escape(e.title)}</h3>")
            H.append(md_to_html(e.text))

    H.append("<h2>Appendix: what is open</h2>")
    H.append("<p class='meta'>These arrive by email; they are here for completeness.</p>")
    for p in sorted(open_loops + dates, key=lambda x: (x.due or "9999", x.slug)):
        bits = [f"<b>{html.escape(p.title)}</b>"]
        if p.due:
            bits.append(f"{DASH} due {p.due}")
        if p.summary:
            bits.append(f"{DASH} {inline(p.summary)}")
        H.append("<p>" + " ".join(bits) + "</p>")

    H.append("</body></html>")
    return "\n".join(H)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(VAULT.parent / "vault-doc.html"))
    args = ap.parse_args()
    text = build()
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"Wrote {args.out} ({len(text):,} characters)")


if __name__ == "__main__":
    main()
