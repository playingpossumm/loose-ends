# Walkthrough

There is no application to install. The system is a folder of text files operated through
Claude Code. This page lists what to type, in order.

## The interface

No graphical interface was built. Two programs do the work:

| | |
|---|---|
| **Claude Code** | Where you operate the system. You type `/capture`, `/ask`, `/brief`, and it edits the files. |
| **Obsidian** | Displays the same folder. Optional. Nothing depends on it. |

The store is markdown files on disk. Nothing is uploaded. You place files in a folder on
your own machine.

---

## Setup

### 1. Install

```bash
git clone https://github.com/playingpossumm/loose-ends.git
cd loose-ends
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ is bin/ on macOS and Linux
python scripts/init_vault.py
```

The last command creates `vault/`, which holds your content. The repository ignores it.

### 2. Make the vault a private repository

```bash
cd vault
git init && git add -A && git commit -m "empty vault"
gh repo create my-vault --private --source=. --push
cd ..
```

Keep it private. It holds your goals, projects, the people you work with, and everything you
capture.

It also provides an undo. One `/ingest` writes to ten or fifteen pages; git shows exactly
what changed and reverses it if the source was misread.

### 3. Open Claude Code in the project root

Not in `vault/`, and not in your home directory. The commands exist only in the outer folder.

To confirm, type a forward slash. You should see:

```
/ask  /bootstrap  /brief  /capture  /close  /ingest  /ingest-all  /lint  /unsource
```

If nothing appears, the directory is wrong. This is the most common setup error.

### 4. Fill in who you are

```
/bootstrap
```

It asks one question at a time about your work, goals, current projects, the people involved,
and the rules it must follow. It takes about twenty minutes and can be stopped and resumed;
each section is written as it finishes.

Answer specifically. Vague answers produce vague output for as long as the file stands.

### 5. Capture something

```
/capture https://example.com/an-article
```

Or move a file into `vault/raw/inbox/`. Capture records the item without interpreting it.

Every capture method writes to the same folder:

| Method | Use |
|---|---|
| Move a file into `vault/raw/inbox/` | anything on the machine |
| `/capture` | a link, a note, the current conversation |
| Obsidian Web Clipper | articles from a browser |
| Telegram | anything, from a phone |
| `brain_capture` over MCP | from any other project |

### 6. Compile it

```
/ingest
```

The command reads the source, checks existing pages, writes and links new ones, and extracts
anything you said you would do.

It compiles one source per run and shows its plan first:

```
Plan — 6 pages:
  new     wiki/sources/2026-08-25-retrieval-survey
  new     wiki/concepts/hybrid-retrieval
  update  wiki/entities/bm25              (+1 source)
  loop    "read the retrieval survey" — also stated 12 August
  flag    contradicts wiki/concepts/reranking on latency

Proceed?
```

Read the plan for the first ten sources. Correcting a misreading at this point is cheaper
than reversing fifteen pages afterwards.

Use `/ingest-all` to compile the whole inbox with one approval. Prefer `/ingest` until you
have seen the compiler handle twenty or so sources correctly.

---

## Commands

| | |
|---|---|
| `/capture` | Record a link, file, note or the current conversation. No interpretation. |
| `/ingest` | Compile one source. Writes pages, links them, extracts loops, flags contradictions. |
| `/ingest-all` | Compile the whole inbox, planned and approved once. |
| `/ask` | Answer a question with citations, and state what the vault does not cover. |
| `/close` | Produce the artifact that finishes one loop, then file the loop. |
| `/brief` | The periodic report. |
| `/lint` | Check citations, links, orphan pages and stale claims. Run monthly. |
| `/bootstrap` | The interview that fills `mem/`. |
| `/unsource` | Remove a source and reverse every change it caused. |

---

## A month of use

### Week 1, Monday, away from the machine

You find a paper worth reading and send it to the Telegram bot. Nothing is running and
nothing needs to be.

### Week 1, Tuesday, at the machine

```
.venv/Scripts/python scripts/telegram_capture.py --once
```
```
  vault/raw/inbox/2026-08-25-retrieval-survey.md
Captured 1 message(s) into raw/inbox/. Run /ingest to compile.
```

The PDF is saved to `vault/raw/pdfs/`. The file itself, not a link that may stop working.

You run `/ingest` and it shows the plan above. Three things in it are worth noting. It read
the PDF rather than only the message. It recorded that you stated the same intention three
weeks earlier, so this is a repeated intention rather than a new one. And it identified that
the paper contradicts an existing page on reranking latency.

You approve. Six pages are written, each claim citing the PDF.

### Week 1, Friday

```
/ask what do I know about reranking latency?
```

The answer is prose with citations, ending with:

```
Coverage: three sources, all before June. Two disagree about latency
under load; the conflict is unresolved. Nothing covers behaviour above
10,000 documents.
```

That last paragraph states what the vault does not contain, which is often more useful than
what it does.

### Week 3, Saturday, by email

