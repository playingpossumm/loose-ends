# loose-ends

A second brain that records what you know and tracks what you said you would do.

It stores a friend's birthday, an article you found worth keeping, a quote you want held
verbatim, and a deadline three weeks out. Ask it about any of that later and it answers with
the source of every claim attached, so you can check the answer rather than trust it.

Most systems stop at storage. You put information in, it becomes something you can pull back
out, and then it dies there because nothing ever acts on it. This one reads what you captured
and extracts the commitments buried inside it, then reports those back on a schedule until
each one is finished or deliberately dropped. A periodic brief tells you what is due this
week, a nudge returns to the article you saved and never opened, and a reminder arrives
before the document you have to submit is late.

Those extracted commitments are called **loops**, and you never type one. They are written
during compilation, from material you captured for some other reason. After a loop has
appeared four times without an answer it moves to the top of the brief with the work already
drafted, so what arrives is the message itself rather than a reminder to write it.

**Requirements:** Claude Code, and a machine you use most days. Nothing else — no API keys,
no database, no server, no vector store, and no monthly cost.

---

## Installation

```bash
git clone https://github.com/playingpossumm/loose-ends.git
cd loose-ends
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ is bin/ on macOS and Linux
python scripts/init_vault.py
```

The vault should be its own private repository, so that your content has a history and a
backup independent of the system that reads it:

```bash
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-vault --private --source=. --push
cd ..
```

Open Claude Code in the project root. The commands exist only there, not in `vault/` and not
in your home directory; type a forward slash to confirm they loaded.

Then run `/bootstrap`. It asks one question at a time about your work, your goals, the
projects you have running, the people involved in them, and the rules the system must
follow, and it writes the answers into `mem/`. It takes about twenty minutes, and it can be
stopped and resumed. Until it has run, everything the system produces is generic.

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

## Operation

```
capture something  →  /ingest  →  /ask, or wait for the brief  →  /close
```

Capture is deliberately separated from compilation, because the two have opposite
requirements. Capture must be fast enough that you do it without thinking, and it must never
fail, so it records material without interpreting it — move a file into `vault/raw/inbox/`,
run `/capture`, click the browser extension, or message the Telegram bot, and all four write
to the same folder. Compilation is where the reading happens, and a single source can touch
ten or fifteen pages at once, so it shows you its plan and waits for approval. `/ingest`
handles one source; `/ingest-all` handles the whole inbox in one pass and can therefore see
across sources, which matters because three notes about the same thing should produce one
loop rather than three.

Captured material is searchable immediately but produces no pages and no loops until it is
compiled. To stop anything sitting unseen, the brief counts what is waiting and reports
anything older than two weeks.

### Automation

Four things run without you. Telegram messages are drained into `vault/raw/inbox/` once a
day, browser clippings land there the moment you click, the brief is written and emailed on
your schedule with a retry the following morning, and nudges go out at 07:00 and 19:30,
silent unless something is due. Compiling is the single exception, for the reason given
above.

Scheduling uses Windows Task Scheduler. Give it the evening **before** the morning you intend
to read the brief:

```
python scripts/install_schedule.py --day FRI,SUN --time 19:00
```

That registers five tasks: the brief on the evening before each day you read it, a second
attempt the following morning, a daily capture from Telegram, and the two daily nudges. Use
`--nudge-morning` and `--nudge-evening` to move the last two.

### Reliability

The system is free because it runs on your own laptop, which means it only runs when your
laptop is on. That is the trade: no server, and therefore no guarantee that the machine is
awake at the hour a brief or a nudge is due. Six behaviours cover it, each addressing a way
the one before it fails.

- **19:00, the evening before you read it.** A morning task has to wake a sleeping laptop,
  which needs Windows wake timers, and Windows disables those on battery.
- **Three Windows task defaults overridden.** Tasks otherwise refuse to start on battery,
  abort when unplugged, and skip a missed run permanently.
- **Up to ten minutes waiting for a network.** Waking a machine starts the task before Wi-Fi
  has associated.
- **A stop rather than a half-run.** Every stage needs a connection and so does the failure
  email, so continuing would produce nothing but misleading errors.
- **A retry on each stage**, twice for capture and mail and once for the brief.
- **The full pass again the next morning**, for any reason at all that the evening run did
  not complete.

