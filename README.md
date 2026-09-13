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
| `/ingest-all` | Drain Telegram, then compile the inbox under one approval. |
| `/ask` | Answer a question with citations, and state what the vault does not cover. |
| `/close` | Produce the artifact that finishes a loop, then file it. |
| `/brief` | Write the periodic report. |
| `/lint` | Check citations, links, orphans, stale claims, synthesis gaps. |
| `/bootstrap` | The interview that fills `mem/`. |
| `/unsource` | Remove a source and reverse every change it caused. |

## Architecture

Capture and compilation are separate steps because they have opposite requirements. Capture
has to be fast enough that you do it without thinking and must never fail, so it records
without interpreting. Compilation does the reading, and a single source can touch fifteen
pages.

```
capture → raw/ → compile ─┬→ wiki/  → ask
                          │
                          └→ loops/ → brief → nudge → close
```

### Two stores

Knowledge about the world and knowledge about you fail differently, so they follow different
rules. `wiki/` can be thrown away and rebuilt; `mem/` cannot be reconstructed by anything.

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

At a few hundred pages an index file and `grep` are faster and easier to inspect than a vector
store, and they fail visibly. Search sits behind one interface, so replacing it is a
substitution rather than a rewrite. A vector store becomes worthwhile above roughly 5,000
pages.

## Automation

Nothing pushes you until these are registered, which leaves you remembering to run `/brief`,
the exact habit it exists to replace.

```
python scripts/install_schedule.py --day FRI,SUN --time 19:00
```

Five Windows tasks:

| Task | Runs | Does |
|---|---|---|
| `Capture` | daily 18:00 | drains Telegram, compiles what triage allows |
| `WeeklyBrief` | your days, 19:00 | writes the brief, queues it for morning delivery |
| `BriefCatchup` | next day 06:00 | recovers a failed run, or revises and re-queues |
| `NudgeMorning` | daily 07:00 | overdue items, silent otherwise |
| `NudgeEvening` | daily 19:30 | overdue items marked `nudge: evening` |

The brief is written in the evening and delivered at 07:00 by a Gmail Apps Script trigger, so
writing depends on the machine and arrival does not. Setup in
[`docs/setup.md`](docs/setup.md).

### Triage

Compiling every source by hand is friction, and compiling every source automatically risks
a wrong date. The nightly pass splits the difference: a wrong `wiki/` page costs a
regeneration, while a wrong date costs a reminder that never arrives, so only the first kind
is written unattended. The test is which store the plan writes to.

| The plan writes | Then |
|---|---|
| `wiki/` only | written |
| a dated loop, or a change to a recorded date | held |
| anything in `mem/` | held |
| a claim contradicting an existing page | held |
| something that reads more than one way | held |

Held sources stay in `raw/inbox/`, so whatever remains after a pass is what waited. The brief
reports each one with its reason. `/ingest-all` settles them.

Where a source is both knowledge and commitment, the source page is written and the loop is
held.

### Reliability

The system is free because it runs on your own laptop, which means it only runs when the
laptop is on. That is the trade for having no server, and these cover it.

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

Silence is the point. A daily message that usually says nothing due trains you to ignore the
channel, and then the one that matters is ignored with it.

Sent only when a date has passed and the item is still open, on days **1, 3, 7 and 14** past
it. Day 14 is marked as the last. Items due today and tomorrow appear in the brief, not here.

A loop sets `nudge: morning` or `nudge: evening` to choose its window.

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

What stops a loop closing is rarely forgetting. It is the cost of starting, so after four
unanswered appearances the brief stops asking and does the work instead.

A loop that has appeared in four briefs without an answer moves to the head of the brief with
its closing artifact attached:

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
- Nudges fire only after a date passes. Items due today and tomorrow appear in the brief only.
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
