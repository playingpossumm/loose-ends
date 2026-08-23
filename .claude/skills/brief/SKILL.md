---
name: brief
description: Generate the weekly brief — what compiled, what contradicted, what went stale, and which open loops need a decision now. Use when the user says "brief", "weekly review", "what changed", or on the weekly schedule.
---

# brief

The weekly brief is the product of this system. Everything else is substrate. If the brief
stops being read, the project has failed — so the constraint below is not stylistic.

**Maximum ten lines of substance.** Not ten paragraphs. A brief that grows every week gets
skimmed, then ignored. Cut the least important thing rather than adding an eleventh line.

## Build it

1. Read `log.md` since the last brief in `briefs/`.
2. Read every `loops/open/*.md`.
3. Read `mem/goals.md` and `mem/projects.md` — a loop that serves a stated goal ranks above
   one that does not.
4. Check `loops/dates/` for anything falling in the next 14 days.

## Structure

```markdown
# Week of YYYY-MM-DD

## Decide now
<loops with surfaced >= 4. For each: what it was, where it came from, and the three
options — kill it, schedule it, or demote to someday. Empty section if none.>

## Open loops
<the rest, ranked by relevance to current goals and projects. One line each, with a
citation back to where the loop came from.>

## Coming up
<dates within 14 days. What the implied action is — e.g. "no calendar event exists">

## Compiled this week
<one line: N sources, N pages touched. Not a list.>

## Flagged
<contradictions found, and anything that went stale. One line each. Omit if empty.>

## What the brain doesn't know
<coverage gaps: topics with thin sourcing, entities mentioned but never compiled,
questions asked this week that the vault couldn't answer.>
```

## Then

- Increment `surfaced:` on every open loop that appeared, **except** those the user
  acknowledged or acted on since the last brief.
- Write to `briefs/YYYY-MM-DD.md`.
- Append to `log.md`: `## [YYYY-MM-DD] brief | week of YYYY-MM-DD`.

## Rules

- **Rank by the user's actual goals**, not by recency. A loop touching a stated goal beats
  three fresher trivial ones.
- **Every loop carries its provenance.** "You said this in the PDF you filed on 3 August"
  is the line that makes a nudge land instead of feeling arbitrary.
- **Calendar items are advice, never actions.** Say the event does not exist. Do not create
  it.
- **The coverage note is mandatory**, even when it is "nothing obvious missing."
- **Never invent a loop to fill the brief.** A short brief is a good brief. Precision is the
  metric this project is judged on — one bad nudge costs more than five missing ones.
