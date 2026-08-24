# second-brain

**Status: built and empty.** Vault, schema, and all eight skills are in place; no sources
compiled yet. **Start here: [the walkthrough](https://claude.ai/code/artifact/e811ca29-719a-46f9-a4c8-d72ca392bdba)**
or [`docs/setup.md`](docs/setup.md). Design rationale in
[`docs/decisions.md`](docs/decisions.md); the 90 questions behind it in
[`docs/architecture-qa.md`](docs/architecture-qa.md).

A persistent personal memory layer. Not an app — a folder of markdown files that any agent
can read, holding everything you have read and everything about how you work.

It has to do four things, and all four are the offering. Drop any one and the rest stop
being worth the effort:

| | |
|---|---|
| **One memory you can interrogate** | Everything you have read and everything about how you work — notes, LLM transcripts, Twitter saves, PDFs, your goals and projects — consolidated into one place that answers with citations. |
| **Reachable from anywhere** | Not locked inside one folder or one tool. Any agent, any project, eventually any device. |
| **It compounds** | Connections form between things read months apart. It gets better with every source rather than merely larger. |
| **It closes loops** | It notices what you said you would do and didn't, pushes you until you decide — and hands you the thing already half-done. |

The last one is the differentiator. Every system in this category *stores*; this one is
built to make you *act*. See below.

Six well-known write-ups of this idea were used as benchmarks — Karpathy's llm-wiki, Garry
Tan's GBrain, and four others. How this differs, and where they are better, is in
[`docs/comparison.md`](docs/comparison.md).

---

## Reach is a design constraint, not a feature

"Reachable from anywhere" is the pillar that shapes the architecture, because it is the one
that fails silently if you design for it late.

A vault that only works when Claude Code is open in its own folder is not a memory layer —
it is a folder. So the vault is exposed through an **MCP server**, and every surface is a
client of it: Claude Code in *any* project, the CLI, later a phone.

Two kinds of reach, with very different costs:

| Reach | Needs | Cost | Status |
|---|---|---|---|
| Any agent, any project, on this laptop | an MCP server, running locally on demand | free | **built** |
| Your phone, away from the laptop | an always-on host running OpenClaw | ~$5/mo | deferred |

Most of the value is in the first row, and it was originally scheduled last. It was moved
up and is now done — [`mcp/server.py`](mcp/server.py) exposes six tools (`brain_index`,
`brain_search`, `brain_read`, `brain_loops`, `brain_capture`, `brain_recent`) over stdio.
Registration is one command, in [`docs/setup.md`](docs/setup.md).

The write surface is deliberately tiny: `brain_capture` appends a file to `raw/inbox/` and
that is all. Nothing reachable over MCP can edit or delete a page — compilation stays inside
the vault where you can watch it happen. Paths resolve against the vault root, so traversal
is refused rather than served.

WhatsApp stays deferred, but it now covers only the phone case rather than the whole of
reach.

## Closing loops

The system tracks **open loops** — things stated that never resolved:

> *"I said I wanted to learn this, filed the PDF, and never read it."*
> *"A friend's birthday went in, and nothing ever made it a calendar event."*
> *"I told them I'd send the thing, and never did."*

A loop is a file with a status, a counter of how often it has been surfaced unacknowledged,
and provenance back to the source that produced it. It returns weekly until you kill it,
schedule it, or demote it to someday.

**The part that matters is what comes with the nudge.** A reminder you have already ignored
three times does not need a fourth reminder; it needs the friction removed. So the brief
does not stop at telling you a loop is open — it arrives with the work already started:

| Loop | What arrives with the nudge |
|---|---|
| You owe someone an email | a **drafted email**, in your voice, with the context from the vault already in it |
| A birthday or deadline | the event details ready to paste, and the fact that no event exists |
| A PDF you never read | a short summary, so you can decide whether you still care instead of re-opening it |
| A decision you never made | the options, with what the vault knows about each |

**Drafts only.** Nothing is ever sent, and nothing is written to a calendar. The system
produces the artifact and hands it to you; pressing send stays a human act. That boundary is
enforced by not holding credentials that could do otherwise, not by an instruction.

**This is not task management.** You never enter a task; nothing here has an "add item"
button. Loops are inferred from material you captured for other reasons. The moment it
requires deliberate task entry, it has become the thing this project explicitly excludes.

---

## Architecture

```
capture ──► raw/ ──► compile ──┬──► wiki/  ──► ask     "what do I know about X"
                               │
                               └──► loops/ ──► brief ──► close
                                             "you said   "here's the email.
                                              you'd..."   send it or kill it."
```

The bottom row is the part that distinguishes this. Everything else in the category stops
at the middle column.

Two knowledge stores, kept strictly apart — this is the load-bearing decision:

| | **World knowledge** (`wiki/`) | **Self knowledge** (`mem/`) |
|---|---|---|
| Author | the model | you |
| Size | unbounded | small |
| Contradictions are | *findings* — flag and keep both | *bugs* — surface and fix |
| Compiler may | write freely | propose only, never write |

Every source that conflates these gets muddled. `wiki/` is compiled and disposable —
it can be rebuilt from `raw/`. `mem/` is authoritative and cannot.

### Vault layout

```
brain/                    the vault. one folder, opened in Obsidian.
├─ CLAUDE.md              thin index → points at mem/
├─ index.md               catalogue of every wiki page
├─ log.md                 append-only record of what happened when
│
├─ raw/                   immutable. never edited after landing.
│  ├─ inbox/              the single landing zone — every capture door drops here
│  └─ articles/ pdfs/ images/ transcripts/ notes/
│
├─ wiki/                  sources/ entities/ concepts/ synthesis/
├─ loops/                 open/ closed/ dates/
├─ mem/                   profile.md goals.md projects.md people.md rules.md
└─ briefs/                one file per week
```

Markdown is the source of truth, git-versioned. Obsidian is a **viewer, not a dependency** —
nothing in the pipeline requires it running. Any index or cache is derived and rebuildable.

### Capture: one landing zone, many doors

Everything lands in `raw/inbox/`. The compiler watches exactly one folder, so capture
methods can be added forever without touching the pipeline.

| Door | For |
|---|---|
| Drag into `raw/inbox/` | anything on the laptop |
| Obsidian Web Clipper | Twitter saves, articles, PDFs |
| `/capture` in Claude Code | LLM transcripts, mid-session thoughts |

### The weekly brief

Run `/brief` weekly. It is designed to be **pushed** rather than fetched — a brief you have
to remember to open is a brief you stop reading — but the delivery channel is the one thing
still unwired; run it by hand until that is decided. Contents, capped at roughly ten lines:

- what compiled this week
- contradictions found between new sources and existing pages
- loops that went stale
- **decide-now**: loops surfaced 4 times without acknowledgement — kill, schedule, or
  demote to someday — each arriving **with the artifact that closes it**, written out in
  full: the drafted email, the event details, the summary. Drafts do not count against the
  ten-line cap; three lines of nudge and one good email draft is the brief working correctly.

Open loops return every week. The escalation exists because flat repetition trains you to
skim, which is failure condition #2 below.

Every answer and every brief ends with a **coverage note** — what the brain does *not* know
yet. Borrowed from GBrain; the best single idea in the six sources.

---

## Deliberately not here

| Not building | Why |
|---|---|
| Vector store, embeddings | No existing corpus; hobby-scale volume. `index.md` + grep wins on latency, cost, and debuggability until roughly 5,000 pages. Retrieval sits behind one interface so this is a swap, not a rewrite. |
| Graph database | Typed relations live in frontmatter. The database earns its keep at 100k pages, not hundreds. |
| Building on GBrain | Scale and shape mismatch — [`docs/gbrain-verdict.md`](docs/gbrain-verdict.md). |
| Reusing `rag-project` | Independent project by decision. |
| A compiled-vs-RAG benchmark | Interesting, but not what this is for. |
| 24/7 daemon | Weekly cadence needs no always-on process. |
| Calendar writes | The brief tells you to make the event. No OAuth write scope. |
| Phone / WhatsApp reach | Deferred — see below. |
| Task entry | See above. |

**Phone reach** is deferred, not cancelled — and it is the *only* part of reach that is.
Reaching the vault from any project or agent on this laptop is step 10 and costs nothing.
Reaching it from your phone needs OpenClaw running 24/7, which means a VPS or similar
(~$5/mo of infrastructure, not API cost). Nothing in the design changes when it arrives:
the MCP server already exists by then and OpenClaw becomes one more client. Build the
memory first, confirm it gets used, then buy the always-on layer once it is earned.

---

## Provenance and reversibility

Two properties none of the six benchmark sources implement, both required by the fact that
compilation is lossy and touches many pages at once:

- **Claim-level citation.** Every claim on a wiki page, and every loop, traces to a source
  page plus a locator. Including claims derived from images — a summary drawn from a
  screenshot must point back at that screenshot.
- **Decompilation.** Every page edit is tagged with the source that caused it, so
  `unsource X` is a real operation. One of the benchmark write-ups admits a bad source
  touches fifteen pages before you notice it, and offers no remedy. This is the remedy.

---

## Cost

Runs on the existing **Claude Code subscription** — roughly $0 marginal for compilation,
queries, and briefs at this cadence and volume. For reference, the API equivalent would run
about $15–40/month (Opus 5 at $5/$25 per MTok, ~100 sources/month), which is what the
subscription path avoids.

The only cost that grows with corpus size is the weekly maintenance sweep. It is
incremental by design — it touches pages changed since the last run, not the whole vault.

---

## Measurement

Deliberately light. The bar here is "is this useful", not "is this defensible".

- **Nudge precision** *(headline)* — of the loops surfaced each week, how many were worth
  surfacing. One click per item. This is the honest measure of whether the thing works.
- **Citation validity** *(automated guard)* — every claim resolves to a real source
  locator. Run on every compile.

## Failure conditions

Kill or rethink if any of these hold:

1. Nothing enters `raw/` for three consecutive weeks — capture friction is fatal no matter
   how good the compiler is.
2. Brief precision drops below ~30% — an ignored brief is worse than no brief.
3. You start maintaining the wiki by hand — the compiler has failed and you have rebuilt
   the filing cabinet.
4. Cost exceeds value.

---

## Build order

| # | Step | Status |
|---|---|---|
| 1 | Vault skeleton, frontmatter schema, git | **done** — [`CLAUDE.md`](CLAUDE.md) |
| 2 | Capture doors — `raw/inbox/`, Web Clipper, `/capture` | **done** — Clipper is a browser install, see setup |
| 3 | `mem/` bootstrap interview | **skill written** — needs you to run `/bootstrap` |
| 4 | Compile loop with claim-level citations | **done** — `/ingest` |
| 5 | Loop extraction and status tracking | **done** — inside `/ingest` |
| 6 | Weekly brief with the escalation rule | **done** — `/brief`; delivery channel open |
| 7 | Query with citations and coverage note | **done** — `/ask` |
| 8 | Lint — contradiction, staleness, link integrity | **done** — `/lint` |
| 9 | Decompilation | **done** — `/unsource` |
| **10** | **MCP server — the vault readable from any project or agent** | **next** — promoted; see reach above |
| 11 | Phone reach via OpenClaw, BM25/vector | deferred by decision |

Step 10 was originally last. It moved because "reachable from anywhere" turned out to be
part of the core offering rather than a later convenience, and without it the memory only
exists inside one folder.

Two things are not code and cannot be: the `/bootstrap` interview needs your answers, and
the brief's delivery channel needs one decision. Both in [`docs/setup.md`](docs/setup.md).

## Skills

| Command | Does |
|---|---|
| `/capture` | file something into `raw/inbox/` — fast, verbatim, no interpretation |
| `/ingest` | compile one source into `wiki/` + `loops/`, max 15 pages, plan shown first |
| `/bootstrap` | interview to fill `mem/`, one question at a time |
| `/brief` | the weekly brief, capped at ten lines |
| `/ask` | synthesised answer, citations, coverage note |
| `/lint` | citation validity, links, orphans, contradictions, staleness |
| `/close` | close one loop — produces the drafted email, summary, or next action |
| `/unsource` | remove a source and revert its influence |

They live in [`.claude/skills/`](.claude/skills/) and load when Claude Code opens this
folder. No installation, no third-party dependencies.
