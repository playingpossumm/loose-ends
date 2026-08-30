# loose-ends

A personal knowledge base that records what you read and tracks what you said you would do
and have not done.

You capture things: articles, documents, notes, messages to yourself. It compiles them into
linked pages you can search, and extracts anything you stated but did not finish.

```
"I want to read this paper."     The file has sat unopened for six weeks.
"I'll send them the document."   You did not.
A birthday went in.              No calendar entry exists.
```

Those are **loops**. They appear in a report on a schedule until you decide what to do with
them. After the fourth unanswered appearance the report includes the work needed to finish
them: the drafted message, a summary of the unread document, the calendar entry to paste.

Two things it does, then:

1. **Answers questions about what you have read**, citing the source of every claim.
2. **Reports what you have not finished**, with the work to finish it attached.

**What you need:** Claude Code, and a machine you use most days. Nothing else — no API keys,
no database, no server, no vector store, and no monthly cost.

---

## Terms

| Term | Meaning |
|---|---|
| **vault** | The folder holding your content: `vault/`. A separate private git repository. |
| **capture** | Recording something without interpreting it. Fast, and it never fails. |
| **compile** | Reading a captured item and writing pages and loops from it. This is where the work happens, and it is the only step that cannot be undone with one keystroke. |
| **source** | One captured item, and the page written from it. |
| **loop** | Something you stated and did not resolve. You do not type these; they are extracted during compilation. |
| **surfaced** | A count on each loop of how many times it has appeared in a brief without an answer. At four it moves to the top. |
| **brief** | The periodic report. What is due, what needs deciding, and the drafted work to finish it. |
| **close** | Producing the artifact that finishes a loop, then marking it done, dropped, or deferred. |
| **unsource** | Removing a source and reversing every change it caused across every page. |

### The four folders

| | Holds | Written by |
|---|---|---|
| `vault/raw/` | what you captured, unchanged | capture |
| `vault/wiki/` | compiled pages: sources, entities, concepts | the compiler |
| `vault/loops/` | open, closed, and dated items | the compiler |
| `vault/mem/` | your profile, goals, projects, people, rules | you |

`raw/` is never edited. `wiki/` can be rebuilt from `raw/` at any time. `mem/` cannot be
rebuilt, so the compiler proposes changes to it and never writes them.

---

## Install

```bash
git clone https://github.com/playingpossumm/loose-ends.git
cd loose-ends
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ is bin/ on macOS and Linux
python scripts/init_vault.py
```

Make the vault a separate private repository, so your content has history and a backup:

```bash
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-vault --private --source=. --push
cd ..
```

Open Claude Code in the project root. The commands exist only there — not in `vault/`, and
not in your home directory. Type a forward slash to confirm they loaded.

Then run `/bootstrap`. It asks one question at a time about your work, goals, current
projects, the people involved, and the rules it must follow, and writes the answers to
`mem/`. It takes about twenty minutes and can be stopped and resumed. Output is generic
until it runs.

## Commands

| | |
|---|---|
| `/capture` | Record a link, file, note, or the current conversation. |
| `/ingest` | Compile one source. Shows its plan before writing. |
| `/ingest-all` | Compile the whole inbox, planned and approved once. |
| `/ask` | Answer a question with citations, and state what the vault does not cover. |
| `/close` | Produce the artifact that finishes one loop, then file the loop. |
| `/brief` | Write the periodic report. |
| `/lint` | Check citations, links, orphan pages, stale claims. Run monthly. |
| `/bootstrap` | The interview that fills `mem/`. |
| `/unsource` | Remove a source and reverse every change it caused. |

## Using it

```
capture something  →  /ingest  →  /ask, or wait for the brief  →  /close
```

**Capture whenever.** Move a file into `vault/raw/inbox/`, run `/capture`, click the browser
extension, or message the Telegram bot. All four write to the same folder.

**Compile when you sit down.** `/ingest` handles one source and shows a plan first;
`/ingest-all` handles the inbox in one pass. Captured items are searchable straight away but
produce no loops and no links until compiled.

**Ask any time.** `/ask` in the project folder, or plain language in any other project once
the MCP server is registered.

**Read the brief when it arrives**, then `/close` whatever you decide to act on.

### What runs on its own

| Step | Automatic |
|---|---|
| Telegram messages into `vault/raw/inbox/` | yes, on a daily schedule |
| Browser clippings into `vault/raw/inbox/` | yes, when you click |
| Compiling captured items | **no** — you run `/ingest` |
| Writing and emailing the brief | yes, on your schedule |

Compilation stays manual because it writes to ten or fifteen pages at once. It shows a plan
and waits. The brief counts anything left uncompiled and reports it, so nothing sits unseen.

Scheduling uses Windows Task Scheduler:

```
python scripts/install_schedule.py --cadence weekly --day SAT --time 08:00
```

Tasks run on battery, survive being unplugged, and can wake a sleeping machine. A machine
that is fully off runs the task at next startup, so the brief arrives late rather than not
at all.

## Capture methods

