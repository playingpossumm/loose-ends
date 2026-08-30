# loose-ends

A personal knowledge base that records what you read and tracks what you said you would do.

It answers two questions:

1. **What do I know about X?** Answers cite the source they came from.
2. **What did I say I would do and have not?** Reported on a schedule until you decide.

Most systems in this category do the first. This one also does the second, and sends the
work needed to finish each item along with the reminder.

It costs nothing to run. No API keys, no database, no server, no vector store.

---

## What it tracks

A **loop** is something you stated and did not resolve. You do not enter loops by hand. The
system extracts them from material you captured for other reasons:

- You said you wanted to read a paper. The file has sat unopened for six weeks.
- You said you would send someone a document. You did not send it.
- You recorded a birthday. No calendar entry exists.

Each loop is a file holding its status, a count of how often it has appeared unanswered, and
a reference to the source it came from. It appears in every brief until you mark it done,
killed, or deferred.

## What arrives with the reminder

After the fourth unanswered appearance, a loop moves to the top of the brief with the work
already drafted:

| Loop | What the brief includes |
|---|---|
| You owe someone a message | the drafted message, using facts from your notes |
| A deadline or birthday | the entry to paste into a calendar, and a note that none exists |
| An unread document | a summary, so you can judge it without opening the file |
| An undecided question | the options, and what your notes record about each |

The system drafts. It does not send. No code path exists that could send a message to a
third party, and the one script that sends mail takes no recipient argument — the address is
fixed in configuration, and passing another one is a syntax error.

---

## Capture

Everything captured lands in one folder, `vault/raw/inbox/`. Adding a new way to capture
does not change anything downstream.

| Method | Use | Setup |
|---|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine | none |
| `/capture` in Claude Code | a link, a note, the current conversation | none |
| Obsidian Web Clipper | articles and documents from a browser | 15 minutes |
| Telegram | anything, from a phone | 5 minutes |
| `brain_capture` over MCP | from any other project | one command |

### Telegram capture without a server

Sending to a personal assistant from a phone usually requires a server that runs constantly.
That is the recurring cost most comparable systems assume.

It is avoidable. Telegram holds messages for a bot for 24 hours, so nothing needs to be
running when you send:

```
Monday, away from the machine  →  send the bot three links and a note
Tuesday, at the machine        →  python scripts/telegram_capture.py --once
                                  four files appear in vault/raw/inbox/
                               →  /ingest-all
```

The script handles text, links, forwarded messages, images and PDFs. Forwarded messages
record who originally sent them. Only your own chat identifier is accepted, so nobody who
finds the bot can write to the vault.

This provides capture, not conversation. The bot does not answer questions. Answering
requires a model running constantly, which is the one part of this design that would cost
money, so it is left out.

---

## Cost

| Component | Why it is free |
|---|---|
| Compiling and answering | Runs on an existing Claude Code subscription |
| Storage | Markdown files on disk |
| Search | An index file and `grep` |
| Phone capture | Telegram's bot API |
| The brief | Sent through your own email account |
| Access from other projects | A local MCP server, started when needed |
| Reading the vault | Obsidian, which is free and optional |

Comparable systems assume a server at $7 to $24 a month, an API budget of roughly $15 to $40
a month at moderate volume, or a hosted vector database. None of that applies here.

One capability is omitted because it would cost money: asking questions from a phone while
the machine is off. Capture from a phone works and is free. Answering does not.

---

## Properties

**The files are yours.** Markdown in a git repository. Not a database, not an account, not a
proprietary format. Any text editor can read them.

**No dependency on one model.** The vault is files and a schema. A different model can read
it. Nothing here requires Claude except convenience.

**Claims are checkable.** Every claim cites the source it came from, so you can verify it
rather than trust it.

**Compilation reverses.** `/unsource` removes a source and every change it caused, across
each page it touched. Compiling one source writes to ten or fifteen pages; the published
descriptions of this pattern state the problem and offer no remedy. `git revert` does not
solve it either, because later correct edits sit on top of the incorrect ones.

**No filing system to maintain.** No folder taxonomy. Pages exist because a source created
them, and structure comes from citations. Maintenance cost is what ends most personal wikis.

**Private by default.** Files stay on the machine, and the vault is a separate private
repository. Content passes through the model when you ask it to read something, as in any
conversation, but the store itself is local.

---

## Design

```
capture → raw/ → compile ─┬→ wiki/  → ask     "what do I know about X"
                          │
                          └→ loops/ → brief → close
```

### Two stores

| | `wiki/` — what you read | `mem/` — who you are |
|---|---|---|
| Written by | the model | you |
| Rebuildable from `raw/` | yes | no |
| A contradiction is | a finding: keep both, flag it | an error: report it, you fix it |
| The compiler may | write freely | propose only |

