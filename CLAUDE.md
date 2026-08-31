# loose-ends — vault schema

This file is the contract. It tells you how this vault is structured and how to maintain it.
Read it before touching anything. Karpathy's llm-wiki write-up calls this the key
configuration file, and it is right: it is what makes you a disciplined maintainer rather
than a generic assistant.

> **Every path in this file and in every skill is relative to `vault/`.**
> `raw/inbox/` means `vault/raw/inbox/`. The repository root holds the *system* — skills,
> server, scripts, docs — and is public. `vault/` holds *your content* and is a separate
> private repository. Never write anything outside `vault/` when compiling.

Design rationale lives in [README.md](README.md); the decision trail is in
[docs/decisions.md](docs/decisions.md). **Do not re-litigate settled decisions** — if
something here seems wrong, say so, don't quietly do it differently.

## The two stores

| | `wiki/` — world knowledge | `mem/` — self knowledge |
|---|---|---|
| Author | you (the model) | the human |
| Rebuildable | yes, from `raw/` | **no** |
| Contradictions are | findings — flag, keep both | bugs — surface, let the human fix |
| You may | write freely | **propose only, never write unasked** |

Never blur these. A claim about the world goes in `wiki/`. A fact about the user goes in
`mem/`, and only with explicit confirmation.

## Layout

```
raw/inbox/     landing zone. everything arrives here.
raw/*/         filed by type after ingest: articles pdfs images transcripts notes
wiki/sources/  one page per raw item
wiki/entities/ people, tools, papers, projects
wiki/concepts/
wiki/synthesis/ answers to the human's own questions, filed back
loops/open/    the acting layer
loops/closed/
loops/dates/   birthdays, deadlines, recurring
mem/           profile.md goals.md projects.md people.md rules.md
briefs/        one file per brief
index.md       catalogue of every wiki page
log.md         append-only, chronological
```

## Frontmatter

### Items in `raw/inbox/`

Written by whichever door captured them — `/capture`, the Telegram script, the MCP server,
or by hand. Read these before compiling:

```yaml
---
id: 2026-08-25-some-slug
captured: YYYY-MM-DD        # when it was filed
sent: <ISO timestamp>       # when it was actually said, if known — may be days earlier
kind: note | article | pdf | image | transcript | file
origin: <url, file path, "conversation", "telegram", or
         "telegram (forwarded from NAME)">
title: <short human title>
attachment: raw/pdfs/foo.pdf    # OPTIONAL — see below
status: uncompiled | compiled
---
```

**`attachment:` means the markdown is a stub.** The real content is in the file it names —
open that. A Telegram-captured PDF has a one-line body and the whole document beside it.

**A forwarded origin is provenance about a third party.** `forwarded from Kyara` means Kyara
said it and the user relayed it; attribute the claim to Kyara. Losing that turns someone
else's opinion into the user's own.

### Pages in `wiki/` and `loops/`

Mandatory on every page:

```yaml
---
type: source | entity | concept | synthesis | loop | date
category: <free-text topical bucket>
folder: <the directory this page lives in>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source-id, ...]      # what this page was compiled from
stability: stable | temporary
confidence: fact | assumption
---
```

`loops/` pages add:

```yaml
status: open | done | killed | someday
title: <the name of the thing, title case — not a description of it>
summary: <one sentence, addressed to the user, that stands alone in an email>
surfaced: <count of times it has appeared in a brief unacknowledged>
due: YYYY-MM-DD                # optional
nudge: morning | evening       # optional; overrides the default split
```

**`title:` is required on every loop.** The `# ` heading may describe the loop; the field
must name the thing, in title case, as a subject line would carry it. A single generic word
is not a title: if the loop is about a sheet, a website or an interview, say which one.

| Heading | `title:` |
|---|---|
| Foundation — start go-to-market planning (Monday) | Foundation GTM Planning |
| RAG finished — Tuesday 1 September | RAG Project |
| Trip — 4 to 6 September 2026 | September Trip |
| Check masters, and what documents need preparing | Masters Applications |

**`summary:` is required on every loop.** The nudge email prints it verbatim and prints
nothing when it is absent. It cannot be assembled from the page body: that body cites its
sources by path, argues its own ranking, and refers to the user in the third person, all of
which is correct in the vault and wrong in an email. Write one sentence, in the second
person, that means something to someone who has not opened the vault.

| Wrong | Right |
|---|---|
| His own date, stated 2026-08-31 | At 75%. Remaining technical work, plus the UI. |
| See `wiki/sources/2026-08-30-masters.md` | Find the closing date, and which documents an application needs. |
| The user wants to read this | Richard Cook, 18 principles, about 20 minutes. Unread. |

**`nudge:` is optional.** Without it, an item due tomorrow is nudged at 19:30 and everything
else at 07:00. Set it when the nature of the item disagrees with its date: reading is an
evening act whatever the deadline, and anything needing an office to be open is a morning
one.

## Non-negotiable rules

1. **Claim-level citation.** Every claim traces to a `sources/` page plus a locator. A
   summary drawn from a screenshot cites that screenshot. No uncited claims, ever.
2. **Tag every edit with its cause.** When a source causes a change to a page, record the
   source id in that page's `sources:`. This is what makes `unsource` possible — without
   it, a bad source is unremovable.
3. **Never overwrite on contradiction.** Keep both claims with their dates and sources,
   flag it, and log it. Resolution is the human's act, not yours.
4. **`raw/` is immutable.** Read it, never edit it. It is the only ground truth.
5. **Never write `mem/` unasked.** Propose changes; wait for confirmation. Observed
   preferences are not confirmed facts.
6. **Mark uncertainty.** `confidence: assumption` on anything inferred rather than stated.
   Date anything that can expire.
7. **Refuse sensitive material.** Passwords, API keys, credentials, health records: do not
   compile them. Say that you refused and why.
8. **No persistent memory outside these files.** Do not imply otherwise.
9. **Cap the blast radius.** One ingest touches at most 15 pages. If it wants more, stop
   and ask.

## Operations

| Skill | Does |
|---|---|
| `/capture` | put something into `raw/inbox/` with correct frontmatter |
| `/ingest` | compile one raw source into `wiki/` + `loops/`, update `index.md`, append `log.md` |
| `/ingest-all` | the same across the whole inbox, planned and approved as one batch |
| `/ask` | synthesised answer with citations and a coverage note |
| `/close` | produce the artifact that finishes one loop, then file the loop |
| `/brief` | the periodic report |
| `/lint` | contradictions, staleness, orphans, citation validity |
| `/bootstrap` | interview the user and fill `mem/` |
| `/unsource` | remove a source and reverse its influence |

## Answering questions

Search `index.md` first, then read the pages it points at. Plain `grep` is the retrieval
layer — that is deliberate, not a gap. Answer in synthesised prose with citations, and
**always end with a coverage note**: what the vault does not know yet, and what would fill
the gap. An answer with no coverage note is incomplete.
