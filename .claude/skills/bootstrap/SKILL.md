---
name: bootstrap
description: Interview the user one question at a time to fill mem/ — profile, goals, projects, people, and decision rules. Run once when setting up the vault, and again to refresh. Use when the user says "bootstrap", "set up my brain", "interview me", or when mem/ files still have status "empty".
---

# bootstrap

Fill `mem/` — the self-knowledge store — by interviewing the user. This is the only content
in the vault they author rather than you. Everything downstream is generic without it.

Expect roughly twenty minutes. Say so up front, and say they can stop anywhere and resume.

## The rule that matters

**One question at a time. Wait for the answer before asking the next.** Do not batch
questions, do not present a form, do not move on until they have actually answered. A
dumped list of fifteen questions gets three shallow answers; asked one at a time, the same
fifteen get real ones.

## Cover, in this order

**1. Profile** — who they are, what they do, what the main job is versus what the side work
and hobbies are. How they want you to communicate with them. How they work: when they think
well, what they avoid, what they are bad at.

**2. Goals** — for this year. For each: why it matters, what "done" looks like, and roughly
when. Push for a checkpoint they could actually miss.

**3. Projects** — what is active right now. For each: current state, the next concrete
action, what is blocking it, and any deadline. This is the file that will go stale fastest.

**4. People** — who materially affects their work. Only what they choose to store. Ask
before writing anything about a person; store nothing sensitive.

**5. Rules** — decision rules, quality standards, boundaries. And explicitly: **what must
you never do without asking first?** That answer becomes the top of `rules.md`.

## How to ask

- **Push for concrete examples when an answer is vague.** "I want to get better at writing"
  is not usable. "I want to publish one technical post a month, and I know I won't unless
  something reminds me" is.
- **Never fill a gap with a guess.** If they skip something, write that it is unanswered.
  An honest hole beats an invented fact — and invented facts here poison everything
  downstream, because this is the file you read every session.
- **Preserve their wording** where the phrasing carries meaning. Do not smooth it into
  business prose.
- **Separate stable from temporary.** A role is stable; a current blocker is not. Mark
  temporary items with `stability: temporary` and date anything that can expire.
- **Mark inferences as assumptions**, never as facts.
- **Do not turn a stated preference into a permanent rule** without asking whether it is
  actually a rule.
- **Refuse** to record passwords, keys, credentials, or health data.

## Writing the files

Write each `mem/*.md` as you finish its section, not all at the end — so a stopped interview
still leaves something behind. Keep the frontmatter, set `status: filled`, update `updated:`.

Append to `log.md`:

```
## [YYYY-MM-DD] bootstrap | mem/ filled
```

## Finish with

1. Which files you wrote and what is in them.
2. The five most important things you learned.
3. Five things still missing that would improve the system.
4. One concrete thing they can do with the brain right now.

Then suggest the obvious first move: capture and ingest their first real source.
