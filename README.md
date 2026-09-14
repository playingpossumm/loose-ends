# loose-ends

A second brain that records what you know and tracks what you said you would do.

You send it articles, notes, files and conversations, and it reads each one, writes a page for
it, and answers questions about anything it has read, citing the page that every claim came
from.

It also picks out whatever you said you would do and never closed, then emails it back to you
on a schedule until you either finish it or drop it. Those are the **loops** in the name, and
they are things like an article you saved and never opened, a deadline mentioned once in
passing, or a message you still owe someone. You never type one yourself, because they come
out of material you captured for some entirely different reason.

**Requirements:** Claude Code, and a machine you use most days. No API keys, no server, no
database, no vector store, no monthly cost.

## Install

```bash
git clone https://github.com/playingpossumm/loose-ends.git
cd loose-ends
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ is bin/ on macOS and Linux
python scripts/init_vault.py
```

Keep the vault as its own private repository:

```bash
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-vault --private --source=. --push
cd ..
```

Open Claude Code in the project root, which is the only place the commands exist, and then run
`/bootstrap`. That is an interview filling `mem/` with your goals, projects, people and rules,
and it takes about twenty minutes, though you can stop partway through and resume later. Until
it has run, everything the system writes back to you is generic.

## Commands

| | |
|---|---|
| `/capture` | Record a link, file, note, or the current conversation. |
| `/ingest` | Compile one source. Shows its plan first. |
| `/ingest-all` | Compile every source waiting, under one approval. Drains Telegram first. |
| `/ask` | Answer a question with citations, and state what the vault does not cover. |
| `/close` | Produce the artifact that finishes a loop, then file it. |
| `/brief` | Write the periodic report. |
| `/lint` | Check citations, links, orphans, stale claims, synthesis gaps. |
| `/bootstrap` | The interview that fills `mem/`. |
| `/unsource` | Remove a source and reverse every change it caused. |

## Architecture

Anything you send goes through two separate steps, capture and then compilation. Capture
writes it straight into `raw/` without reading it, so it finishes in a second and cannot fail
on a source it does not understand. Compilation reads that file later, writing a page for the source, updating every
existing page the source touches, and opening a loop for anything you said you would do, which
for a single source can come to as many as fifteen pages.

```
capture → raw/ → compile ─┬→ wiki/  → ask
                          │
                          └→ loops/ → brief → nudge → close
```

### Two stores

`wiki/` holds what you have read, and you can delete the whole of it knowing that a recompile
of `raw/` will rebuild it exactly. `mem/` holds your goals, projects, people and rules, none of
which can be reconstructed from anything else, so the compiler is never allowed to write there
and proposes changes for you to accept instead.

| | `wiki/` | `mem/` |
|---|---|---|
| Written by | the compiler | you |
| Rebuildable from `raw/` | yes | no |
| A contradiction is | a finding: keep both, record it | an error: reported for you to fix |
| The compiler may | write freely | propose only |

### Layout

The system and the content live in two repositories, this public one holding none of your
content and `vault/` being a separate private repository that is gitignored here. Every
compilation lands as a commit in the vault, so you can read the diff of what a source changed
and revert it when it turns out to be wrong.

```
loose-ends/              the system. shareable.
├─ .claude/skills/       the nine commands
├─ mcp/ scripts/ docs/
├─ CLAUDE.md             the schema the model follows
├─ .env                  credentials. gitignored.
└─ vault/                content. gitignored here; a separate private repository.
   ├─ raw/               what you captured, unchanged. never edited.
   ├─ wiki/              sources, entities, concepts
   ├─ loops/             open, dated, closed
   ├─ mem/               profile, goals, projects, people, rules
   └─ index.md  log.md   generated catalogue, and a record of what happened
```

### Search

Two mechanisms work together, both of them reading plain files on disk. The first is
`index.md`, a generated catalogue listing every page with its one-line summary and grouped by
subject, which a question is matched against to narrow a few hundred pages down to a handful.
`grep` then reads the full text of those few pages for anything the summaries did not say.

Both sit behind a single interface, so replacing them with a vector store means changing one
file, though at a few hundred pages there is nothing to gain from doing so.

## Automation

`/brief` writes a brief whenever you ask for one, and the schedule below sends one without
being asked, which matters because remembering to run `/brief` is the exact habit the brief
exists to replace.

With no server and no API key anywhere in this, everything runs as a Windows task on your own
laptop, which is what makes it free and also why the safeguards further down are necessary.

```
python scripts/install_schedule.py --day FRI,SUN --time 19:00
```

That is the base case used here, and it registers the five tasks below.

