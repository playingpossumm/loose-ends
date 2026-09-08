---
name: ingest-all
description: Compile every uncompiled source in raw/inbox in one pass — plan the whole batch first, approve once, then write. Use when the user says "ingest all", "compile everything", "clear the inbox", or when several sources are waiting and compiling them one at a time is just friction.
---

# ingest-all

Same work as `/ingest`, done across the whole inbox with **one approval instead of one per
source**. Everything in [`../ingest/SKILL.md`](../ingest/SKILL.md) still applies — the rules
about citation, provenance, contradictions and loops are not relaxed because there are more
files.

What changes is only where the human checkpoint sits: once, over the whole batch, instead of
between every source.

Read [CLAUDE.md](../../../CLAUDE.md) first if you have not this session.

## Drain first

Before planning anything, run:

```
python scripts/telegram_capture.py --once
```

`/ingest-all` compiles what is in `raw/inbox/`, and Telegram messages only land there when
that script runs. Without this step, "compile everything" silently means "compile everything
that arrived before the last scheduled drain" — so a note sent from your phone an hour ago
is missed, and the run reports success anyway.

`--weekly` already drains before writing the brief, for the same reason. Draining twice
costs nothing: the script tracks an offset, so a second run in the same minute fetches
nothing.

## What writes itself, and what waits

Not every source carries the same risk, so not every source needs the same approval. Plan
the whole batch first, as always, then split it.

The test is **which store the plan writes to**, which is the two-store distinction in
`CLAUDE.md` applied one step earlier — at the decision of whether to write, not only at what
may be written.

| The plan writes | Stakes | Then |
|---|---|---|
| `wiki/` only | rebuildable from `raw/` at any time | **write it** |
| a loop carrying a date | a nudge fires, or fails to fire | **hold** |
| a change to a date already recorded | the same, and it overrides something you set | **hold** |
| anything in `mem/` | nothing can reconstruct it | **hold** — you may only propose there anyway |
| a claim contradicting a page in the vault | both must be kept and the conflict recorded | **hold** |
| more than one reading of what the source means | a guess becomes a fact once written | **hold** |

A wrong `wiki/` page costs a regeneration. A wrong date costs a reminder that does not
arrive, or one that arrives about the wrong thing. That asymmetry is the whole rule.

**The mixed case is the common one.** An article saved is knowledge; "I should read this" is
a commitment. Write the source page, hold the loop. The reader keeps what was learned and
still decides what is owed.

**Held sources stay in `raw/inbox/`.** Do not move them, do not mark them, do not write a
holding file. Whatever remains in the inbox after a pass is by definition what waited, which
is what the brief counts and reports. Re-planning them on the next pass is intended: the
vault has changed since, and a source that was ambiguous last night may not be tonight.

**Say what you did.** Every source that wrote itself gets one line in the report, and every
source held gets one line saying which row of the table above caught it. Nothing enters the
vault unseen, and nothing waits without a stated reason.


## Promotion

Compiling the whole inbox at once is the only moment the compiler sees across sources, so it
is the right moment to promote. After writing every source, run `python scripts/synthesis.py`
and create the entity and concept pages it lists.

This is where the wiki stops being a pile of source summaries. A vault with fifty source
pages and no entity pages answers "what do I know about X" by re-reading fifty pages and
learning nothing that persists.


## Procedure

**1. List what is waiting.** Every file in `raw/inbox/` with `status: uncompiled`, oldest
first. Say how many. If more than 10, do the oldest 10 and say the rest are still queued —
a batch too large to read the plan for is a batch nobody actually approves.

**2. Read them all, and orient once.** Read `index.md` and the existing pages that any of
them plausibly touch. Doing this once for the batch is the main saving over running
`/ingest` repeatedly.

**3. Plan the entire batch before writing anything.** One block per source:

```
1. 2026-08-30-collect-boardgames.md
   pages   wiki/sources/… (new), wiki/concepts/boardgames (new)
   loops   "decide which boardgame to buy" — overlaps #3 below
   flags   none

2. 2026-08-30-start-learning-to-cook.md
   pages   wiki/sources/… (new)
   loops   "start learning to cook" — due end of September
   flags   none

3. …

Total: 8 sources, ~14 pages, 5 loops, 1 contradiction.
Proceed, or shall I hold any of these back?
```

**Look across the batch, not just within each source.** This is the thing one-at-a-time
compiling cannot do:

- **Duplicate loops.** Three notes about boardgames should produce one loop, not three.
  Say which you are merging.
- **Entity promotion.** A name appearing across several sources in the batch may cross the
  three-mention threshold now. Promote it — mention that you are.
- **Sources that contradict each other**, not only ones contradicting the existing wiki.

**4. Wait for approval.** Do not write before it. One approval for the batch is the point;
zero approvals is not.

**5. Compile in order**, applying `/ingest`'s rules to each. Report a line per source as you
go, so a long batch shows progress rather than going silent.

**6. Stop mid-batch and ask** if any of these happen — do not push through:

- a source would touch more than 15 pages on its own
- a source is unreadable, or its `attachment:` is missing
- a source contradicts something you already wrote *earlier in this same batch*
- the total is heading past ~40 pages

Report what is done, what stopped you, and what remains. A half-finished batch you were told
about beats a finished one that quietly went wrong.

**7. Update `index.md` once** at the end, not per source.

**8. Append one log entry per source** — the log is a per-source record and batching must
not collapse it, or `/unsource` loses the trail:

```
## [YYYY-MM-DD] ingest | <title>
```

Then one batch line:

```
## [YYYY-MM-DD] ingest-all | N sources, N pages, N loops
```

**9. Report** in five lines or fewer: sources compiled, pages created and updated, loops
opened, loops merged, contradictions flagged, anything held back.

## When not to use this

**The first ten sources of a new vault.** Compile those one at a time — you are still
learning whether the compiler reads your material the way you would, and per-source approval
is how you find that out. Batch once you trust it.

**When the inbox is a mixed bag of important and trivial.** A batch plan encourages skimming.
If two of eight actually matter, `/ingest` those two properly first.

## Rules

Everything in `/ingest` holds. Emphatically:

- **Every claim cites a source and a locator.** More files is not a reason to get loose.
- **Never write `mem/`.** Propose at the end; the human decides.
- **`raw/` stays immutable** apart from `status:`.
- **Be conservative about loops** — a batch is where false loops multiply fastest, and
  brief precision is the metric this project lives on. When unsure, list it rather than
  filing it.
