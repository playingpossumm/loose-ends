# Decisions log

Answers to `architecture-qa.md`, round 1. Open items marked **OPEN**.

## Locked

| # | Decision |
|---|---|
| A1 | Personal database of things + information, **and acting on it**. Core examples: an intent stated but never followed through ("wanted to learn this, shared a PDF, never read it"), and a fact that implies an action ("friend's birthday → calendar event"). |
| A2 | Both daily-use and portfolio, but **does not need to be as defensible as `rag-project`**. Lowers the eval bar. |
| A3 | Broad scope, but **not a daily task manager**. |
| A4 | Single user, permanently. |
| B1 | Own notes, LLM transcripts, Twitter saves, PDFs. |
| B2 | **No existing corpus.** Volume unknown. Domain is side jobs and hobbies, with some main-job overlap. |
| B3 | Start empty, compile forward. |
| B4 | Images are first-class, **and must remain auditable** — a task or summary derived from an image must trace back to that image. |
| C5 | Voice notes: no. |
| D5 | Frontmatter looks fine; **add category and owning folder**. Details deferred. |
| E1 | **Weekly** cadence, not daily. |
| E3 | Idempotent, but a repeat encounter **implies the information is important** — treat re-ingest as a salience signal, not just a no-op. |
| E5 | Human writes wiki pages rarely. |
| F1 | Delegated. |
| H1 | **`rag-project` is not reused. This project is independent.** |
| I2 | Entity types: papers, tools, concepts, projects, people. |
| M2 | **No** compiled-vs-RAG benchmark. Not the point of this project. |

## Derived from the above

- **B2 + H1 settle section H.** No existing corpus, hobby-scale volume, no `rag-project` reuse
  → `index.md` + grep is sufficient for a long time. No embeddings, no vector store,
  no graph database in v1. Retrieval stays behind one interface so it can be swapped
  when (if) volume justifies it.
- **A2 + M2 settle section M.** Eval drops from a research harness to a lightweight
  operational check. See M1 candidates below.
- **A1 changes the core object model.** Neither A1 example is a knowledge query. Both are
  *open loops* — something stated that never resolved. See `loops/` below.

## The reframe

The central object is not a wiki page. It is a **loop**: an intent, commitment, or dated
fact extracted from captured material, carrying a status, tracked to closure.

```
raw/     immutable captures, content-hashed
wiki/    entities, concepts, sources — the substrate
loops/   intents, commitments, dates — the acting layer
mem/     profile, goals, projects, people, rules — self knowledge
```

The wiki is the substrate; **the weekly brief is the product.** All six benchmark sources
treat the wiki as the deliverable and the brief as a nice-to-have. For A1's use case that
is backwards.

**Why this is not the task manager A3 rules out:** you never enter a task. The system
*infers* loops from material captured for other reasons, and you react weekly. If it ever
requires deliberate task entry, it has become the thing A3 excluded.

## M1 — candidate claims (pick one headline)

| Claim | Measurable how | Cost to measure |
|---|---|---|
| **Nudge precision** — of loops surfaced, how many were worth surfacing | one click per item, weekly | ~nil |
| Loop recall — of intents actually expressed, how many were caught | hand-label one month of raw | moderate |
| Citation validity — every claim traces to a real source locator | fully automated | nil |
| Link integrity / orphan rate | fully automated | nil |

*Recommended: **nudge precision** as the headline, citation validity as an automated guard.*

## P3 — abandonment conditions

Kill or rethink if any of these hold:

1. Nothing enters `raw/` for three consecutive weeks — capture friction is fatal
   regardless of how good the compiler is.
2. Weekly brief precision drops below ~30% — an ignored brief is worse than no brief.
3. You start maintaining the wiki by hand — the compiler has failed and you have rebuilt
   the filing cabinet.
4. Cost exceeds the N1 ceiling without proportional value.

## GBrain — verdict: **no**

See `docs/gbrain-verdict.md`.

## Locked — round 2

| # | Decision |
|---|---|
| Scope | **Both** surfaces: "what do I know about X" (wiki query) *and* "what did I say I'd do" (loop nudging). Neither is subordinate. Synthesised answers with citations move into v1. |
| Cost | **Claude Code subscription**, not the API. ~$0 marginal for compilation and briefs. |
| Vault | One folder, subfolders inside. Tree below. |
| Brief | **Pushed** to the user, not left in a file to be found. |
| Nudges | Open loops **re-surface every week**. See escalation note below. |
| C1 | WhatsApp as **both** capture inbox and query surface. |
| L | **No confidentiality constraint** — all material is the user's own to keep. Simplifies section L considerably. |

## Vault layout

```
brain/                    ← the vault. one folder, opened in Obsidian.
├─ CLAUDE.md              ← thin index, points at mem/
├─ index.md               ← catalogue of every wiki page
├─ log.md                 ← append-only chronological record
│
├─ raw/                   ← immutable. never edited after landing.
│  ├─ inbox/              ← THE single landing zone. every capture door drops here.
│  ├─ articles/  pdfs/  images/  transcripts/  notes/
│
├─ wiki/                  ← LLM-owned. answers "what do I know about X"
│  ├─ sources/            ← one page per raw item
│  ├─ entities/           ← people, tools, papers, projects
│  ├─ concepts/
│  └─ synthesis/          ← filed answers to your own questions
│
├─ loops/                 ← the acting layer. answers "what did I say I'd do"
│  ├─ open/  closed/
│  └─ dates/              ← birthdays, deadlines, recurring
│
├─ mem/                   ← human-authoritative. compiler proposes, never writes.
│  └─ profile.md  goals.md  projects.md  people.md  rules.md
│
└─ briefs/                ← one file per week, archived
```

