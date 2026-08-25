# Walkthrough

There is no app to open. Your second brain is a folder of text files, and you already have
everything needed to run it. This page shows exactly what to type, in order, the first time.

## What the interface actually is

No UI was built, and that was a decision rather than an omission — a web interface sits last
in the build order, deferred until the system proves it gets used. What you have instead is
two windows:

| | |
|---|---|
| **Claude Code** — where you work | This is the whole interface. You type `/capture`, `/ask`, `/brief`, and it does the work on the files. |
| **Obsidian** — where you look | A free notes app that displays the same folder. Optional. Nothing breaks if you never install it. |

The "database" is markdown files on your disk. That is what makes it portable, greppable,
versioned in git, and still readable in ten years.

There is also no *uploading*. You put files in a folder on your own computer.

---

## Setup

### 1. Install, and create your vault

```bash
git clone https://github.com/ArdellAlfatih/second-brain.git
cd second-brain
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ → bin/ on macOS and Linux
python scripts/init_vault.py
```

That last command creates `vault/` — the folder your content lives in. It is ignored by this
repository on purpose.

### 2. Make the vault its own private repo

```bash
cd vault
git init && git add -A && git commit -m "empty vault"
gh repo create my-brain --private --source=. --push
cd ..
```

**Keep it private.** It will hold your goals, your projects, the people you work with, and
everything you ever capture.

This also gives you an undo. A single `/ingest` rewrites ten to fifteen pages at once — with
git you can see exactly what changed and roll it back if it misread the source.

### 3. Open Claude Code in the repository root

Not in `vault/`, and not in your home folder. The commands only exist in the outer folder.

Check it worked — type a forward slash and start typing "capture":

```
/capture   /ingest   /ask   /close   /brief   /lint   /bootstrap   /unsource
```

If nothing autocompletes, you are in the wrong directory. This is by far the most common
thing that goes wrong.

### 4. Tell it who you are

Right now the brain knows nothing about you, and every answer will be generic.

```
/bootstrap
```

It interviews you one question at a time — your work, your goals, active projects, the
people who matter, and the rules it must follow. About twenty minutes. You can stop partway
and resume; it writes each section as it finishes.

Answer properly. Vague answers here produce a vague assistant forever.

### 5. Put something in

```
/capture https://example.com/that-article-you-saved
```

Or drag a file into `vault/raw/inbox/`. Capture is deliberately dumb and instant — it files
things word for word and does no thinking at all.

Everything you set up later drops into that same folder, which is why adding a new way to
capture never touches the rest of the system:

| Door | For |
|---|---|
| Drag into `vault/raw/inbox/` | anything already on your machine |
| `/capture` | a link, a thought, or the conversation you're in |
| Obsidian Web Clipper | articles and threads, one click from the browser |
| Telegram | anything, from your phone, anywhere |
| `brain_capture` over MCP | from inside any other project |

### 6. Compile it

```
/ingest
```

This is where the actual work happens: it reads the source, checks what you already have,
writes and links pages, and pulls out anything you said you would do.

It compiles **one source per run**, not your whole inbox — batching hides mistakes, and
compilation is the one irreversible step. It also shows its plan before writing anything:

```
Plan — 6 pages:
  new     wiki/sources/2026-08-24-retrieval-survey
  new     wiki/concepts/hybrid-retrieval
  update  wiki/entities/bm25       (+1 source)
  loop    "read the retrieval survey" — you said this on 12 Aug too
  flag    contradicts wiki/concepts/reranking on latency

Proceed?
```

Read that plan for the first ten or so sources. If it is misreading things, better to catch
it there than fifteen pages later.

---

## The eight commands

| | |
|---|---|
| `/capture` | **Put something in.** A link, a file, a thought, or this conversation. Instant, no interpretation. |
| `/ingest` | **Compile one source.** Writes pages, links them, extracts open loops, flags contradictions. |
| `/ask` | **Ask a question.** A real answer with citations, plus what the vault does *not* know. |
| `/close` | **Deal with one loop.** Produces the drafted email, the summary, the next action. |
| `/brief` | **The weekly review.** What compiled, what contradicted, what you said you would do and haven't. |
| `/lint` | **Health check.** Broken links, uncited claims, stale pages. Monthly. |
| `/bootstrap` | **The interview.** Fills in who you are. Once, then refresh occasionally. |
| `/unsource` | **Undo a source.** Removes it and everything it caused, across every page it touched. |

---

## What using it actually feels like

Not a list of commands — a month, in order, so you can see where the value shows up.

### Week 1, Monday — on the train

You see a paper worth reading. You send it to your Telegram bot and forget about it. Takes
three seconds. Nothing is running; nothing needs to be.

### Week 1, Tuesday — at your desk

```
.venv/Scripts/python scripts/telegram_capture.py --once
```
```
  vault/raw/inbox/2026-08-25-hybrid-retrieval-survey.md
Captured 1 message(s) into raw/inbox/. Run /ingest to compile.
```

The PDF itself landed in `vault/raw/pdfs/` — the actual file, not just a link that will rot.

You type `/ingest`. Before writing anything, it shows you what it intends to do:

```
Plan — 6 pages:
  new     wiki/sources/2026-08-25-hybrid-retrieval-survey
  new     wiki/concepts/hybrid-retrieval
  update  wiki/entities/bm25              (+1 source)
  loop    "read the hybrid retrieval survey"
          — you also said this on 12 Aug
  flag    contradicts wiki/concepts/reranking on latency

Proceed?
```

Three things happened there that are worth noticing.

