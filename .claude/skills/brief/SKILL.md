---
name: brief
description: Write the periodic brief — what to do today, what is coming this week, and things captured and forgotten. Use when the user says "brief", "weekly review", "what changed", or on the schedule.
---

# brief

The brief tells the user what to do today and resurfaces what they would otherwise lose.

It does not explain their work back to them. They know how to update a CV, prepare for an
interview, or plan a launch. Telling them how is noise, and it is the fastest way to make
the brief unreadable.

Check `mem/rules.md` for a `## Brief` section first. Anything there overrides this file.

## How to write

Neutral and factual, like a reference entry. State the fact and stop. Follow Orwell's rules:

1. No metaphor, simile or figure of speech you are used to seeing in print.
2. No long word where a short one will do.
3. Cut every word that can be cut.
4. Active, not passive.
5. Everyday English, not jargon.
6. Break any of these before writing something barbarous.

| Do not write | Write |
|---|---|
| "This has been sitting unresolved for some time" | "Open since 12 August." |
| "It might be worth considering whether to..." | "Decide whether to..." |
| "The deadline is fast approaching" | "Due Sunday." |
| "The vault has no record of X" | *(nothing — say only what is there)* |
| "No calendar event exists" | *(nothing — it is not an action)* |
| "a number of items" | "four items" |

No opening line about what the brief covers. No closing remark. No commentary on the
system's own reasoning, counters, or file paths. The first line of a section is the first
fact.

**Write long lines.** Do not hard-wrap sentences mid-clause; the email renders them as
written.

## Title

```
# Morning Brief — Monday, 31 August 2026
```

`Morning Brief` on a weekday, `Weekend Brief` on Saturday or Sunday. Full day name, full
month, four-digit year. Nothing else on the line.

## Structure

Three sections. Two of them are often empty, and an empty section is omitted entirely.

```markdown
# Morning Brief — Monday, 31 August 2026

## Now
<Only what is to be done TODAY, or worked on continuously today. Nothing else.

One item per entry, in this shape:

**Foundation go-to-market planning** — today
Sit down with Kyara for 45 minutes. Four questions: first donor by name, what they fund,
what you can show, what you ask for.

**AI projects** — continuous, 11 September
Procedural Art Generator is unstarted and scheduled last.

Keep the elaboration to one or two lines. State what it is and when, not how to do it.>

## Soon
<This week, and early next week only when it genuinely needs preparing for now. Nothing
further out — a deadline three weeks away is not news today.

Same shape, usually one line each:

**Trip** — Friday 4 to Sunday 6 September
Pack Wednesday.>

## Don't forget
<The section that earns the brief. Things captured and not returned to: an article dumped
and unread, a note about something to look into, a decision deferred and gone quiet.

These are the items the user would otherwise lose, which is the whole reason this system
exists. Rank by how likely they are to be lost, not by importance.

**How complex systems fail** — saved 30 August, unread
`raw/articles/2026-08-30-how-complexsystems-fail.md`

**collectui.com** — saved 29 August, no note on why

Give the title, when it arrived, and where it is. Nothing more.>
```

## What never appears

Removed because they carried no information:

- **Still open** — a list of everything outstanding, most of it not actionable today.
- **Worth knowing** — vault housekeeping.
- **Compiled this week** — page and source counts.
- Anything of the form "the vault has no record", "no calendar event exists", "nothing has
  been added since". Absence is not an action.
- Instructions for work the user already knows how to do.
- File paths, except in **Don't forget**, where the path is how they find the thing.
- Counters, `surfaced` values, or any description of how the brief was assembled.

## Overdue

An item more than 14 days past its date goes at the top of `Now` with three options and
nothing else:

```
**Foundation go-to-market planning** — due 31 August, 23 days ago
Drop it, set a new date, or do it now.
```

The daily due check stops reminding at 14 days so this can take over. Do not soften it and
do not carry it silently. An item nobody has acted on for three weeks is dead or mis-dated;
both are answers, leaving it open is not.

## Length

The whole brief fits on a phone screen. If it does not, `Now` is holding things that belong
in `Soon`, or `Soon` is holding things that belong nowhere.

## Then

- Increment `surfaced:` on every loop that appeared, except ones acted on since the last
  brief.
- Write to `briefs/YYYY-MM-DD.md`.
- Append to `log.md`: `## [YYYY-MM-DD] brief | <date>`.

## Rules

- **`Now` means today.** Not this week, not soon. If it cannot be started today, it is not
  in `Now`.
- **Rank against stated goals**, then by deadline.
- **Never invent an item to fill a section.** Omit the section.
- **Never write a calendar entry.** Do not mention that one is missing either.
- If the inbox holds more than five uncompiled items, or one has waited more than two weeks,
  add a single line at the end: `12 items uncompiled, oldest 16 days. Run /ingest-all.`
  Otherwise say nothing about the inbox.