| Task | Runs | Does |
|---|---|---|
| `Capture` | daily 18:00 | drains Telegram, compiles what triage allows |
| `WeeklyBrief` | Fri and Sun 19:00 | writes the brief, queues it for the morning |
| `BriefCatchup` | Sat and Mon 06:00 | reruns a failed evening, or revises and re-queues |
| `NudgeMorning` | daily 07:00 | due today and overdue |
| `NudgeEvening` | daily 19:30 | the same, for loops marked `nudge: evening` |

A brief therefore arrives at **07:00 on Saturday and 07:00 on Monday**, having been written
the evening before, held out of the inbox overnight by a Gmail filter, and released the next
morning by an Apps Script trigger, which means that writing depends on the laptop being on
while arrival does not, and the setup for all of it is in [`docs/setup.md`](docs/setup.md).

Every day and time above is an argument to `install_schedule.py`, so running it again with
different values replaces all five tasks.

### Triage

The daily 18:00 pass compiles what it can safely handle without you and leaves everything else
alone, planning each source first and then deciding from what that plan would write.

| The plan writes | Then |
|---|---|
| `wiki/` only | compiled |
| a dated loop, or a change to a date already recorded | held |
| anything in `mem/` | held |
| a claim contradicting an existing page | held |
| something that reads more than one way | held |

A wrong `wiki/` page only costs a regeneration, whereas a wrong date costs a reminder that
never arrives, which is why anything touching a date waits for you.

Held sources stay where they are in `raw/inbox/`, so whatever is still sitting there after a
pass is exactly what waited, and the brief lists each one along with the reason it waited.
Running `/ingest-all` clears the backlog whenever you are ready to go through it.

### Reliability

A task only runs while the laptop is on, so the schedule assumes it will sometimes miss.

- Runs at 19:00, delivered 07:00, so the machine is awake when it matters
- Overrides the three Windows defaults that would skip a run on battery, on unplugging, or
  after a miss
- Waits up to ten minutes for a network before starting
- Stops rather than half-running if the network never arrives
- Retries each stage, twice for capture and mail, once for the brief
- Repeats the full pass next morning if the evening failed
- Emails what broke and the command that fixes it

The nudges get the same network wait, the same retries and the same failure email, and a
machine that was switched off will run its missed tasks at the next startup.

### Nudges

A nudge is a short email that sends the thing itself back to you, whether that is the article
you saved and never opened, with its link attached, or the date you set and have not closed
out. Without it a vault is simply where saved things go to accumulate.

One goes out on the day a date arrives and then on days **1, 3, 7 and 14** after it passes,
for as long as the item is still open, with day 14 marked as the last one you will get.
Nothing due in the future ever appears here, since that is the brief's job.

Most days it sends nothing at all, which is deliberate, because a daily message that usually
says nothing due trains you to ignore the channel and then the one that matters gets ignored
along with it.

A loop can pick its own window with `nudge: morning` or `nudge: evening`, so that reading
arrives at 19:30 and anything needing an office to be open arrives at 07:00.

Nudges follow the same writing rules as the brief, and since the only model-authored text in
one is the loop's `summary:` field, those rules are enforced on that field by the frontmatter
contract in [`CLAUDE.md`](CLAUDE.md), which bars repeating the due date that is printed beside
the title anyway, bars relative dates and em dashes, and bars any clause arguing why the item
matters.

## Capture

There are five ways in and all of them write the same thing, a single markdown file in
`raw/inbox/` holding the text, where it came from and when it arrived. Nothing is read until
compilation, so capture cannot fail on a source it does not understand.

| Method | Use | Setup |
|---|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine | none |
| `/capture` | a link, a note, the current conversation | none |
| Obsidian Web Clipper | articles from a browser | 15 min |
| Telegram | anything, from a phone | 5 min |
| `brain_capture` over MCP | from any other project | one command |

Before anything reaches disk, capture refuses labelled credentials such as `password:`,
`api key =`, seed phrases and PEM private key blocks, because the vault is a git repository
and a password is far easier to never store than it is to remove afterwards.

### Telegram

Send anything to your own bot from a phone and the 18:00 drain files it that same evening,
which works because Telegram holds bot messages for 24 hours and nothing has to be running at
the moment you send.

It takes text, links, forwarded messages, images and PDFs, recording who originally sent a
forwarded message, and it accepts messages from your own chat id only, capturing whatever you
send without ever replying to it.

## MCP server