It **read the PDF**, not just the message you sent. It **noticed you'd said the same thing
three weeks ago** — so this isn't a new intention, it's a recurring one you keep not acting
on. And it **caught that this paper disagrees** with something already in your notes about
reranking latency, which you would not have remembered.

You approve. Six pages get written, every claim citing the PDF.

### Week 1, Friday

```
/ask what do I actually know about reranking latency?
```

You get prose, not a list of files — with citations you can follow, and this at the end:

```
Coverage: three sources, all before June. Two of them disagree about
latency under load and the conflict is unresolved. Nothing covers
behaviour above 10k documents.
```

That last paragraph is the part most systems don't give you. Knowing what your notes *don't*
cover is often more useful than what they do.

### Week 3, Monday morning — the brief arrives by email

You didn't ask for this. It shows up because it's Monday.

```
Week of 2026-09-08

DECIDE NOW
  "Read the hybrid retrieval survey" — surfaced 4x since 12 Aug.

  You keep saying you'll read this and not reading it. Here's the
  summary so you can decide in ten seconds instead of an evening:

  38 pages. Section 4 is the only part relevant to you — BM25 and
  vector fusion, the thing you flagged in March. The other 30 pages
  are benchmark tables you don't need.

  Kill it, schedule it, or move to someday?

COMING UP
  Sarah's birthday, 12 Sep. No calendar event exists.

FLAGGED
  The survey contradicts your reranking notes on latency.
  Still unresolved from 25 Aug.

WHAT THE BRAIN DOESN'T KNOW
  Nothing added since 28 Aug. Two topics you asked about this
  month have no sources at all.
```

**This is the point of the whole project.** Not that it remembered the paper — anything can
do that. That it noticed you'd committed to reading it four times, and then removed the
reason you kept avoiding it, by telling you which 8 pages of 38 actually matter.

### Week 3, still Monday

```
/close the retrieval survey
```

It gives you the full section-4 summary, you read it in five minutes, and the loop moves to
`vault/loops/closed/`. It never appears again.

Or you say kill it — and it also never appears again, without guilt, because you made an
actual decision instead of letting it rot in a list.

---

### What that looked like in effort

Three seconds on a train. One command on Tuesday. Reading a brief on Monday. Everything
else — the reading, the linking, the cross-referencing, the noticing — happened without you.

That's the trade the whole design is built around: **you choose what goes in and what to do
about it; the system does the bookkeeping.**

---

## Where things live

```
vault/raw/       what you fed it. never edited. the ground truth.
vault/wiki/      what it worked out. answers "what do I know about X".
vault/loops/     what you said you'd do. the part that nudges you.
vault/mem/       who you are. yours — it proposes, never writes.
vault/briefs/    one file per week.
vault/index.md   the catalogue of everything.
vault/log.md     what happened, when.
```

You will rarely open these by hand, but it helps to know they are just files.

---

## Obsidian, if you want it

Optional. Skip it entirely and nothing breaks.

1. Install from [obsidian.md](https://obsidian.md) — free.
2. Choose **Open folder as vault** and pick the `vault/` subfolder. Not "create new vault",
   which makes an empty one somewhere else.
3. Install the **Web Clipper** browser extension and point it at `vault/raw/inbox/`. This is
   the best fifteen minutes you can spend on the whole system — saving an article becomes one
   click.

Obsidian only reads and displays. The commands never need it running.

---

## Optional extras

Each is independent; set up none, some, or all. Details in [`setup.md`](setup.md).

| | What it gets you |
|---|---|
| **MCP server** | The vault reachable from every other project you work in, not just this folder. |
| **Email delivery** | The weekly brief pushed to you instead of waiting in a file. |
| **Telegram capture** | Send things from your phone. Nothing needs to be running when you send. |

### How the Telegram one works

Worth understanding, because it's the part that sounds like it should cost money and doesn't.

Normally, messaging an assistant from your phone means a server is listening somewhere —
that's the $7–24/mo most builds of this assume. But **Telegram holds bot messages for 24
hours**, so nothing has to be running when you send:

```
Monday, on the train   →  you message your bot three links and a thought
Tuesday, at your desk  →  .venv/Scripts/python scripts/telegram_capture.py --once

                          vault/raw/inbox/2026-08-25-hybrid-retrieval-paper.md
                          vault/raw/inbox/2026-08-25-look-into-this-for-the-.md
                          vault/raw/inbox/2026-08-25-whiteboard-photo.md
                          Captured 4 message(s). Run /ingest to compile.

                       →  /ingest
```

You fire things at it all week from wherever you are; it drains when you next sit down.

It handles text, links, forwards (keeping the original sender as provenance), photos and
PDFs — those get downloaded into `vault/raw/` so the source survives even if the link rots.
Only your own chat ID is accepted, so nobody who stumbles across your bot can write into
your vault.

**One tradeoff, stated plainly:** this is capture, not conversation. It won't answer you.
Replying needs a model running somewhere always-on, which is the single thing in this project
that would cost money — so it's left out. Capture is the more valuable half, and it's the
half that's free.

Setup is about five minutes: message @BotFather, run `--setup` to find your chat ID, paste
two values into `.env`. Full steps in [`setup.md`](setup.md#6-telegram-capture-from-your-phone-optional).

---

## Your first week

In order, and nothing else:

1. Run `/bootstrap`. Twenty minutes, and everything downstream depends on it.
2. Capture and ingest three or four things you actually care about.
3. Ask it something you already know the answer to, and check the citations.
4. Run `/brief` by hand at the end of the week.

Then decide whether it earned a second week. The failure conditions are in the
[README](../README.md) — the honest one being that if nothing enters `raw/` for three weeks
running, the capture friction is too high and no amount of compiler quality will save it.
