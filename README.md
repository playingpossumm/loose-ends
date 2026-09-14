# loose-ends

A second brain that records what you know and tracks what you said you would do.

It stores what you capture and answers questions about it, citing the source of every claim.
It also extracts the commitments buried in that material and reports them on a schedule until
each one is finished or dropped. Those commitments are called **loops**. You never type one;
they are written during compilation, from material captured for some other reason.

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

Open Claude Code in the project root. The commands exist only there. Then run `/bootstrap`,
an interview that fills `mem/` with your goals, projects, people and rules. It takes about
twenty minutes and can be resumed. Output is generic until it has run.

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

Capture and compilation are two steps. Capture writes what you send straight to `raw/` without
reading it, so it takes a second and cannot fail on something it does not understand.
Compilation reads that file later: it writes a page for the source, updates every existing
page the source touches, and opens a loop for anything you said you would do. One source can
touch up to fifteen pages.

```
capture → raw/ → compile ─┬→ wiki/  → ask
                          │
                          └→ loops/ → brief → nudge → close
```

### Two stores

`wiki/` holds what you have read. Delete it and a recompile of `raw/` rebuilds it exactly.
`mem/` holds your goals, projects, people and rules, which nothing can reconstruct, so the
compiler is not allowed to write there and proposes instead.

| | `wiki/` | `mem/` |
|---|---|---|
| Written by | the compiler | you |
| Rebuildable from `raw/` | yes | no |
| A contradiction is | a finding: keep both, record it | an error: reported for you to fix |
| The compiler may | write freely | propose only |

### Layout

The system and the content are separate repositories, which is what lets the system be public
while the vault stays private. Versioning the vault on its own makes each compilation a commit
you can inspect or undo.

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

Two mechanisms, both reading files on disk. `index.md` is a generated catalogue: every page
with its one-line summary, grouped by subject. A question is matched against that first, which
narrows a few hundred pages to a handful. `grep` then reads the full text of those pages for
anything the summary did not say.

Both sit behind one interface, so a vector store can replace them by changing one file. At a
few hundred pages there is nothing to gain from doing so.

## Automation

`/brief` writes a brief when you ask for one. The schedule below sends one without being
asked, which is the point: remembering to run `/brief` is the habit the brief exists to
replace.

There is no server and no API key. Everything runs as a Windows task on your own laptop,
which is what makes it free and is why the safeguards below exist.

```
python scripts/install_schedule.py --day FRI,SUN --time 19:00
```

That is the base case used here. It registers five tasks:

| Task | Runs | Does |
|---|---|---|
| `Capture` | daily 18:00 | drains Telegram, compiles what triage allows |
| `WeeklyBrief` | Fri and Sun 19:00 | writes the brief, queues it for the morning |
| `BriefCatchup` | Sat and Mon 06:00 | reruns a failed evening, or revises and re-queues |
| `NudgeMorning` | daily 07:00 | due today and overdue |
| `NudgeEvening` | daily 19:30 | the same, for loops marked `nudge: evening` |

So a brief arrives **Saturday 07:00 and Monday 07:00**. It is written the evening before, held
out of the inbox overnight by a Gmail filter, and released in the morning by an Apps Script
trigger, so writing depends on the laptop being on and arrival does not. Setup in
[`docs/setup.md`](docs/setup.md).

Every day and time above is an argument to `install_schedule.py`. Run it again with different
ones and the five tasks are replaced.

### Triage

The daily 18:00 pass compiles what it safely can without you and leaves the rest. It plans
each source first, then decides from what the plan would write:

| The plan writes | Then |
|---|---|
| `wiki/` only | compiled |
| a dated loop, or a change to a date already recorded | held |
| anything in `mem/` | held |
| a claim contradicting an existing page | held |
| something that reads more than one way | held |

A wrong `wiki/` page costs a regeneration. A wrong date costs a reminder that never arrives,
so dates wait for you.

Held sources stay in `raw/inbox/`, so whatever is still sitting there after a pass is what
waited. The brief lists each one and why. `/ingest-all` clears them.

A source that is both knowledge and commitment splits: the page is written, the loop is held.

### Reliability

A task only runs while the laptop is on, so the schedule assumes it will sometimes miss.

