"""second-brain MCP server.

Exposes the vault to any agent, in any project, on this machine. Data access only —
searching, reading, capturing. Synthesis is the calling agent's job, which is what keeps
this useful to Claude Code, a CLI, or anything else that speaks MCP.

Vault location comes from BRAIN_VAULT, or defaults to this file's parent directory.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

from mcp.server import MCPServer

VAULT = Path(os.environ.get("BRAIN_VAULT", Path(__file__).resolve().parent.parent / "vault")).resolve()

# Searched in priority order. raw/ is last: the wiki is compiled understanding, raw is
# ground truth you fall back to.
SEARCH_DIRS = ("wiki", "loops", "mem", "briefs", "raw")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".claude"}

server = MCPServer(
    name="second-brain",
    version="1.0.0",
    instructions=(
        "Personal knowledge vault. Call brain_index first to see what exists, then "
        "brain_search to find pages and brain_read to read them. Cite every claim by its "
        "page path. Always tell the user what the vault does NOT cover — that coverage "
        "note is part of a correct answer here. Use brain_capture to file something new; "
        "it does not compile, it only files."
    ),
)


def _safe(rel: str) -> Path:
    """Resolve a vault-relative path, refusing anything that escapes the vault."""
    p = (VAULT / rel.strip().lstrip("/\\")).resolve()
    if p != VAULT and VAULT not in p.parents:
        raise ValueError(f"path escapes the vault: {rel}")
    return p


def _pages() -> list[Path]:
    out: list[Path] = []
    for d in SEARCH_DIRS:
        root = VAULT / d
        if not root.is_dir():
            continue
        for p in root.rglob("*.md"):
            if not any(part in SKIP_DIRS for part in p.parts):
                out.append(p)
    return out


def _rel(p: Path) -> str:
    return p.relative_to(VAULT).as_posix()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:48] or "note").rstrip("-")


@server.tool()
def brain_index() -> str:
    """The catalogue of everything in the vault. Read this first — it is the map."""
    idx = VAULT / "index.md"
    if not idx.is_file():
        return "No index.md. The vault may not be initialised."
    counts = {d: len(list((VAULT / d).rglob("*.md"))) for d in SEARCH_DIRS if (VAULT / d).is_dir()}
    tally = ", ".join(f"{k}: {v}" for k, v in counts.items())
    return f"{idx.read_text(encoding='utf-8')}\n\n---\nPage counts — {tally}"


@server.tool()
def brain_search(query: str, limit: int = 15) -> str:
    """Search the vault for pages matching a query.

    Returns ranked paths with matching lines. Read the promising ones with brain_read
    before answering — snippets alone are not enough to cite from.
    """
    terms = [t for t in re.split(r"\s+", query.lower().strip()) if len(t) > 1]
    if not terms:
        return "Empty query."

    hits = []
    for p in _pages():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        low = text.lower()
        if not any(t in low or t in p.name.lower() for t in terms):
            continue

        # A hit in the filename means the page is probably *about* the term.
        score = sum(low.count(t) for t in terms) + 12 * sum(t in p.name.lower() for t in terms)
        lines = [
            f"    {i}: {ln.strip()[:160]}"
            for i, ln in enumerate(text.splitlines(), 1)
            if any(t in ln.lower() for t in terms)
        ][:3]
        hits.append((score, _rel(p), lines))

    if not hits:
        return f"No matches for {query!r}. The vault does not cover this yet."

    hits.sort(key=lambda h: -h[0])
    out = [f"{len(hits)} match(es) for {query!r}" + (f", showing {limit}" if len(hits) > limit else "")]
    for _, rel, lines in hits[:limit]:
        out.append(f"\n  {rel}")
        out.extend(lines)
    return "\n".join(out)


@server.tool()
def brain_read(path: str) -> str:
    """Read one page in full. Path is vault-relative, e.g. wiki/concepts/retrieval.md"""
    try:
        p = _safe(path)
    except ValueError as e:
        return f"Refused: {e}"
    if not p.is_file():
        return f"Not found: {path}"
    if p.suffix.lower() != ".md":
        return f"Not a markdown page: {path}"
    return f"# {_rel(p)}\n\n{p.read_text(encoding='utf-8', errors='replace')}"


@server.tool()
def brain_loops(status: str = "open") -> str:
    """List tracked loops — things the user said they would do.

    status: open, closed, dates, or all. Use this when asked what is outstanding, or
    before suggesting new work.
    """
    folders = ["open", "closed", "dates"] if status == "all" else [status]
    out = []
    for f in folders:
        d = VAULT / "loops" / f
        if not d.is_dir():
            continue
        pages = sorted(d.glob("*.md"))
        if not pages:
            continue
        out.append(f"\n## loops/{f} ({len(pages)})")
        for p in pages:
            text = p.read_text(encoding="utf-8", errors="replace")
            meta = {
                k: v.strip()
                for k, v in re.findall(r"^(status|surfaced|due):\s*(.+)$", text, re.M)
            }
            body = next(
                (ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith(("-", "#"))),
                "",
            )
            bits = " ".join(f"{k}={v}" for k, v in meta.items())
            out.append(f"  {_rel(p)}  {bits}\n    {body[:140]}")
    return "\n".join(out) if out else f"No loops with status {status!r}."


@server.tool()
def brain_capture(content: str, title: str, kind: str = "note", origin: str = "mcp") -> str:
    """File something into the vault inbox. Does NOT compile it — /ingest does that.

    Use when the user says something worth keeping, or asks to save something. Store their
    wording verbatim; capture is a photocopier, not an editor.

    kind: note, article, pdf, image, transcript
    """
    inbox = VAULT / "raw" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    ident = f"{today}-{_slug(title)}"
    path = inbox / f"{ident}.md"
    n = 2
    while path.exists():
        path = inbox / f"{ident}-{n}.md"
        n += 1

    path.write_text(
        "---\n"
        f"id: {path.stem}\n"
        f"captured: {today}\n"
        f"kind: {kind}\n"
        f"origin: {origin}\n"
        f"title: {title}\n"
        "status: uncompiled\n"
        "---\n\n"
        f"{content}\n",
        encoding="utf-8",
    )
    return f"Filed {_rel(path)} — uncompiled. Run /ingest in the vault to compile it."


@server.tool()
def brain_recent(count: int = 10) -> str:
    """The last N things that happened in the vault — ingests, briefs, lints, closures."""
    log = VAULT / "log.md"
    if not log.is_file():
        return "No log.md yet."
    # Real entries only — log.md documents its own format with a YYYY-MM-DD placeholder.
    entries = re.findall(r"^## \[\d{4}-\d{2}-\d{2}\].*$", log.read_text(encoding="utf-8"), re.M)
    return "\n".join(entries[-count:]) if entries else "Log is empty — nothing compiled yet."


if __name__ == "__main__":
    if not VAULT.is_dir():
        raise SystemExit(f"Vault not found: {VAULT}. Set BRAIN_VAULT.")
    server.run()
