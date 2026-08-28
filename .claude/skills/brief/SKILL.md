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
5. **Count `raw/inbox/` — anything with `status: uncompiled`.** Capture is automated;
   compilation is not. Material arrives from Telegram and the clipper on its own, but it
   only becomes pages, links and loops when someone runs `/ingest`. Uncompiled material is
   invisible to everything else in this brief, so it has to be surfaced here or it silently
   rots.

## Structure

```markdown
# Week of YYYY-MM-DD

## Decide now
<loops with surfaced >= 4. For each: what it was, where it came from, the three
options — kill it, schedule it, demote to someday — AND the artifact that closes it,
written out in full. See "arrive with the work started" below. Empty section if none.>

## Open loops
<the rest, ranked by relevance to current goals and projects. One line each, with a
citation back to where the loop came from.>

## Coming up
<dates within 14 days. What the implied action is — e.g. "no calendar event exists">

## Waiting to be compiled
<N items sitting uncompiled in raw/inbox/, oldest first, with their titles and how long
they have been waiting. Say plainly that these are invisible until /ingest runs, and give
the command. Omit the section entirely when the inbox is empty — an empty inbox needs no
paragraph congratulating itself.

If anything has been waiting more than two weeks, say so directly: capture without
compilation is how this system fails quietly, and it is failure condition #1.>

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

## Arrive with the work started

A loop the user has ignored four times does not need a fifth reminder. It needs the friction
removed. For everything in **Decide now**, produce the artifact that would close it — in
full, inline, ready to use:

| Loop | Produce |
|---|---|
| owes someone an email or message | the **drafted message**, in their voice, with vault context already in it |
| a date or deadline | the event details ready to paste, and the fact that nothing exists yet |
| something unread | a short summary from the source, so they can decide whether they still care |
| an undecided decision | the options, with what the vault knows about each |
| anything else | the smallest concrete next action, written out, not described |

Draw the voice from `mem/profile.md` and past material in `raw/`. Draw the facts from the
vault and cite them. If you lack what you need to draft well, say what is missing rather
than inventing details — a wrong draft costs more than no draft.

**Drafts only. Never send anything, never write a calendar.** Produce the artifact and stop.
If a draft needs a fact you do not have, leave a clearly marked `[gap: ...]` rather than
guessing.

Keep the ten-line cap for the brief's *summary* sections. Drafts sit below it and do not
count — a brief that is three lines of nudge and one good email draft is working correctly.

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