The middle four apply to the nudges as well, since both run through the same script. The
first and last are specific to the brief, which is weekly and can therefore afford a second
attempt; a nudge that fails outright is instead picked up by the next morning's run, where
the item now counts as overdue.

If they all fail, the system emails you what broke, the last 25 lines of the log, the
command to run by hand, and what to check, and every attempt appends to `autopilot.log`
whether or not that mail got out.

If the machine was simply off, nothing is lost and nothing is retried. Windows runs the
missed task the next time you start the laptop, so the brief arrives late rather than never.

The morning task has a second job, which is to recover the one thing an evening brief gives
up. It drains Telegram and resends only when something captured overnight changes what you
would actually do, such as a new deadline or a loop now resolved, and otherwise sends
nothing. A normal week therefore produces one email.

### Nudges

The brief reports what is coming, but a deadline also needs saying on the day itself. Nudges
go out twice a day and send nothing at all unless something is due, because a reminder is
only useful at the hour you can act on it.

- **07:00** carries what is due today and what is overdue, so the working day is still in
  front of it.
- **19:30** carries what is due tomorrow, while there is still an evening to prepare in.

The split follows the due date by default, and a loop overrides it with `nudge: morning` or
`nudge: evening` when its nature disagrees. An article to read is an evening item whatever
its date; a booking that needs an office to be open is a morning one.

The silence between them is the point. A daily message that usually says "nothing due"
trains you to ignore the channel, and the one that matters is then ignored with the rest. An
overdue item stops nudging after 14 days and appears only in the brief, where it is put as a
decision rather than a reminder: drop it, set a new date, or do it now. Reminding
indefinitely is the same failure by a slower route.

## Capture

| Method | Use | Setup |
|---|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine | none |
| `/capture` | a link, a note, the current conversation | none |
| Obsidian Web Clipper | articles from a browser | 15 minutes |
| Telegram | anything, from a phone | 5 minutes |
| `brain_capture` over MCP | from any other project | one command |

Capture refuses labelled credentials before writing anything to disk. A message containing
`password:`, `api key =`, a seed phrase, or a PEM private key block is rejected and nothing
is stored. The test errs toward refusing, because losing one note costs less than storing one
password in a git repository.

### Telegram

Messaging an assistant from a phone would normally require a server running continuously,
which is the recurring cost most comparable systems assume. Telegram holds bot messages for
24 hours, so nothing has to be running at the moment you send:

```
Monday, away from the machine  →  send the bot three links and a note
Tuesday, at the machine        →  python scripts/telegram_capture.py --once
                                  four files appear in vault/raw/inbox/
                               →  /ingest-all
```

It accepts text, links, forwarded messages, images and PDFs. A forwarded message records its
original sender, so a claim relayed from someone else is never attributed to you, and only
your own chat identifier is accepted, so nobody who finds the bot can write into the vault.

This provides capture and not conversation; the bot does not reply. Answering would require a
model running continuously, which is the one part of this design that would cost money.

## MCP server

Without the MCP server the vault is readable only when its folder is open in Claude Code.
Registering it once makes searching, reading, listing open loops and capturing available from
any project on the machine, while the commands that write stay in the project folder:
`/ingest`, `/brief`, `/close`, `/lint`, `/unsource` and `/bootstrap`.

