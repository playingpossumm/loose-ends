---
name: brief
description: Write the periodic brief — what to do this week, what is coming in the next two to three weeks, and things captured and forgotten. Use when the user says "brief", "weekly review", "what changed", or on the schedule.
---

# brief

The brief tells the user what to do this week and resurfaces what they would otherwise
lose.

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

**Two sentences. Never three.**

Lead with what finishes this week, not with what is late. A paragraph that opens on four
overdue items reads as a charge sheet, and the reader has not reached the list yet.

The first sentence names the work that completes, and what completing it opens up. The
second names what is still outstanding, briefly, and stops.

```
The CV and the personal website both finish this weekend, which clears the run at GMAP
submission on Friday 18 September. RAG and the masters check are still open from last week.
```

What that replaced was four sentences, eleven dates and no order of importance:

```
RAG passed its date yesterday, Friday 11 September, and the two days to Sunday 13 September
already hold the CV, the personal website, the brief redesign and agents and subagents.
Every part of the GMAP preparation is due Thursday 17 September and submission opens Friday
18 September. The masters check is three days past its third date, and route B has no dates
of its own until it is done.
```

Energy comes from brevity and from leading with what is in reach. It never comes from
adjectives. No "you've got this", no "a strong week ahead", no exclamation marks, and nothing
rating the work as big, important or exciting.

Do not write a sentence whose subject is the report: no "this brief covers", "here is what is
coming up", "as of today". Do not do arithmetic for the reader: "six working days, three of
them away" is a calculation nobody asked for.

If nothing is due, say so in one sentence and omit the empty sections.

## Staleness, and what is being held

Anything still in `raw/inbox/` when the brief is written was **held on purpose**, not
forgotten. The nightly pass compiles every source whose plan touches only `wiki/`, and holds
anything that would write a dated loop, change a date already recorded, touch `mem/`,
contradict an existing claim, or that reads more than one way. What remains is what needs a
person.

So report it as a decision waiting, not as a backlog:

```
*2 sources held: the 8 September transaction touches mem/, and "edbert briefing" reads two
ways. Run /ingest-all to settle them.*
```

Say what each one is and why it waited, up to three. Above three, give the count and the two
most consequential. A held source with a date in it goes first, because that is the one where
waiting costs something.

Separately, check `log.md` for the most recent `ingest` entry. If it is **seven or more days
old**, the nightly pass has not been running at all, which is a different fault:

```
*Nothing has compiled for 9 days. The nightly pass may not be running — check
autopilot.log.*
```

Both lines go directly under the opening paragraph, before the first section. A warning about
whether the contents can be trusted is useless after the contents have been read.

Neither condition met means no line at all. Do not write a reassurance that the vault is up
to date; silence is the signal.

## Structure

Three sections. One or two are usually empty, and an empty section is omitted
entirely — `Don't forget` is often empty.

Three heading levels, and they are not interchangeable:

```markdown
## Now                          the section
### Monday 14 September         the date group
#### Thrive Application         the entry
A CV and a written introduction. The posting names no closing date.
```

Entries are `####`, date groups are `###`, sections are `##`. Headings rather than bold
text, because the email stylesheet uses the level to space them: without it, title, detail
and the next title sit the same distance apart and the section reads as one block.

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

### Timing after the title

**No dates after a title. Ever.** The date group above the entry carries the date, and
repeating it is noise. That includes ranges: `#### GMAP Application Prep — Monday 14 to
Sunday 27` says nothing the heading above it has not already said.

| Wrong | Right |
|---|---|
| `#### GMAP Application Prep — Monday 14 to Sunday 27` | `#### GMAP Application Prep` |
| `#### GMAP SEA Submission — Saturday 19 to Sunday 20` | `#### GMAP SEA Submission` |
| `#### CV Update — Sunday 13 September` | `#### CV Update` |

Where a range genuinely matters, the detail line is the place for it, and only when the span
changes what the reader would do:

```
#### GMAP SEA Submission
Management trainee programme, with a logic and numerical test. The window closes Sunday.
```

Two exceptions, and nothing else:

| Allowed | Because |
|---|---|
| `#### How Complex Systems Fail — 20 minutes` | a duration, not a date |
| `#### Masters Check — due 9 September, 5 days ago` | overdue, where the lateness is the point |

**Dates in the detail line are absolute.** A relative word means something different on
Thursday from what it meant on Monday, and the brief is read across the week.

| Wrong | Right |
|---|---|
| today | Monday 31 August |
| due tomorrow | due Tuesday 1 September |
| this weekend | Saturday 5 September |

Day name and date together. The year only when the item falls in a different one.

### Numbers

Digits and standard symbols: `75%`, `20 minutes`, `£40`, `3 September`. Never `75 per cent`.
Spell out only where a digit starts a sentence.

### Grouping inside a section

`Now` and `Soon` are grouped by date, not listed flat. A date that carries work becomes a
subheading; everything without a fixed day sits in one group at the end.

```markdown
## Now

### Monday 14 September

#### Thrive Application
A CV and a written introduction. The posting names no closing date.

#### Masters Check
Find the closing date and which documents are needed.

### Across the week

#### CV and Portfolio
Stage one of the GMAP preparation.

#### Personal Website
The last of the three portfolio projects.
```

Date subheadings carry the day and the date, earliest first. The trailing group is titled
**Across the week** in `Now` and **No fixed date** in `Soon`. Omit it when everything has a
day.

A date subheading with one item under it is still a date subheading. Do not fold it into the
trailing group to save a line.

### The three sections

```markdown
# Morning Brief — Monday, 14 September 2026

<Opening. Two sentences.>
<Then the held line, only if something is held.>

## Now
<This week, grouped by date. Anything due or worked on between today and Sunday.>

## Soon
<The next two to three weeks, grouped the same way.>

## Don't forget
<Only things to read and things to buy. See below.>
```

### Don't forget

**Two kinds of thing, and nothing else:**

- **Something to read.** An article, a paper, a page saved and never opened.
- **Something to buy.** An item the user said they wanted.

That is the whole scope. It is the gentle end of the brief, and it exists so a saved article
does not vanish.

**It is not a place for work.** A decision, an evaluation, something to write, a list to
confirm: those are tasks. They belong in `Now` or `Soon` under a date, or nowhere.

| Belongs | Does not belong |
|---|---|
| An unread article, with its reading time | "Antigravity", because evaluating a tool is a task |
| A monitor the user said they wanted | "The Five Books List", because confirming a list is a task |
| A saved paper, unopened | "Coding and Writing Rules Prompt", because that is work |

```
#### [How Complex Systems Fail](https://how.complexsystems.fail/)
Richard Cook, 18 principles. About 20 minutes.
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
- Counts of pages, sources or compiled items.
- **A closing sentence arguing why the item matters.** "A verdict closes it." "The reading
  goal cannot be tracked without it." "Thrive is waiting behind it." The reader knows why
  their own work matters, and saying it back is the brief padding itself. State what the
  thing is and when it is due, then stop.
- **Em dashes inside a detail line.** Use a comma, a colon or a full stop. The dash after a
  title is a separator, not punctuation, and is the only one in the brief.
- Counters, `surfaced` values, or any description of how the brief was assembled.

## Overdue

An item more than 14 days past its date goes at the top of `Now` with three options and
nothing else:

```
### Foundation GTM Planning — due Monday 31 August, 23 days ago

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

- **`Now` means this week.** The brief is weekly, so a section covering one day would be
  empty most weeks and would leave the rest of the week unreported.
- **Rank against stated goals**, then by deadline.
- **Never invent an item to fill a section.** Omit the section.
- **Never write a calendar entry.** Do not mention that one is missing either.
- **Report what is held, and why.** See above. Held sources are decisions waiting on you,
  and a brief that silently reports a vault missing them is worse than no brief, because it
  is believed.
