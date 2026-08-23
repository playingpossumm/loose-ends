# second-brain

**Status: built and empty.** Vault, schema, and all seven skills are in place; no sources
compiled yet. **Start here: [the walkthrough](https://claude.ai/code/artifact/e811ca29-719a-46f9-a4c8-d72ca392bdba)**
or [`docs/setup.md`](docs/setup.md). Design rationale in
[`docs/decisions.md`](docs/decisions.md); the 90 questions behind it in
[`docs/architecture-qa.md`](docs/architecture-qa.md).

A personal knowledge base that does two things:

1. Answers **what do I know about X**, with citations back to the thing you actually read.
2. Notices **what did I say I'd do that I haven't** — and tells you, every week.

Six well-known write-ups of this idea were used as benchmarks. All six build the first
thing. None of them builds the second. The second is the point.

---

## The core object is a loop

The two motivating cases are not knowledge queries:

> *"I said I wanted to learn this, shared a PDF, and never read it."*
> *"A friend's birthday went in, and nothing ever made it a calendar event."*

Both are **open loops** — something stated that never resolved. So the primary object is
not a wiki page. It is a loop: an intent, commitment, or dated fact extracted from material
you captured for some other reason, carrying a status, tracked until it closes.

The wiki is the substrate. **The weekly brief is the product.**

### Why this is not a task manager

You never enter a task. Nothing here has an "add item" button. The system infers loops from
things you captured for other reasons, and you react to them once a week. The moment it
requires deliberate task entry, it has become the thing this project explicitly excludes.

---

## Architecture

```
capture ──► raw/ ──► compile ──► wiki/  ──► query   "what do I know about X"
                          └────► loops/ ──► brief   "what did I say I'd do"
```

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
  demote to someday

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
| WhatsApp | Deferred — see below. |
| Task entry | See above. |

**WhatsApp** is deferred, not cancelled. As capture inbox and query surface it needs
OpenClaw running 24/7, which means a VPS or similar (~$5/mo of infrastructure, not API
cost). Nothing in the design changes when it arrives: the brain exposes an MCP server and
OpenClaw becomes one client among several. Build the thing first, confirm it gets used,
then buy the always-on layer once it is earned.

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
| 10 | WhatsApp, BM25/vector | deferred by decision |

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
| `/unsource` | remove a source and revert its influence |

They live in [`.claude/skills/`](.claude/skills/) and load when Claude Code opens this
folder. No installation, no third-party dependencies.