- Runs at 19:00, delivered 07:00, so the machine is awake when it matters
- Three Windows defaults overridden: battery, unplugging, missed runs
- Waits up to ten minutes for a network before starting
- Stops rather than half-running if the network never arrives
- Retries each stage, twice for capture and mail, once for the brief
- Repeats the full pass next morning if the evening failed
- Emails what broke and the command that fixes it

The middle five cover the nudges. A machine that was off runs its missed tasks at next
startup.

### Nudges

A short email that sends the thing back to you: the article you saved and never opened, with
its link; the date you set and have not closed. Otherwise a vault is where saved things go to
accumulate.

One goes out on the day a date arrives, then on days **1, 3, 7 and 14** after it passes while
the item is still open. Day 14 is marked as the last. Nothing due in the future appears; that
is the brief's job.

Most days it sends nothing, which is deliberate. A daily message that usually says nothing due
trains you to ignore the channel, and then the one that matters is ignored with it.

A loop sets `nudge: morning` or `nudge: evening` to pick its window, so reading arrives at
19:30 and anything needing an office open arrives at 07:00.

A nudge follows the brief's writing rules. The only model-authored text in one is the loop's
`summary:` field, so the register is enforced there, in the frontmatter contract in
[`CLAUDE.md`](CLAUDE.md): no repeat of the due date, which is printed beside the title anyway;
absolute dates; no em dashes; no clause arguing why the item matters.

## Capture

| Method | Use | Setup |
|---|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine | none |
| `/capture` | a link, a note, the current conversation | none |
| Obsidian Web Clipper | articles from a browser | 15 min |
| Telegram | anything, from a phone | 5 min |
| `brain_capture` over MCP | from any other project | one command |

Capture refuses labelled credentials before writing to disk: `password:`, `api key =`, seed
phrases, PEM private key blocks. The vault is a git repository, and a password is easier to
never store than to remove.

### Telegram

Telegram holds bot messages for 24 hours, so nothing needs to be running when you send. The
daily drain collects them inside that window.

Accepts text, links, forwarded messages, images and PDFs. Forwarded messages record their
original sender. Only your own chat id is accepted.

Capture only. The bot does not reply.

## MCP server

Without it the vault is readable only when its folder is open in Claude Code. Registering it
once makes search, read, list loops and capture available from any project, while the commands
that write stay in the project folder, where a plan can be reviewed before it is applied. One command, in
[`docs/setup.md`](docs/setup.md#4-reach-it-from-your-other-projects-recommended).

## Escalation

A loop that has appeared in four briefs without an answer moves to the head of the next one
with its closing artifact already attached. What stops a loop closing is rarely forgetting, it
is the cost of starting, so the brief stops asking and does the work:

| Loop | What arrives |
|---|---|
| You owe someone a message | the message, written |
| A deadline or birthday | the calendar entry |
| An unread document | a summary |
| An undecided question | the options, and what your notes say about each |

The system drafts and does not send. `send_brief.py` takes no recipient argument; the
destination is read once from configuration.

## Cost

Nothing recurring. Compiling and answering run on an existing Claude Code subscription.
Storage is files on disk, search is `grep`, phone capture is Telegram's free bot API, mail
goes through your own account, and the MCP server is local.

One capability is omitted because it would cost money: asking questions from a phone while
the machine is off.

## Notes

Properties worth knowing before relying on it.

- Markdown in a git repository. Any editor can read it.
- Every claim cites its source.
- `/unsource` removes a source and every change it caused. `git revert` does not solve this,
  because later correct edits sit on top of the incorrect ones.
- No folder taxonomy. Pages exist because a source created them.
- Files stay on the machine.
- Portable with work: the vault is markdown and the scripts are plain Python. The nine
  commands are prose instruction files, so moving to another agent means translating those.
- Not included: task entry, a vector store, a web interface, a continuously running process,
  sending messages, writing to a calendar, unattended writes to `mem/` or to a date.

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
| **held** | A source the nightly pass declined to compile without you |
| **surfaced** | How many briefs a loop has appeared in without an answer. At four it escalates. |
| **brief** | The periodic report |
| **nudge** | A reminder sent after a date passes |
| **close** | Producing the artifact that finishes a loop, then filing it |
| **unsource** | Removing a source and reversing every change it caused |

## License

MIT. See [`LICENSE`](LICENSE).