The division follows from risk rather than convenience. Reading is safe from any directory,
so it is exposed everywhere; compiling and deciding stay where the vault is visible and where
a plan can be reviewed before it is applied. Setup is a single command, documented in
[`docs/setup.md`](docs/setup.md#4-reach-it-from-your-other-projects-recommended).

## Escalation

Every loop carries a count of how many briefs it has appeared in without being answered. The
count exists because repetition on its own does not change behaviour, and a reminder that has
been ignored three times is unlikely to succeed on the fourth attempt in the same form. On
the fourth appearance the loop is promoted to the head of the brief and its closing artifact
is generated alongside it.

- If you owe someone a message, it arrives written, drawing on facts the vault already holds
  about them and about what you promised.
- If you recorded a deadline or a birthday, it arrives as a calendar entry, ready to paste.
- If you saved a document and never opened it, it arrives summarised closely enough to judge
  without opening the file.
- If you left a question undecided, it arrives with the options, and with what your notes
  record about each of them.

The premise throughout is that what prevents a loop from closing is rarely forgetting, and
usually the cost of starting.

The system drafts and it does not send. The single script that transmits mail accepts no
recipient argument: the destination is read once from configuration, and passing another one
is a syntax error rather than a policy violation. No code path exists by which a message
reaches a third party.

## Cost

Nothing in the system carries a recurring charge. Compiling and answering run on a Claude
Code subscription you already hold. Storage is markdown files on disk and search is an index
file and `grep`, so neither is a service. Phone capture uses Telegram's bot API, the brief
goes out through your own email account, the MCP server is local and starts only when
something asks for it, and Obsidian, which is optional, is free.

Comparable systems assume a server at $7 to $24 a month, an API budget of roughly $15 to $40
a month at moderate volume, or a hosted vector database.

One capability is omitted because it would cost money, which is asking questions from a phone
while the machine is off. Capture from a phone works and is free; answering does not.

## Architecture

```
capture → raw/ → compile ─┬→ wiki/  → ask
                          │
                          └→ loops/ → brief → close
```

### Storage model

The vault is divided into two stores, which are treated differently because they fail
differently. `wiki/` holds what the compiler has written from material you captured, and
because it can be rebuilt from `raw/` in full, the compiler writes into it without asking.
`mem/` holds what you have told the system about yourself, and nothing can reconstruct it if
it is lost, so the compiler may only propose changes there and never apply them.

| | `wiki/` — what you read | `mem/` — who you are |
|---|---|---|
| Written by | the compiler | you |
| Rebuildable from `raw/` | yes | no |
| A contradiction is | a finding: keep both, record it | an error: report it, you fix it |
| The compiler may | write freely | propose only |

The distinction extends to how contradiction is handled. Two articles that disagree
constitute a finding, and both are kept with the conflict recorded. A stated goal that
contradicts a stated commitment is an error, and it is reported for you to resolve rather
than quietly reconciled. Systems that collapse these two cases into one produce output that
grows vaguer the more they hold.

### Directory layout

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

The vault holds four folders, in a strict order of authority. `raw/` holds what you captured,
unchanged, and is never edited. `wiki/` holds the compiled pages and can be rebuilt from
`raw/` at any time. `loops/` holds open, closed and dated items, all written by the compiler.
`mem/` holds your profile, goals, projects, people and rules, and is the one folder you write
yourself.

Separating the system from the vault is what allows the system to be public while the content
stays private. Versioning the vault on its own means that each compilation is a commit you
can inspect, and one you can undo.

### Search

At a few hundred pages, an index file and `grep` are faster, cheaper and easier to inspect
than a vector store, and they fail in ways you can see. Search sits behind a single interface,
so replacing it later is a substitution rather than a rewrite. Vector search becomes
worthwhile somewhere above 5,000 pages.

## Properties

**The files are yours.** Markdown in a git repository, readable by any text editor.

**Claims are checkable.** Every claim cites its source, so you can verify it instead of
trusting it.

**Compilation reverses.** `/unsource` removes a source and every change it caused. This
matters because compiling one source writes to ten or fifteen pages, and `git revert` does
not solve it: later correct edits sit on top of the incorrect ones. Published descriptions of
this pattern state the problem and offer no remedy.

**There is no filing system to maintain.** No folder taxonomy and no tags to keep consistent.
Pages exist because a source created them, and the structure comes from citations.

**It is private by default.** Files stay on the machine. Content passes through the model when
you ask it to read something, as in any conversation, but the store is local.

**It is portable, with some work.** The vault is markdown and the scripts are plain Python, so
neither needs Claude. The MCP server speaks a standard protocol and works with any client
that supports it. The nine commands are the part written for Claude Code, and they are prose
instruction files rather than code, so moving to another agent means renaming `CLAUDE.md` to
whatever that agent reads and translating those nine files. Your content is never the thing
that has to move.

Several things are absent deliberately:

- **Task entry.** You never type a task. Loops come from material captured for other reasons,
  and a system that requires task entry is a task manager.
- **A vector store or graph database.** Justified above 100,000 pages, not hundreds.
- **A web interface.** Claude Code operates it and Obsidian reads it.
- **A continuously running process.** A weekly schedule does not need one.
- **Sending messages, and writing to a calendar.** The system drafts and produces the entry.
  You send it and you create it.

## Status

The system is complete and has been in use for one week. Its central claim, that reminders
delivered with the work already attached get acted on where bare reminders do not, is an
argument rather than a result.

The measure is **nudge precision**: of the loops reported in each period, how many were worth
reporting. Below roughly 30% the design is wrong. Two further conditions end the project.
Nothing entering `raw/` for three consecutive weeks means capture is too inconvenient, and
finding yourself editing the wiki by hand means the compiler has failed at the only job it
has.

## Updates

Newest first. The reasoning behind each one is in the commit that made it.

**31 August 2026, evening.** Running a nudge for the first time showed it followed none of
the rules the brief follows. It pasted the opening lines of the loop page into the email,
which is the compiler's own working — source paths, ranking arguments, and the user narrated
in the third person, so one reminder read "His own date, stated 2026-08-31" — and then cut
it off at a character count, mid-word. Loops now carry `title:` and `summary:`, two fields
written for a reader rather than for the vault, and the nudge is built from those alone.

Nudges also moved from one daily send to two. **07:00** carries what is due today and what is
overdue, with the working day still in front of it; **19:30** carries what is due tomorrow,
while there is an evening left to prepare in. A loop overrides the split with `nudge:
morning` or `nudge: evening` when its nature disagrees with its date.

The reliability work of that morning turned out not to cover the nudge at all. It was
scheduled to run its own script directly, bypassing the network wait, the retries and the
failure email, so a laptop that woke before its Wi-Fi killed the reminder in silence. It now
runs the same path as everything else.

**31 August 2026, morning.** The brief was rewritten after a week of real output. Two
sections that reported on the system rather than on your work were cut, and a `Don't forget`
section took their place to resurface things captured and never returned to. Entries carry a
due date rather than the date they were captured, anything with a URL is linked from its
title, and every date is absolute — the brief is read across a whole week, so "tomorrow"
means something different on Thursday from what it meant on Monday. Capture began refusing
labelled credentials after a bank password reached the vault and had to be removed. Delivery
was rebuilt in layers, described under [Reliability](#reliability), following a brief that
was lost to a laptop that woke before its Wi-Fi did.

**30 August 2026.** Added `/ingest-all`, which compiles the whole inbox under one approval
and can therefore see across sources, so three notes about the same thing produce one loop
rather than three. Added a daily due-date check that emails only when something is overdue,
due today, or due tomorrow, and which stops at 14 days so the brief can force a decision
instead. The brief email began rendering as HTML rather than raw markdown. The project was
renamed from `second-brain`, a name shared with thousands of repositories that said nothing
about what this one does.

## Terminology

| Term | Meaning |
|---|---|
| **vault** | The folder holding your content: `vault/`. A separate private git repository. |
| **capture** | Recording something without interpreting it. Fast, and it never fails. |
| **compile** | Reading a captured item and writing pages and loops from it. Where the work happens, and the only step that cannot be undone with one keystroke. |
| **source** | One captured item, and the page written from it. |
| **loop** | Something you stated and did not resolve. You do not type these; they are extracted during compilation. |
| **surfaced** | The count on each loop of how many times it has appeared in a brief without an answer. At four it is promoted. |
| **brief** | The periodic report. What is due, what is coming, and what you captured and forgot. |
| **nudge** | A short email sent on the day a loop is due, at 07:00 or 19:30. Silent otherwise. |
| **close** | Producing the artifact that finishes a loop, then marking it done, dropped, or deferred. |
| **unsource** | Removing a source and reversing every change it caused across every page. |

## Further reading

| | |
|---|---|
| [`docs/walkthrough.md`](docs/walkthrough.md) | Full setup, with a worked example of a month of use |
| [`docs/setup.md`](docs/setup.md) | Obsidian, MCP, email, Telegram, scheduling |
| [`docs/comparison.md`](docs/comparison.md) | Against GBrain, llm-wiki and others, including where they are better |
| [`docs/decisions.md`](docs/decisions.md) | Every design decision and how it was reached |
| [`docs/architecture-qa.md`](docs/architecture-qa.md) | The questions behind those decisions |
| [`docs/writing-style.md`](docs/writing-style.md) | The register everything here is written in, as a prompt you can reuse |

## License

MIT. See [`LICENSE`](LICENSE).
