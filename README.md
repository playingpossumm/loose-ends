# second-brain

A personal knowledge base that doesn't just remember what you read — it notices what you
said you'd do, and hands you the thing already half-done.

It answers two questions:

1. **What do I know about X?** — with citations back to the thing you actually read.
2. **What did I say I'd do and haven't?** — every week, until you decide.

Six well-known write-ups of this idea were used as benchmarks, including Karpathy's
[llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and Garry
Tan's GBrain. All six build the first thing. None of them builds the second.

**It runs at $0/month.** No API keys, no database, no server, no vector store.

---

## The part that's different

Most systems in this category are storage. You put things in, they organise them, you ask
questions. This one also tracks **open loops** — things you said and never resolved:

> *"I want to learn this"* — and the PDF has sat unread for six weeks.
> *"I'll send them that thing"* — and you didn't.
> A friend's birthday went in, and no calendar event ever appeared.

You never type these in. They're inferred from material you captured for other reasons.

**And the nudge arrives with the work already started.** A reminder you've ignored three
times doesn't need a fourth — the reminder was never the bottleneck:

| The loop | What arrives with it |
|---|---|
| You owe someone an email | the **drafted email**, in your voice, with context from your notes already in it |
| A birthday or deadline | the event details ready to paste, and the fact that nothing exists yet |
| A PDF you never read | a summary, so you can decide whether you still care without reopening it |
| A decision you never made | the options, and what your notes know about each |

GBrain will tell you that Alice owes you a security review and you owe her pricing. It won't
write the follow-up. That's the gap this fills.

**Drafts only.** Nothing is ever sent and nothing is written to a calendar. That boundary
holds because the system has no credential that could do otherwise — not because a prompt
asks it nicely. The one script that can send mail ([`send_brief.py`](scripts/send_brief.py))
has **no recipient parameter at all**: the destination is a config value, and
`--to someone@else.com` is a parse error rather than a policy violation.

---

## Getting things in

These systems don't die because the compiler is bad. They die because capture is
inconvenient, you stop feeding them, and a knowledge base nobody feeds is a dead repo. So
capture is designed to be the easiest part.

**One landing zone, many doors.** Everything ends up in `vault/raw/inbox/`, and the compiler
watches exactly one folder. That means new ways to get things in can be added forever
without touching the pipeline.

| Door | For | Setup |
|---|---|---|
| Drag into `vault/raw/inbox/` | anything already on your machine | none |
| `/capture` in Claude Code | a link, a thought, or the conversation you're in | none |
| **Obsidian Web Clipper** | articles, threads, PDFs — one click from the browser | ~15 min |
| **Telegram** | anything, from your phone, anywhere | ~5 min |
| `brain_capture` over MCP | from inside any other project you're working in | one command |

### The Telegram trick

Sending to your brain from your phone normally means running a server somewhere — that's
the $7–24/mo most builds of this quietly assume.

It isn't necessary. **Telegram queues bot updates for 24 hours.** So nothing has to be
listening when you send:

```
Monday, on the train      →  you message your bot three links and a thought
Tuesday, at your desk     →  python scripts/telegram_capture.py --once
                             ...four files land in vault/raw/inbox/
                          →  /ingest
```

You fire things at it all week from wherever you are; it drains when you next sit down.
No host, no VPS, no subscription, and the Telegram bot API is official — unlike every
WhatsApp route, which either needs a paid always-on host or a reverse-engineered library
that can get your number banned.

It handles text, links, forwards (keeping the original sender as provenance), photos and
PDFs. Only your own chat ID is accepted, so nobody who stumbles across your bot can write
into your vault.

**The tradeoff, stated plainly:** this gets you *capture* from your phone, not *answers*.
Replying needs a model running somewhere always-on, which is the one thing here that would
cost money. Capture is the more valuable half, and it's the half that's free.

---

## $0/month, and why that's possible

Every piece was chosen so nothing bills you:

| Part | How it's free |
|---|---|
| **Compilation and answers** | Runs on an existing Claude Code subscription. No API keys, no per-token billing. |
| **Storage** | Markdown files on your disk. No database, no hosting, no sync service. |
| **Retrieval** | An index file and `grep`. No vector store, no embedding API — deliberate, see below. |
| **Phone capture** | A Telegram bot. Official API, free, and *nothing needs to be running when you send*. |
| **The weekly brief** | Sent through your own email account. |
| **Reach from other projects** | A local MCP server, started on demand. No daemon, no open port. |
| **Viewing** | Obsidian — free, and optional. Nothing depends on it. |

For comparison, the usual builds of this idea assume a $7–24/mo VPS, an API budget of roughly
$15–40/mo at moderate volume, or a hosted vector database. None of that is here.

One thing is deliberately left out *because* it would cost money: **asking questions from
your phone while your laptop is closed.** That needs a model running somewhere always-on.
Capturing from your phone works and is free; answering doesn't.

---

## Why you'd want this

**You own it.** Plain markdown in a git repo. Not a database, not a SaaS account, not a
proprietary format. Readable in Notepad, in ten years, after the tools that made it are gone.

**No lock-in.** The vault is files plus a schema. Point a different model at it next year and
it still works. Nothing here is Claude-specific except convenience.

**Everything is checkable.** Every claim cites the source it came from. When it tells you
something, you can verify it instead of trusting it.

**It's reversible.** `/unsource` removes a bad source *and everything it caused*, across
every page it touched. Compilation spreads one source across a dozen pages; the published
write-ups of this pattern acknowledge that problem and offer no way back. `git revert`
doesn't solve it either — later good edits sit on top of the bad ones.

**Nothing to maintain.** No PARA, no Zettelkasten, no folder taxonomy to keep tidy. Pages
exist because a source created them, and structure emerges from citations. The maintenance
burden is what kills personal wikis; there isn't one here.

**Private by default.** Files on your disk, and the vault is a separate private repo.
Content passes through the model when you ask it to read something — the same as any
conversation — but the memory itself never leaves your machine.

---

## How it works

```
capture ──► raw/ ──► compile ──┬──► wiki/  ──► ask     "what do I know about X"
                               │
                               └──► loops/ ──► brief ──► close
                                             "you said   "here's the email.
                                              you'd..."   send it or kill it."
```

Two stores, kept strictly apart. This is the load-bearing decision:

| | **`wiki/`** — what you've read | **`mem/`** — who you are |
|---|---|---|
| Written by | the model | you |
| Rebuildable from `raw/` | yes | **no** |
| A contradiction is | a *finding* — flag it, keep both | a *bug* — surface it, you fix it |
| The compiler may | write freely | **propose only, never write** |

That asymmetry is the point. A conflict between two articles is interesting and gets
preserved. A conflict between your stated goal and your actual commitments is a problem and
gets escalated. Same word, two mechanisms — systems that blur them feel vague.

### Two repositories, one folder

```
second-brain/            the system — skills, server, scripts, docs. Shareable.
├─ .claude/skills/       the eight commands
├─ mcp/ scripts/ docs/
├─ CLAUDE.md             the schema the model must follow
├─ .env                  your credentials. gitignored, never leaves your machine.
└─ vault/                YOUR CONTENT. ignored here; its own private repo.
   ├─ raw/               what you fed it. immutable. ground truth.
   ├─ wiki/              sources, entities, concepts, synthesis
   ├─ loops/             open, closed, dates
   ├─ mem/               profile, goals, projects, people, rules
   ├─ briefs/            one file per week
   └─ index.md  log.md   the catalogue, and what happened when
```

You open the outer folder in Claude Code; everything the skills write goes into `vault/`.
Separating them is what lets the system be public while your notes stay private — and
versioning the vault on its own means every compile is a commit you can inspect or roll back.

### What the MCP server is for, in plain terms

Without it, your notes only exist when you have this one folder open. That's a filing
cabinet in a room you have to walk to.

The MCP server is a small program that lets **any** Claude Code session read the vault —
whatever project you happen to be working in. Register it once, and from then on you can
just say *"search my brain for what I know about X"* while you're deep in some unrelated
codebase, and get an answer without switching folders.

Think of it as the difference between *going to your notes* and *having your notes with
you*.

What travels, and what doesn't:

| From anywhere | Only inside this folder |
|---|---|
| search, read, list open loops, save something new | `/ingest`, `/brief`, `/close`, `/lint`, `/unsource`, `/bootstrap` |

That split is deliberate rather than a limitation. Reading is safe from anywhere.
Compiling rewrites ten to fifteen pages and can't be undone with an undo key — so it
happens where you're actually looking at the vault, not half-distracted from another
project.

Setup is one command, in [`docs/setup.md`](docs/setup.md#4-reach-it-from-your-other-projects-recommended).

### Why grep and not embeddings

At a few hundred pages, an index file plus `grep` beats a vector store on latency, cost,
debuggability, and your ability to read your own system. Retrieval sits behind one interface,
so swapping it later is a change rather than a rewrite. Vector search earns its keep
somewhere north of ~5,000 pages; most personal vaults never get there.

---

## Getting started

Full walkthrough: [`docs/walkthrough.md`](docs/walkthrough.md). The short version:

```bash
git clone https://github.com/ArdellAlfatih/second-brain.git
cd second-brain
python -m venv .venv
.venv/Scripts/python -m pip install -r mcp/requirements.txt   # Scripts/ → bin/ on macOS and Linux
python scripts/init_vault.py
```

Then make your vault its own private repo, so your notes get history and a backup:

```bash
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-brain --private --source=. --push
```

Now open Claude Code **in the repository root** — the commands only exist there — and run:

```
/bootstrap
```

It interviews you one question at a time to fill `mem/`: your work, your goals, active
projects, the people who matter, and the rules it must follow. Twenty minutes, and you can
stop and resume. Everything downstream is generic until it runs.

After that: `/capture` something, `/ingest` it, `/ask` a question.

Optional, and independent of each other — [Obsidian and the Web
Clipper](docs/setup.md#2-obsidian-optional-recommended) for one-click article saving, the
[MCP server](docs/setup.md#4-reach-it-from-your-other-projects-recommended) so the vault
reaches your other projects, [email delivery](docs/setup.md#5-email-delivery-for-the-brief)
for the weekly brief, and [Telegram
capture](docs/setup.md#6-telegram-capture-from-your-phone-optional) from your phone.

## The commands

| | |
|---|---|
| `/capture` | file something — a link, a PDF, a thought, the conversation you're in |
| `/ingest` | compile one source into pages and loops. One at a time, on purpose. |
| `/ask` | a real answer with citations, and an explicit note on what the vault *doesn't* know |
| `/close` | deal with one loop — get the drafted email, summary, or next action |
| `/brief` | the weekly review |
| `/lint` | citation validity, broken links, orphans, stale pages |
| `/bootstrap` | the interview that fills `mem/` |
| `/unsource` | remove a source and revert everything it caused |

## What it deliberately isn't

| Not building | Why |
|---|---|
| A task manager | You never enter a task. Loops are inferred from things captured for other reasons. The moment it needs deliberate entry, it has become the thing this avoids. |
| A vector store or graph DB | Earns its keep at 100k pages, not hundreds. |
| A web UI | The interface is Claude Code, plus Obsidian for reading. |
| A 24/7 daemon | A weekly cadence needs no always-on process. |
| Anything that sends on your behalf | It drafts. You send. |
| Calendar writes | It tells you the event doesn't exist. You make it. |

## Honest status

**This is new and unproven.** The system is complete; it has not been lived with. The claim
that it changes anything is an argument, not a result.

The metric it should be judged on is **nudge precision** — of the loops surfaced each week,
how many were worth surfacing. If that lands under ~30%, the concept is wrong. The other
stated failure conditions: nothing entering `raw/` for three consecutive weeks (capture
friction is fatal no matter how good the compiler is), or catching yourself maintaining the
wiki by hand.

How this compares to GBrain, llm-wiki, and the wider category — **including where they are
better** — is in [`docs/comparison.md`](docs/comparison.md). The design decisions and how
they were reached are in [`docs/decisions.md`](docs/decisions.md), and the ninety questions
behind them in [`docs/architecture-qa.md`](docs/architecture-qa.md).

## License

MIT — see [`LICENSE`](LICENSE).
