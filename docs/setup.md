# Setup

The vault is built and the skills are written. Three things remain, and only the first is
required to start using it.

## 1. Open Claude Code in this folder (required)

```
C:\Users\ArdellFavourCapital\Desktop\second-brain
```

Project skills only load when this folder is the working directory. Opening Claude Code in
your home folder gives you no `/capture`, no `/ingest`. Confirm with `/capture` — if it
does not autocomplete, you are in the wrong directory.

Then run `/bootstrap`. It interviews you one question at a time and fills `mem/`. About
twenty minutes; you can stop and resume. Until it runs, every answer the brain gives is
generic.

## 2. Obsidian (optional, recommended)

Obsidian is a **viewer**. Nothing in the pipeline needs it running — that dependency is what
makes most published setups of this pattern fragile.

1. Install from [obsidian.md](https://obsidian.md) — free.
2. *Open folder as vault* → this folder. Not "create new vault".
3. Graph view shows the shape of what you have built, and which pages are orphans.

### Web Clipper — the highest-value fifteen minutes here

The browser extension turns articles, Twitter threads, and PDFs into markdown in one click.
It solves your main capture path with no pipeline code.

1. Install *Obsidian Web Clipper* for your browser.
2. Point its save location at `raw/inbox/`.
3. For image-heavy pages: Obsidian → Settings → Files and links → set *Attachment folder
   path* to `raw/images/`, then bind *Download attachments for current file* to a hotkey
   under Settings → Hotkeys. Clip, press the hotkey, images land locally instead of as URLs
   that rot.

## 3. Weekly brief scheduling (needs one decision from you)

`/brief` works today — run it manually any time. Automating the push needs a delivery
channel, which is the one open item in this project:

| Option | Cost | Notes |
|---|---|---|
| Run `/brief` manually, weekly | free | Works now. Relies on you remembering, which is exactly what this system exists to fix. |
| Scheduled Claude Code routine | free on your plan | Generates the brief on a cron. Delivery still needs a channel. |
| Email | free | Needs SMTP config or a mail account for it to send from. |
| WhatsApp via OpenClaw | ~$5/mo host | Deferred by decision. The brain exposes MCP; OpenClaw becomes a client. |

Tell me which and I will wire it up. Manual for the first few weeks is a reasonable start —
you will learn what the brief should contain before automating it.

## Daily use

| Command | When |
|---|---|
| `/capture` | anything worth keeping — a link, a PDF, a thought, this conversation |
| `/ingest` | compile one waiting source. One at a time, on purpose. |
| `/ask` | any question the brain might know |
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