The distinction matters. Two articles that disagree is useful information and both are kept.
A stated goal that conflicts with a stated commitment is an error and is reported for you to
resolve. Systems that treat these the same produce vague output.

### Layout

```
loose-ends/              the system. shareable.
├─ .claude/skills/       the nine commands
├─ mcp/ scripts/ docs/
├─ CLAUDE.md             the schema the model follows
├─ .env                  credentials. ignored by git.
└─ vault/                content. ignored here; a separate private repository.
   ├─ raw/               what you captured. never edited.
   ├─ wiki/              sources, entities, concepts, syntheses
   ├─ loops/             open, closed, dates
   ├─ mem/               profile, goals, projects, people, rules
   ├─ briefs/            one file per brief
   └─ index.md  log.md   the catalogue, and a record of what happened
```

Open the outer folder in Claude Code. Everything the commands write goes into `vault/`.
Separating the two allows the system to be public while the content stays private.
Versioning the vault separately means each compilation is a commit you can inspect or undo.

### The MCP server

Without it the vault is readable only when that one folder is open. The server lets any
Claude Code session read the vault from any project.

| Available anywhere | Only in the project folder |
|---|---|
| search, read, list open loops, capture | `/ingest`, `/brief`, `/close`, `/lint`, `/unsource`, `/bootstrap` |

Reading is safe from anywhere. Compiling writes to many pages at once and cannot be undone
with a keystroke, so it stays where the vault is visible.

### Search

At a few hundred pages an index file and `grep` are faster, cheaper and easier to inspect
than a vector store. Search sits behind one interface, so replacing it later is a
substitution rather than a rewrite. Vector search becomes worthwhile somewhere above 5,000
pages.

---

## Installing

```bash
git clone https://github.com/ArdellAlfatih/loose-ends.git
cd loose-ends
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ is bin/ on macOS and Linux
python scripts/init_vault.py
```

Make the vault a separate private repository, so the content has history and a backup:

```bash
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-vault --private --source=. --push
```

Open Claude Code in the project root — the commands exist only there — and run:

```
/bootstrap
```

It asks one question at a time and writes the answers to `mem/`: your work, goals, current
projects, the people involved, and the rules it must follow. It takes about twenty minutes
and can be stopped and resumed. Output is generic until it runs.

Then `/capture` something, `/ingest` it, and `/ask` a question.

Optional, and independent of each other: [Obsidian and the Web
Clipper](docs/setup.md#2-obsidian-optional-recommended), the [MCP
server](docs/setup.md#4-reach-it-from-your-other-projects-recommended), [email
delivery](docs/setup.md#5-email-delivery-for-the-brief), and [Telegram
capture](docs/setup.md#6-telegram-capture-from-your-phone-optional). Full instructions in
[`docs/walkthrough.md`](docs/walkthrough.md).

## Commands

| | |
|---|---|
| `/capture` | file a link, a document, a note, or the current conversation |
| `/ingest` | compile one source into pages and loops, after showing a plan |
| `/ingest-all` | compile the whole inbox, planned and approved once |
| `/ask` | answer a question with citations, and state what the vault does not cover |
| `/close` | produce the artifact that finishes one loop, then file it |
| `/brief` | the periodic report |
| `/lint` | check citations, links, orphans and stale pages |
| `/bootstrap` | the interview that fills `mem/` |
| `/unsource` | remove a source and reverse everything it caused |

## Not included

| Omitted | Reason |
|---|---|
| Task entry | You never type a task. Loops come from material captured for other reasons. A system that requires task entry is a task manager. |
| Vector store or graph database | Justified above 100,000 pages, not hundreds. |
| A web interface | Claude Code operates it. Obsidian reads it. |
| A constantly running process | A weekly schedule does not need one. |
| Sending messages | The system drafts. You send. |
| Writing to a calendar | The brief reports that no entry exists. You create it. |

## Status

The system is complete and has been in use for one week. Its central claim — that reminders
delivered with the work attached get acted on — is an argument, not a result.

The measure is **nudge precision**: of the loops reported each period, how many were worth
reporting. Below about 30 per cent the design is wrong. Two further conditions end the
project: nothing entering `raw/` for three consecutive weeks, which means capture is too
inconvenient; or finding yourself editing the wiki by hand, which means the compiler failed.

A comparison with GBrain, llm-wiki and similar systems, including where they are better, is
in [`docs/comparison.md`](docs/comparison.md). The design decisions and how they were reached
are in [`docs/decisions.md`](docs/decisions.md), and the questions behind them in
[`docs/architecture-qa.md`](docs/architecture-qa.md).

## License

MIT. See [`LICENSE`](LICENSE).
