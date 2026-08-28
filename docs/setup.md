# Setup

## 0. Two repositories, one folder

This repository holds the **system** — skills, MCP server, scripts, docs — and is meant to be
shareable. Your **content** lives in `vault/`, which this repo ignores entirely and which is
its own separate private repository.

```
second-brain/            the system. shareable.
├─ .claude/skills/  mcp/  scripts/  docs/
├─ CLAUDE.md  README.md
├─ .env                  your credentials. gitignored. never leaves this machine.
└─ vault/                YOUR CONTENT. gitignored here; its own private repo.
   └─ raw/ wiki/ loops/ mem/ briefs/  index.md  log.md
```

You open the outer folder in Claude Code — that is where the skills load from — and
everything the skills write goes into `vault/`.

After cloning:

```
python scripts/init_vault.py
cd vault && git init && git add -A && git commit -m "empty vault"
gh repo create my-brain --private --source=. --push
```

Keep that second repo **private**. It holds your goals, your projects, the people you work
with, and everything you have ever captured.

## 1. Open Claude Code in the repository root (required)

```
<wherever you cloned it>
```

Project skills only load when this folder is the working directory — the outer one, not
`vault/`. Opening Claude Code anywhere else gives you no `/capture`, no `/ingest`. Confirm
with `/capture`: if it does not autocomplete, you are in the wrong directory.

Then run `/bootstrap`. It interviews you one question at a time and fills `mem/`. About
twenty minutes; you can stop and resume. Until it runs, every answer the brain gives is
generic.

## 2. Obsidian (optional, recommended)

Obsidian is a **viewer**. Nothing in the pipeline needs it running — that dependency is what
makes most published setups of this pattern fragile.

