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

## OPEN

- **C1** — which WhatsApp role: capture inbox, query surface, or chat-history corpus.
- **Calendar** — does the system *create* events, or only tell you to?
- **Capture path** — how material physically reaches `raw/` from desktop and phone.
- **Brief delivery** — where the weekly brief arrives.
- **Nudge persistence** — re-raise forever, escalate, or expire.
- **Subscription vs API** — the $0 vs ~$25/mo fork.
- **Main-job material** — confidentiality constraints, if any.
- **N1** — monthly ceiling.
