---
name: close
description: Close an open loop — produce the artifact that resolves it (a drafted email, event details, a summary, a decision) and mark it done, killed, or someday. Use when the user says "close this", "draft that email", "help me deal with X", or picks something from a weekly brief.
---

# close

Take one open loop and remove the friction that has kept it open. Tracking a loop is worth
little; this is where the system earns its place.

## How to write

Neutral, plain, direct — a reference article, not an essay. Follow Orwell's rules: no
familiar figures of speech, no long word where a short one works, cut every word that can
go, active over passive, everyday English over jargon. Give numbers where you have them.
No throat-clearing, no closing remark.

## Procedure

**1. Find the loop.** Named by the user, or picked from `loops/open/`. If they are referring
to something in the last brief, read `briefs/` to resolve it. Ambiguous → list candidates.

**2. Read its provenance.** Every loop cites the source that produced it. Read that source.
A draft written without it will be generic, and generic is what makes the user stop using
this.

**3. Gather context.** `mem/profile.md` for voice and working style, `mem/people.md` if a
person is involved, and any `wiki/` pages the loop touches. Cite what you use.

**4. Produce the artifact — in full, not described.**

| Loop | Produce |
|---|---|
| owes someone an email or message | the drafted message, subject line included, ready to paste |
| a date or deadline | event title, date, time, and the details to paste in |
| something unread | a summary of the actual source — what it says, whether it still matters |
| an undecided decision | the options, what the vault knows about each, and a recommendation |
| a task with no obvious artifact | the smallest concrete next action, written out |

Write the thing. Do not write *about* the thing. "You could email them explaining the
delay" is a failure; the email itself is the deliverable.

**5. Ask what to do with the loop:**

- **done** — move to `loops/closed/`, `status: done`
- **killed** — move to `loops/closed/`, `status: killed`, record why
- **someday** — stays open, `status: someday`, stops appearing weekly
- **still open** — leave it, reset `surfaced: 0` since it has now been acted on

**6. File the artifact** if it is worth keeping — a summary belongs in `wiki/synthesis/`, a
sent message does not. Ask if unsure.

**7. Log:** `## [YYYY-MM-DD] close | <loop> — <outcome>`

## Rules

- **Never send. Never write a calendar. Never post.** Produce and hand over. This is enforced
  by holding no credentials that could do otherwise; do not work around it.
- **Never invent facts to make a draft read well.** Mark what you do not know as
  `[gap: what's missing]` and say so. A confident wrong draft about a real person is the
  worst thing this system could produce.
- **Match their voice**, drawn from `mem/` and their own writing in `raw/`. If you have too
  little to go on, say so and write plainly rather than guessing at a style.
- **One loop per run.** Batch-closing produces four mediocre drafts instead of one good one.
- If closing reveals a new commitment, open a new loop for it and say so.