| Method | Use | Setup |
|---|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine | none |
| `/capture` | a link, a note, the current conversation | none |
| Obsidian Web Clipper | articles from a browser | 15 minutes |
| Telegram | anything, from a phone | 5 minutes |
| `brain_capture` over MCP | from any other project | one command |

### Telegram without a server

Messaging an assistant from a phone normally requires a server running constantly, which is
the recurring cost most comparable systems assume.

Telegram holds bot messages for 24 hours, so nothing needs to be running when you send:

```
Monday, away from the machine  →  send the bot three links and a note
Tuesday, at the machine        →  python scripts/telegram_capture.py --once
                                  four files appear in vault/raw/inbox/
                               →  /ingest-all
```

It handles text, links, forwarded messages, images and PDFs. Forwarded messages record the
original sender, so a claim relayed from someone else is not attributed to you. Only your own
chat identifier is accepted, so nobody who finds the bot can write to the vault.

This provides capture, not conversation. The bot does not reply. Answering requires a model
running constantly, which is the one part of this design that would cost money.

## Reading it from other projects

Without the MCP server the vault is readable only when its folder is open. Registering it
once lets any Claude Code session read the vault from any project.

| Available anywhere | Only in the project folder |
|---|---|
| search, read, list open loops, capture | `/ingest`, `/brief`, `/close`, `/lint`, `/unsource`, `/bootstrap` |

Reading is safe from any directory. Compiling and deciding stay where the vault is visible.
Setup is one command, in [`docs/setup.md`](docs/setup.md#4-reach-it-from-your-other-projects-recommended).

---

## What arrives with a reminder

After the fourth unanswered appearance, a loop moves to the top of the brief with the work
already drafted:

| Loop | What the brief includes |
|---|---|
| You owe someone a message | the drafted message, using facts from your notes |
| A deadline or birthday | the entry to paste into a calendar, and a note that none exists |
| An unread document | a summary, so you can judge it without opening the file |
| An undecided question | the options, and what your notes record about each |

The system drafts. It does not send. The one script that sends mail takes no recipient
argument: the address is fixed in configuration, and passing another one is a syntax error.
No code path exists that could send a message to a third party.

## What it costs

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
a month at moderate volume, or a hosted vector database.

One capability is omitted because it would cost money: asking questions from a phone while
the machine is off. Capture from a phone works and is free. Answering does not.

## How it works

```
capture → raw/ → compile ─┬→ wiki/  → ask
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

Two articles that disagree is useful information, and both are kept. A stated goal that
conflicts with a stated commitment is an error and is reported for you to resolve. Systems
that treat these the same produce vague output.

### Layout

```
loose-ends/              the system. shareable.
├─ .claude/skills/       the nine commands
├─ mcp/ scripts/ docs/
├─ CLAUDE.md             the schema the model follows
├─ .env                  credentials. ignored by git.
└─ vault/                content. ignored here; a separate private repository.
   ├─ raw/ wiki/ loops/ mem/ briefs/
   └─ index.md  log.md   the catalogue, and a record of what happened
```

Separating the two allows the system to be public while the content stays private.
Versioning the vault on its own means each compilation is a commit you can inspect or undo.

### Search

At a few hundred pages an index file and `grep` are faster, cheaper and easier to inspect
than a vector store. Search sits behind one interface, so replacing it later is a
substitution rather than a rewrite. Vector search becomes worthwhile above roughly 5,000
pages.

## Properties

**The files are yours.** Markdown in a git repository. Any text editor can read them.

**Portable, with some work.** The vault is markdown and the scripts are plain Python, so
neither needs Claude. The MCP server speaks a standard protocol and works with any client
that supports it. The nine commands are the part written for Claude Code, and they are prose
instruction files rather than code — moving to another agent means renaming `CLAUDE.md` to
whatever that agent reads and translating those nine files. Your content is never the thing
that has to move.

**Claims are checkable.** Every claim cites its source, so you can verify it rather than
trust it.

**Compilation reverses.** `/unsource` removes a source and every change it caused. Compiling
one source writes to ten or fifteen pages; published descriptions of this pattern state the
problem and offer no remedy. `git revert` does not solve it either, because later correct
edits sit on top of the incorrect ones.

**No filing system to maintain.** No folder taxonomy. Pages exist because a source created
them, and structure comes from citations.

**Private by default.** Files stay on the machine. Content passes through the model when you
ask it to read something, as in any conversation, but the store is local.

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

## Further reading

| | |
|---|---|
| [`docs/walkthrough.md`](docs/walkthrough.md) | Full setup, with a worked example of a month of use |
| [`docs/setup.md`](docs/setup.md) | Obsidian, MCP, email, Telegram, scheduling |
| [`docs/comparison.md`](docs/comparison.md) | Against GBrain, llm-wiki and others, including where they are better |
| [`docs/decisions.md`](docs/decisions.md) | Every design decision and how it was reached |
| [`docs/architecture-qa.md`](docs/architecture-qa.md) | The questions behind those decisions |

## License

MIT. See [`LICENSE`](LICENSE).
