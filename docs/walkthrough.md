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

## What a real session looks like

**You:**
```
/capture that PDF on retrieval I keep meaning to read
```
**It replies:**
```
Filed 2026-08-24-retrieval-survey (pdf). Uncompiled.
```

**You:**
```
/ingest
```
It shows the plan above, you approve, it writes.

Then a week later, without you asking:

```
Week of 2026-08-31

DECIDE NOW
  "Read the retrieval survey" — surfaced 4x since 12 Aug.
  Kill it, schedule it, or move to someday?

  Summary, so you can decide without reopening it:
  38 pages on hybrid retrieval. The part relevant to you is §4 —
  BM25 and vector fusion, which is the thing you flagged in March.
  The rest is benchmark tables.

COMING UP
  A birthday, 4 Sep. No calendar event exists.

WHAT THE BRAIN DOESN'T KNOW
  Three sources on retrieval, all pre-June. Nothing on how any
  of it behaves at scale.
```

That first block is the point of the project. Nothing else you use notices that you said you
would read something, twice, and then didn't — and then hands you the summary so the decision
takes ten seconds instead of an evening.

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