Register it once and `brain_search`, `brain_read`, `brain_loops` and `brain_capture` become
available from any project rather than only from this folder, while the commands that write
stay here, where you can read a plan before it is applied. Registering it takes one command,
which is given in
[`docs/setup.md`](docs/setup.md#4-reach-it-from-your-other-projects-recommended).

## Escalation

A loop that has appeared in four briefs without an answer moves to the head of the next one
with its closing artifact already attached, because what stops a loop closing is rarely
forgetting but the cost of starting, so at that point the brief stops asking and does the work
instead.

| Loop | What arrives |
|---|---|
| You owe someone a message | the message, written |
| A deadline or birthday | the calendar entry |
| An unread document | a summary |
| An undecided question | the options, and what your notes say about each |

Everything here is drafted and nothing is ever sent, and `send_brief.py` takes no recipient
argument at all, reading its single destination once from configuration.

## Cost

There is nothing recurring to pay, because compiling and answering run on a Claude Code
subscription you already have, storage is files on disk, search is `grep`, phone capture uses
Telegram's free bot API, mail goes through your own account, and the MCP server runs locally.

The one thing not included is asking questions from a phone while the machine is off, which
would need a hosted API and is the only part of this that could not have been free.

## Notes

What it is made of, and what it does not do.

- Markdown in a git repository, readable in any editor you already use.
- Every claim cites the source it came from.
- `/unsource` removes a source along with every change it caused, which `git revert` cannot
  do, because later correct edits sit on top of the incorrect ones.
- No folder taxonomy, since a page exists only because some source created it.
- Everything stays on the machine.
- Portable with some work, in that the vault is markdown and the scripts are plain Python,
  though the nine commands are prose instruction files and moving to another agent would mean
  translating all of them.
- Nothing here does task entry, a vector store, a web interface, a continuously running
  process, sending messages, writing to a calendar, or unattended writes to `mem/` or a date.

## Changelog

### 2026-09-13
- Brief sections grouped by date. Entries are `####` under `###` date groups.
- Opening paragraph capped at two sentences.
- `Don't forget` restricted to things to read and things to buy.
- Nudges fire on the due date and on days 1, 3, 7 and 14 after it. Due tomorrow dropped.
- Nudges written to the brief's register, enforced on the loop `summary:` field. Dates are
  `Sunday 13 September`, not ISO. Entry titles are `h4`, matching the brief stylesheet.
- `Findings` section removed.
- Queue tag renamed to `[WEEKLY BRIEF]`.

### 2026-09-08
- Nightly pass compiles sources whose plan touches only `wiki/`, holds the rest. See Triage.
- `/ingest-all` drains Telegram before planning.
- `index.md` generated from `summary:` fields rather than hand-maintained.

### 2026-09-07
- Morning delivery moved to a Gmail Apps Script trigger. Writing depends on the machine,
  arrival does not.
- Brief reports how long since the last compile and how much is waiting.
- `/lint` reports entities and concepts past the promotion threshold with no page.
- `scripts/synthesis.py` counts promotion candidates from `mem/` names and `category:` values.

### 2026-08-31
- Loops carry `title:` and `summary:`. Nudges are built from those fields only.
- Nudges split into 07:00 and 19:30 windows.
- Overdue nudges fire on days 1, 3, 7 and 14 rather than daily.
- Brief dates are absolute. Entries carry a due date, not a capture date.
- Capture rejects labelled credentials.
- Delivery retries, waits for a network, and reports failures.

### 2026-08-30
- Added `/ingest-all`.
- Added the daily due-date check.
- Brief email renders as HTML.
- Renamed from `second-brain`.

## Docs

| | |
|---|---|
| [`docs/setup.md`](docs/setup.md) | Obsidian, MCP, email, Telegram, scheduling |
| [`docs/walkthrough.md`](docs/walkthrough.md) | Full setup with a worked example |
| [`docs/decisions.md`](docs/decisions.md) | Every design decision and how it was reached |
| [`docs/architecture-qa.md`](docs/architecture-qa.md) | The questions behind those decisions |
| [`docs/comparison.md`](docs/comparison.md) | Against GBrain, llm-wiki and others |
| [`docs/writing-style.md`](docs/writing-style.md) | The register used throughout |

## Terminology

| Term | Meaning |
|---|---|
| **vault** | `vault/`, a separate private git repository holding your content |
| **capture** | Recording something without interpreting it |
| **compile** | Reading a captured item and writing pages and loops from it. What `/ingest` does. |
| **source** | One captured item, and the page written from it |
| **loop** | Something you stated and did not resolve, extracted during compilation |
| **held** | A source the daily pass declined to compile without you |
| **surfaced** | How many briefs a loop has appeared in without an answer. At four it escalates. |
| **brief** | The periodic report |
| **nudge** | A reminder sent on a loop's due date, and on days 1, 3, 7 and 14 after it |
| **close** | Producing the artifact that finishes a loop, then filing it |
| **unsource** | Removing a source and reversing every change it caused |

## License

MIT. See [`LICENSE`](LICENSE).