1. Install from [obsidian.md](https://obsidian.md) — free.
2. *Open folder as vault* → the `vault/` subfolder. Not "create new vault".
3. Graph view shows the shape of what you have built, and which pages are orphans.

### Web Clipper — the highest-value fifteen minutes here

The browser extension turns articles, Twitter threads, and PDFs into markdown in one click.
It solves your main capture path with no pipeline code.

1. Install *Obsidian Web Clipper* for your browser.
2. Point its save location at `vault/raw/inbox/`.
3. For image-heavy pages: Obsidian → Settings → Files and links → set *Attachment folder
   path* to `images/`, then bind *Download attachments for current file* to a hotkey
   under Settings → Hotkeys. Clip, press the hotkey, images land locally instead of as URLs
   that rot.

## 3. Run the brief by hand for a few weeks

`/brief` works today. Run it at the end of the week and read what comes out.

Do this before automating anything. You will learn what belongs in the brief — and, more
usefully, what does not — and that is much easier to adjust while you are still running it
yourself. Email delivery is step 5, once you know the thing is worth delivering.

## 4. Reach it from your other projects (recommended)

Without this, the brain only exists when Claude Code is open in this folder. With it, the
vault is available in every project you work in — your memory follows you instead of
waiting in a directory.

The MCP server is built and tested. Inside this folder it works already via `.mcp.json`.
To make it available **everywhere**, register it once at user scope:

```
claude mcp add --scope user second-brain -- "/ABSOLUTE/PATH/TO/second-brain/.venv/Scripts/python.exe" "/ABSOLUTE/PATH/TO/second-brain/mcp/server.py"
```

Then from any project: *"search my brain for what I know about reranking"*.

Six tools, all read-mostly:

| Tool | Does |
|---|---|
| `brain_index` | the catalogue — what exists at all |
| `brain_search` | ranked search with matching lines |
| `brain_read` | one page in full |
| `brain_loops` | what is still outstanding |
| `brain_capture` | file something new into the inbox |
| `brain_recent` | last N things that happened |

The only tool that writes is `brain_capture`, and it only ever appends a new file to
`raw/inbox/`. Nothing over MCP can edit or delete anything — compilation stays inside the
vault where you can see it. Paths are checked against the vault root, so a traversal attempt
is refused rather than served.

If you move the folder, re-run the command above with the new path.

## 5. Email delivery for the brief

Loops and reminders go out by email. Phone capture is Telegram's job (step 6); the two
channels do different things on purpose.

1. Copy `.env.example` to `.env` and fill it in. `.env` is gitignored — never commit it.
2. Gmail needs an **App Password**, not your account password. Go to
   **myaccount.google.com/apppasswords**.

   If it says *"the setting you are looking for is not available for your account"*, you
   need **2-Step Verification** switched on first (Security → 2-Step Verification), then
   the app-passwords page appears. Any SMTP host works if you would rather not use Gmail.
3. Test without sending:

```
.venv\Scripts\python.exe scripts/send_brief.py --dry-run
```

4. Then for real:

```
.venv\Scripts\python.exe scripts/send_brief.py
```

The script sends the most recent file in `briefs/` to exactly one address — the one in
`BRAIN_EMAIL_TO`. There is no recipient argument, deliberately: the vault drafts emails to
other people, and no code path exists that could transmit one.

It goes out flagged **high priority** (`Importance: High` and the `X-Priority` headers), and
when the brief has an unresolved decide-now section the subject gains `· decisions waiting`
so you can see it in the list without opening it.

A caveat worth knowing: Outlook, Apple Mail and Thunderbird show priority flags; **Gmail
largely ignores them** — its importance markers are algorithmic. If you read mail in Gmail
and want these to stand out reliably, add a filter: *from* your own address, *subject
contains* `Brain —`, action *star it* or *apply a label*.

Schedule it weekly once you have run `/brief` a few times by hand and know what belongs in
it.

## 6. Telegram capture from your phone (optional)

Send things to the brain from anywhere. Telegram queues bot updates for 24 hours, so
**nothing needs to be running when you send** — you message the bot, and next time you open
your laptop the backlog drains into `raw/inbox/`.

Telegram rather than WhatsApp on purpose: the bot API is official and free, where every
WhatsApp route either risks your account (Baileys, which is what OpenClaw uses by default)
or needs a $10-15/mo always-on host.

1. Message **@BotFather** on Telegram, send `/newbot`, follow the prompts. Copy the token
   into `.env` as `BRAIN_TELEGRAM_TOKEN`.
2. Send your new bot any message.
3. Find your chat id:

```
.venv\Scripts\python.exe scripts/telegram_capture.py --setup
```

   Put the printed `BRAIN_TELEGRAM_CHAT_ID` into `.env`. Messages from any other chat are
   ignored — without this, anyone who found your bot could write into your vault.
4. Then whenever you sit down:

```
.venv\Scripts\python.exe scripts/telegram_capture.py --once
```

Handles text, links, forwards (the original sender is kept as provenance), photos and PDFs
(downloaded into `raw/`). Voice notes keep the caption and drop the audio, per the earlier
decision to leave transcription out of scope.

`--watch` keeps polling if you want it live while you work.

**It captures only.** Asking questions from your phone needs a model on the other end, which
is the part that needs OpenClaw or an API budget — see the note in `decisions.md`.

## Daily use

| Command | When |
|---|---|
| `/capture` | anything worth keeping — a link, a PDF, a thought, this conversation |
| `/ingest` | compile one waiting source. One at a time, on purpose. |
| `/ask` | any question the brain might know |
| `/close` | deal with one open loop — get the drafted email, summary, or next action |
| `/brief` | weekly |
| `/lint` | monthly, or before a brief |
| `/unsource` | a source turned out to be wrong |

## First real session

The six benchmark sources you gave me are the best possible first corpus: you know the
content, so you can judge the output, and they genuinely contradict each other — Karpathy
says an index file is enough, GBrain says you need a vector graph. That contradiction should
surface on the first compile. If it does not, the compiler needs work.

Capture them into `raw/inbox/`, then `/ingest` them one at a time.

## A note on repository size

Binary sources — PDFs and images — are committed alongside the markdown, because provenance
breaks if the original disappears. This is fine at personal scale. If the repo passes a few
hundred megabytes, move binaries to git-lfs rather than gitignoring them; an uncitable
source is worse than a large repo.
