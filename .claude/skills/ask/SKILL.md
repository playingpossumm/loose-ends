---
name: ask
description: Answer a question from the vault — synthesised prose with citations and an explicit note on what the vault does not know. Use whenever the user asks something the brain might know, or says "ask my brain", "what do I know about", "what did I read about".
---

# ask

Answer the question, do not hand back a list of pages. The answer is the deliverable — a
ranked list of five files the user then has to read themselves is a search engine, and they
already have one.

## Retrieve

1. Read `index.md`. It is the catalogue, and at this vault's size it is the retrieval layer.
2. `grep` the vault for the question's key terms and entity names — deliberate, not a
   shortfall. Entity names dominate this corpus and plain text search is strong on them.
3. Read the pages that look relevant, in full.
4. Read `mem/` when the question touches the user's own goals, projects, or people.
5. Only if `wiki/` comes up thin, fall back to `raw/`. **When that fallback fires, say so** —
   it means compilation missed something, and that is worth knowing.

## Answer

Synthesised prose. Every claim carries a citation to the page it came from, and through
that page to the original source. If you cannot cite it, do not assert it.

Keep `## What sources say` distinct from `## Current view` when the distinction matters —
never present the user's own evolving position as though a source established it.

**Always end with a coverage note.** What the vault does not know, what is thinly sourced,
what has not been updated since something newer arrived. This is the most valuable part of
the answer and the easiest to skip:

> *The vault has three sources on this, all from before June. Nothing covers how it
> behaves at scale, and the tool page has not been touched since the version bump you filed
> last week.*

## Offer to file it

If the answer was substantial — a comparison, a synthesis, a connection across several
pages — offer to file it to `wiki/synthesis/`. Good answers should compound rather than
vanish into scrollback.

If they accept: write it with `type: synthesis`, cite every page it drew on, add it to
`index.md`, and log it. Mark it clearly as derived from the wiki rather than from a source,
so future compiles never treat your own output as evidence.

## Rules

- **No uncited claims.** If the vault does not support it, say the vault does not have it.
- **Do not answer from your own general knowledge** and let it read as vault content. If you
  add outside knowledge, label it plainly as outside the vault.
- **Say when you found nothing.** An honest "the vault has nothing on this, here is what
  would fill the gap" is a useful answer.
- Never write `mem/` from a query.