```
Week of 2026-09-12

## Now
Read the retrieval survey. Fourth appearance since 12 August.
38 pages; section 4 is the relevant part, covering BM25 and vector
fusion. The remaining 30 pages are benchmark tables.
Decide: read section 4, schedule it, or drop it.

## Soon
Sarah's birthday, 19 September. No calendar entry exists.

## Worth knowing
The survey contradicts your reranking notes on latency, unresolved
since 25 August.
```

You did not request this. It arrives on schedule.

The point is not that the system remembered the paper. It is that the system recorded four
unanswered appearances and then supplied the summary, so the decision takes seconds rather
than an evening.

### Week 3, the same morning

```
/close the retrieval survey
```

It produces the section 4 summary. You read it and the loop moves to `vault/loops/closed/`.
It does not appear again. Marking it dropped has the same effect, and is also a decision.

### Effort spent

One message on Monday. One command on Tuesday. Reading a report on Saturday. The reading,
linking, cross-referencing and tracking happened without further input.

---

## Where files are kept

```
vault/raw/       what you captured. never edited.
vault/wiki/      compiled pages. answers "what do I know about X".
vault/loops/     what you said you would do.
vault/mem/       who you are. the compiler proposes changes; it does not write them.
vault/briefs/    one file per brief.
vault/index.md   the catalogue.
vault/log.md     a record of what happened and when.
```

---

## Obsidian

Optional.

1. Install from [obsidian.md](https://obsidian.md).
2. Choose **Open folder as vault** and select `vault/`. Not "create new vault", which
   creates an empty one elsewhere.
3. Install the **Web Clipper** extension and set its save location to `vault/raw/inbox/`.
   This is the highest-value fifteen minutes of setup if you save articles.

Obsidian only reads and displays. The commands do not require it.

---

## Optional additions

Each is independent. Instructions in [`setup.md`](setup.md).

| | Effect |
|---|---|
| **MCP server** | The vault becomes readable from every project, not only this folder. |
| **Email delivery** | The brief is sent rather than left in a file. |
| **Telegram capture** | Send from a phone. Nothing runs while you send. |
| **Scheduling** | The brief writes and sends itself; deadlines get a reminder on the day. |

### What the schedule does

```
python scripts/install_schedule.py --day FRI,SUN --time 19:00
```

Give it the evening **before** the morning you read the brief. A morning task on a sleeping
laptop depends on Windows wake timers, which Windows disables on battery; the run then waits
until you next open the machine. In the evening it is already awake.

Four tasks:

| When | What |
|---|---|
| 18:00 daily | drain Telegram into the inbox |
| 19:00, your days | write the brief and email it |
| 08:00, the next morning | recover a failed run, or fold in overnight material that changes something |
| 19:30 daily | email if something is overdue, due today, or due tomorrow — silent otherwise |

The morning run sends nothing on a normal week. It exists for the evening having failed, and
for material arriving overnight that changes what you would do.

The due check is separate from the brief because a deadline needs saying on the day. It goes
quiet once an item is more than 14 days overdue, and the brief takes over then with a forced
decision: drop it, set a new date, or do it now.

### How Telegram capture works

Messaging an assistant from a phone normally requires a server running constantly, which is
the recurring cost most comparable systems assume.

Telegram holds bot messages for 24 hours, so nothing needs to be running when you send. The
backlog is collected the next time the machine is used:

```
Monday, away        →  send the bot three links and a note
Tuesday, at the machine →  scripts/telegram_capture.py --once
                        four files appear in vault/raw/inbox/
                     →  /ingest-all
```

It handles text, links, forwarded messages, images and PDFs. Forwarded messages record the
original sender. Only your own chat identifier is accepted.

This is capture, not conversation. The bot does not reply. Answering requires a model running
constantly, which is the one part of this design that costs money, so it is omitted.

Setup takes about five minutes: message @BotFather, run `--setup` to find your chat
identifier, and put two values in `.env`.

### What the MCP server does

Without it the vault is readable only when that folder is open.

Register it once and any Claude Code session can read the vault from any project. You are
working in an unrelated repository, you ask *"search my notes for what I know about vector
search"*, and you get an answer.

| Available anywhere | Only in the project folder |
|---|---|
| *"search my notes for X"* | `/ingest` |
| *"what is still open?"* | `/brief` |
| *"save this to my notes"* | `/close`, `/lint`, `/unsource`, `/bootstrap` |

Reading is safe from any directory. Compiling writes to many pages at once and cannot be
undone with a keystroke, so it stays where the vault is visible.

After registering, restart other Claude Code windows so they load it.

---

## First week

1. Run `/bootstrap`. Everything else depends on it.
2. Capture and compile three or four items you care about.
3. Ask a question you already know the answer to, and check the citations.
4. Run `/brief` at the end of the week.

Then decide whether it earned a second week. The conditions for abandoning it are in the
[README](../README.md). The first is that nothing enters `raw/` for three consecutive weeks,
which means capture is too inconvenient and no improvement to the compiler will help.
