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

No closing remark. No commentary on the system's own reasoning, counters, or file paths.
The first line of a section is the first fact.

**Write long lines.** Do not hard-wrap sentences mid-clause; the email renders them as
written.

## Title

```
# Morning Brief — Monday, 31 August 2026
```

`Morning Brief` on a weekday, `Weekend Brief` on Saturday or Sunday. Full day name, full
month, four-digit year. Nothing else on the line.

## Opening

Two or three sentences under the title, before the first section. **Name things.** Every
sentence must contain a real item and a real date, or it is not worth writing.

```
The RAG project is due tomorrow at 75%, and Kyara is waiting on the GTM plan today. Sunday
takes the CV, the portfolio and the personal website at once, with the Jakarta trip
occupying Friday to Sunday before it.
```

Do not write a sentence whose subject is the report — no "this brief covers", "here is what
is coming up", "as of today". Do not do arithmetic on the reader's behalf: "six working
days, three of them away" is a calculation, not a fact, and it belongs nowhere in the brief.
If nothing is due, say that in one sentence and omit the empty sections.

## Structure

Three sections. Two of them are often empty, and an empty section is omitted entirely.

Every entry is a level-three heading followed by one or two lines:

```
### Proper Title — when it is due

One or two lines.
```

Use `###`, not bold. The heading is what puts space above each entry and keeps its detail
attached to it; bold text renders as another paragraph and the whole section reads as one
block.

### Titles

Use the real name of the thing, in title case. Standard abbreviations are fine.

| Wrong | Right |
|---|---|
| RAG | RAG Project |
| Foundation go-to-market planning | Foundation GTM Planning |
| Masters | Masters Applications |
| Trip | Jakarta Trip |
| Haircut | Haircut Booking |
| CV and portfolio | CV and Portfolio |

A single generic word is not a title. If the entry is called `Sheet` or `Website` or
`Interview`, name which one. Where the vault does not know which one, do not paper over it
with a vague description — quote the user's own words verbatim so at least he recognises
what he meant, and offer to drop it.

**Link anything that has a URL.** An article, a page, a tool, a repository: the title is the
link.

```
### [How Complex Systems Fail](https://how.complexsystems.fail/) — 20 minutes
```

A reminder to read something that does not include the thing to read is a reminder to go
looking for it.

### The timing after the dash

A date, a deadline, or how long the thing takes. Nothing else.

| Wrong | Right |
|---|---|
| saved 30 August | due 30 November |
| captured 29 August | 20 minutes |
| added last week | Thursday 3 September |

When the item has no date and no useful duration, drop the dash and the timing and give the
title alone. When something arrived is not a deadline, and the user already knows he saved
it.

### Numbers

Digits and standard symbols: `75%`, `20 minutes`, `£40`, `3 September`. Never `75 per cent`.
Spell out only where a digit starts a sentence.

### The three sections

```markdown
# Morning Brief — Monday, 31 August 2026

<Opening paragraph. Two or three sentences, each naming a real item and a real date.>

## Now
<Only what is to be done today, or worked on continuously today. Nothing else.

### Foundation GTM Planning — today

Sit down with Kyara and write it down. Q4 starts in one month.

### RAG Project — due tomorrow

At 75%. Remaining technical work, plus the UI.

State what it is and when. Not how to do it.>

## Soon
<This week. Early next week only when it needs preparing for now. Nothing further out.

### Jakarta Trip — Friday 4 to Sunday 6 September

Pack Wednesday.

### Masters Applications — Thursday 3 September

Find the closing date. No programme or school recorded yet.>

## Don't forget
<Things captured and not returned to. These are what the user would otherwise lose, which is
what the system is for. Rank by how likely they are to be lost.

### [How Complex Systems Fail](https://how.complexsystems.fail/) — 20 minutes

Richard Cook, 18 principles. Unread.

### [Collect UI](https://collectui.com/)

A gallery of interface patterns.

Give the real title, link it if it has a URL, and say what the thing is if the name does not
carry it. Never say where the file lives, never say a loop produced it, never say when it
was saved, and never say that no note was attached.>
```

## What never appears

Removed because they carried no information:

- **Still open** — a list of everything outstanding, most of it not actionable today.
- **Worth knowing** — vault housekeeping.
- **Compiled this week** — page and source counts.
- Anything of the form "the vault has no record", "no calendar event exists", "nothing has
  been added since". Absence is not an action.
- Instructions for work the user already knows how to do.
- File paths. Anywhere. The user opens the vault to find things, not the brief.
- "no note on why", "nothing recorded", "untouched since" as a description of what the
  user did or did not do when saving something.
- Which loop or source an item came from.
- Counters, `surfaced` values, or any description of how the brief was assembled.

## Overdue

An item more than 14 days past its date goes at the top of `Now` with three options and
nothing else:

```
### Foundation GTM Planning — due 31 August, 23 days ago

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