## Capture: one landing zone, many doors

Everything lands in `raw/inbox/`. The compiler watches one place; the number of ways
material gets there is unlimited and can grow without touching the pipeline.

| Door | For | Status |
|---|---|---|
| Drag-and-drop into `raw/inbox/` | anything on the laptop | works day one, zero setup |
| Obsidian Web Clipper | Twitter saves, articles | best value per minute of setup |
| `/capture` in Claude Code | LLM transcripts, mid-session thoughts | free, and nothing else builds this |
| OneDrive-synced `raw/inbox/` | phone capture | **sync the inbox subfolder only**, never the vault root — OneDrive and `.git` conflict badly |
| WhatsApp → OpenClaw | phone, lowest friction | needs an always-on host — see conflict below |

## Unresolved conflict: always-on

Subscription-only and WhatsApp are in tension. Compilation and brief *generation* run fine
on the subscription (interactively, or as a scheduled Claude Code routine). But WhatsApp as
a live capture inbox and query surface needs OpenClaw running 24/7 — a closed laptop means
a dead assistant. That requires a small VPS (~$5/mo), a Pi, or an always-on desktop.

Everything else on the list runs at ~$0. WhatsApp is the only item that does not.

## Nudge escalation

"Every week, forever" as stated has a failure mode that is also abandonment condition #2: a
loop ignored twelve weeks running trains you to skim past the whole brief. Proposed
refinement — it does return every week, but after 4 unacknowledged appearances it is
promoted to a **decide-now** block at the top of the brief: kill it, schedule it, or
demote it to someday. Still weekly, with a forcing function.

## Locked — round 3

| # | Decision |
|---|---|
| Calendar | **Advise only.** The brief says the event does not exist; you make it. No OAuth write scope. |
| WhatsApp | **Deferred.** Revisit once the system is in daily use and the ~$5/mo always-on host is earned. |
| Nudge escalation | **Accepted** — weekly return, promoted to a decide-now block after 4 unacknowledged appearances. |
| OneDrive inbox sync | **Dropped.** No phone capture in v1. Capture is laptop-only: drag-drop, Web Clipper, `/capture`. |
| Brief delivery | Scheduled Claude Code routine → **email**. The only push channel needing no always-on host. |

Nothing open. Specification is closed — see [`../README.md`](../README.md).

## Locked — round 4 (tooling)

| # | Decision |
|---|---|
| **D4 reversed** | **Repo and vault are the same folder.** The original split (private vault, shareable code) assumed a confidentiality boundary that round 2 removed — the repo is already private, single-user, all material the user's own. Merging them means skills load automatically on opening the folder, everything is versioned together, and the Windows skill-copy problem never arises. |
| Skills location | `.claude/skills/` inside the repo. Project-scoped, version-controlled, no install step. |
| Third-party llm-wiki plugins | **Not installed.** Same reasoning as the GBrain verdict — they implement the generic pattern and would fight the `loops/` layer, the two-store split, and decompilation. |
| Built-in skills used | `schedule` (weekly brief), `update-config` (permissions and hooks), `code-review` / `simplify` (once there is code). |
| Installed user skills | All 17 are design/animation packs. **None relevant.** No action. |

Written this round: `CLAUDE.md` (the vault schema — build step 1), `.claude/skills/capture`
(step 2), `.claude/skills/ingest` (step 4). Remaining skills — `/brief`, `/ask`, `/lint`,
`/unsource` — are written at their build steps, not speculatively.

## Locked — round 5 (the offering, corrected)

Loops were promoted to the spine of the project on the strength of two examples in A1. That
was an over-read. **Correction: the offering is the memory layer itself, and it is all four
of these at once** — none subordinate:

1. **Never start from zero** — any session, project, or agent already knows you.
2. **One archive you can interrogate** — everything scattered, consolidated, citable.
3. **Reachable from anywhere** — not locked in one folder or one tool.
4. **It compounds** — connections form across time.

Loops remain wanted, as a **capability of** the memory rather than the reason for it.

### Consequence: the MCP server moves from last to next

Pillar 3 was scheduled at step 10 and treated as roughly equivalent to WhatsApp. That
conflated two very different things:

| Reach | Needs | Cost | Was | Now |
|---|---|---|---|---|
| Any agent or project on this laptop | MCP server, local, on demand | free | step 10 | **step 10, next up** |
| Phone, away from the laptop | OpenClaw on an always-on host | ~$5/mo | step 10 | step 11, still deferred |

Most of pillar 3's value is in the first row and costs nothing. A vault reachable only when
Claude Code is open in its own folder is a folder, not a memory layer — which means the
current state fails pillar 3 outright, and pillars 1 and 2 partially (the memory cannot
reach you while you work in `rag-project` or `kyarayum`).

Rewritten this round: README spine, `docs/comparison.md` positioning.
