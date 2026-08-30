---
name: brief
description: Write the periodic brief — what needs deciding, what is due, and the work already started so it can be decided quickly. Use when the user says "brief", "weekly review", "what changed", or on the schedule.
---

# brief

The brief is the product of this system. Everything else is substrate.

**It reports on the user's life, not on the vault's activity.** That is the whole rule.
Nobody needs to be told how many sources compiled or how many pages were touched — that is
the system talking about itself, and it is why briefs get skimmed and then ignored.

Every line must carry a decision, a deadline, or a fact that changes what the user does
today. If a line does none of those, cut it.

Check `mem/rules.md` for a `## Brief` section first — the user may have set tone and how
hard to push. That overrides the defaults here.

## Read

`log.md` since the last brief · every `loops/open/*.md` · `loops/dates/` for the next 14
days · `mem/goals.md` and `mem/projects.md` for what actually matters · a count of
`raw/inbox/` items still `status: uncompiled`.

## Structure

Ordered by urgency, not by category. Nearest deadline first, always.

```markdown
# <date>

## Now
<Anything due within 7 days, or any loop at surfaced >= 4. For each: one line saying what
and when — then the artifact that closes it, in full, below the fold. Skip the section if
genuinely nothing is due.>

## Soon
<Dates and deadlines, 8-14 days out. One line each. What it is, when, and the one thing
that is missing — "no calendar event exists", "no agenda written yet".>

## Still open
<Everything else, one line each, ranked against stated goals. Name and why it matters. No
sub-bullets, no commentary about how many times it has surfaced.>

## Worth knowing
<At most three lines. Only gaps that block a decision above, or something that changed
underneath the user — a stale project date, a contradiction between sources. Omit the
section entirely if there is nothing.>

---

## <artifact for each item under Now>
```

## Length

**The summary — everything above the divider — fits on a phone screen.** Roughly 15 lines.
If it does not fit, the ranking is wrong: cut from the bottom, never from `Now`.

**Artifacts below the divider are uncapped.** A three-line summary and one genuinely useful
draft is the brief working correctly. Length below the fold is earned; length above it is
noise.

## Never include

These all appeared in early briefs and all made it worse:

- **Vault statistics.** "5 sources, 19 pages touched, 3 loops killed." Zero action value.
- **Meta-commentary about the system's own reasoning.** "Corrected in the compiler's rules
  for future ingests." "Highest `surfaced` is 1, so nothing has been ignored yet." The user
  does not need the mechanism narrated.
- **Sections that exist to say they are empty.** No `*(none)*`. Omit the heading.
- **Restating what the user just told you.** If they answered six loops yesterday, do not
  report that back as news.
- **File paths in the summary.** They belong in the artifact, if anywhere. A path in a nudge
  is clutter.
- **Hedging about your own confidence.** State it or leave it out.

## Uncompiled inbox

Capture is automated; compilation is not, so material can pile up unseen.

**Say nothing when the inbox is small and fresh.** Mention it only when it is actually a
problem — more than five items, or anything waiting more than two weeks — and then in one
line under `Worth knowing`:

> 7 things captured but not compiled, oldest 16 days. Run `/ingest-all`.

That is failure condition #1 and worth flagging when real. A daily nag about two items from
yesterday is exactly the noise that gets briefs ignored.

## Then

- Increment `surfaced:` on every loop that appeared, **except** ones the user acted on or
  answered since the last brief.
- Write to `briefs/YYYY-MM-DD.md`.
- Append to `log.md`: `## [YYYY-MM-DD] brief | <date>`.

## Rules

- **Rank against stated goals, not recency.** A loop touching a real goal beats three
  fresher trivial ones.
- **Nearest deadline leads.** Always.
- **Every item under `Now` arrives with its artifact** — the drafted email, the agenda, the
  summary, the options. A nudge without the work started is just a reminder, and reminders
  are what failed before this existed.
- **Calendar items are advice.** Say the event does not exist. Never create it.
- **Never invent an item to fill a section.** A short brief is a good brief. Precision is the
  metric this project is judged on: one bad nudge costs more than five missing ones.
- **Mark real gaps `[gap: ...]`** inside artifacts rather than guessing. A confident wrong
  draft is worse than an honestly incomplete one.
