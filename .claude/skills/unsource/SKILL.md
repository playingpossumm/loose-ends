---
name: unsource
description: Remove a source from the vault and revert its influence across every page it touched — decompilation. Use when a source turns out to be wrong, unreliable, or must be deleted, or when the user says "remove that source", "that article was wrong", "undo that ingest".
---

# unsource

Compilation spreads one source across many pages. A bad source touches fifteen pages before
anyone notices, and none of the published write-ups of this pattern offer a way back. This
is the way back.

It is also the deletion mechanism — removing information about a person means removing every
page their source touched, which is the same operation.

## Why not just `git revert`

Because later good edits sit on top of the bad ones. Reverting the commit throws away
everything compiled since. This works claim-by-claim instead, which is why `CLAUDE.md`
requires every page to record the source ids that shaped it.

## Procedure

**1. Identify.** Resolve the user's description to a `sources/` page and its raw id. If
ambiguous, list candidates and ask — unsourcing the wrong thing is expensive.

**2. Find the blast radius.** `grep` the vault for the source id. Every page with it in
`sources:`, every citation pointing at it, every loop extracted from it. Read `log.md` for
the original ingest entry.

**3. Report before touching anything:**
- pages that exist *only* because of this source → will be deleted
- pages where it is one of several sources → claims removed, page survives
- loops extracted from it → will be closed as `killed`
- claims that lose their only citation → **flag these individually and ask.** A claim you
  still believe but can no longer cite is the genuinely hard case, and it is the user's call
  whether to drop it or find a new source.

**4. Wait for confirmation.** Never proceed automatically. Show the full list first.

**5. Execute.**
- Delete single-source pages.
- On shared pages: remove claims citing only this source, strip the id from `sources:`,
  bump `updated:`, and leave a note in the body recording that a source was removed and
  when. Do not silently rewrite history.
- Close its loops as `status: killed` with a reason.
- Remove deleted pages from `index.md`.
- Move the raw file out of `raw/` only if the user asked for deletion; otherwise mark it
  `status: unsourced` and leave it. Removing a claim and destroying evidence are different
  requests.

**6. Re-lint.** Unsourcing creates orphans and broken links. Run `/lint` and fix what it
finds mechanically.

**7. Log:**

```
## [YYYY-MM-DD] unsource | <title> — N pages edited, N deleted, N loops killed
```

## Rules

- **Never proceed without explicit confirmation of the blast radius.**
- **Never silently drop a claim that other sources also support.** Check before removing.
- **Leave a trace.** A page that lost content records that it did. Invisible deletion is how
  a knowledge base starts quietly lying.
- Prefer marking over destroying when the user's intent is ambiguous — say what you did and
  let them escalate.
