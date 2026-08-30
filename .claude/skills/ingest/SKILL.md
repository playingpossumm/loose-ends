---
name: ingest
description: Compile one uncompiled source from raw/inbox into the wiki and loops — extract claims, write and update pages, link them, extract open loops, flag contradictions, update index.md and log.md. Use when the user says "ingest", "compile", "process my inbox", or asks what is waiting to be compiled.
---

# ingest

Compile **one** source at a time. This is the irreversible step in the system — everything
else can be redone from `raw/`, but a bad compile spreads across many pages before anyone
notices. Work carefully and stay inside the caps.

Read [CLAUDE.md](../../../CLAUDE.md) first if you have not this session. Its rules override
anything here.

## Procedure

**1. Pick the source.** Named by the user, or the oldest `status: uncompiled` file in
`raw/inbox/`. If several are waiting, say how many and compile one.

**2. Read it fully — including anything it points at.**

Check the frontmatter before you start:

| Field | What it means for you |
|---|---|
| `attachment:` | **The markdown is only a stub. Open the file it names** — that is the real source. A Telegram-captured PDF or photo has its text in the attachment, not the page. |
| `origin: telegram (forwarded from X)` | X sent this, the user relayed it. Attribute claims to X, not to the user. This distinction matters and is easy to lose. |
| `kind: image` | View the image itself, not only any transcription beside it. |
| `sent:` vs `captured:` | When they said it vs when it was filed. Use `sent:` for anything time-sensitive — a forwarded message can arrive days late. |

**3. Orient before writing.** Read `index.md`, then every existing page plausibly related.
You cannot flag a contradiction against a page you did not read — this step is what makes
step 6 work, and skipping it is the most common way this system silently degrades.

**4. Extract, and show your work.** Before writing anything, list for the user:
- key claims, each with its locator in the source
- entities mentioned (people, tools, papers, projects, concepts)
- **open loops** — see below
- contradictions with existing pages
- which pages you intend to create or update

Stop here if the plan touches more than 15 pages. Ask.

**5. Write.**
- `wiki/sources/<id>.md` — one page for this source: what it is, what it claims, why it
  matters.
- `wiki/entities/`, `wiki/concepts/` — create or update. Promote a mention to its own page
  at 3 independent source mentions, or if the user asks.
- On every page touched, add this source's id to `sources:` and bump `updated:`. This is
  what makes `/unsource` possible later. Do not skip it.
- Concept pages keep `## What sources say` and `## Current view` separate. Never merge them.

**6. Contradictions.** Never overwrite. Keep both claims with dates and sources, mark the
section, and log it. Resolution belongs to the human.

**7. Loops — this is the part that matters most.** Scan for anything stated but unresolved:

| Signal | Example |
|---|---|
| stated intent | "I want to learn X", "I should read this" |
| commitment | "I'll send them the thing" |
| dated fact implying action | a birthday, a deadline, a renewal |
| a source captured for a purpose that never happened | a PDF filed under "to read" |

Write each to `loops/open/<id>.md` with `status: open`, `surfaced: 0`, a citation back to
where it came from, and `due:` if one is implied. Dated facts go to `loops/dates/`.

Be conservative. A false loop costs the user trust in the brief, and brief precision
is the metric this project lives or dies by. When unsure, list it for the user rather than
filing it.

**8. Update `index.md`** with every new page, one line each.

**9. Append to `log.md`**, keeping the prefix format exactly so `grep "^## \["` works:

```
## [YYYY-MM-DD] ingest | <title>
```

**10. File the raw source** from `raw/inbox/` into the right `raw/` subfolder and set
`status: compiled`.

**11. Report** in five lines or fewer: what compiled, pages created, pages updated, loops
opened, contradictions flagged.

## Rules

- **One source per run.** Batch compilation hides mistakes.
- **Max 15 pages touched.** Over that, stop and ask.
- **Every claim cites a source and a locator.** No exceptions, including claims from images
  — cite the image.
- **Never write `mem/`.** If the source implies something about the user's goals,
  preferences, or projects, propose it at the end and let them decide.
- **`raw/` is immutable** apart from the `status:` field.
- **Refuse** credentials, keys, and health records; say you refused.
- If the source is low quality or you cannot verify what it claims, say so plainly. A bad
  source compiled confidently is worse than one not compiled at all.
