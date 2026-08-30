---
name: lint
description: Health-check the vault — citation validity, broken links, orphan pages, contradictions, stale claims, and index drift. Reports; fixes only mechanical problems. Use when the user says "lint", "health check", "check the vault", or before a brief.
---

# lint

Find what has rotted. Report everything; fix only what is unambiguous.

## Checks

**1. Citation validity** *(the automated guard — this is the one that matters)*
Every claim in `wiki/` and every loop must cite a `sources/` page plus a locator. Every
cited source id must exist in `raw/`. Report uncited claims and dangling citations
individually — this metric is how the project is judged, so do not summarise it away.

**2. Link integrity**
Every `[[wikilink]]` resolves. Report broken ones with their containing page.

**3. Orphans**
Pages with no inbound links. Often means `index.md` or a related page was not updated on
ingest.

**4. Index drift**
Every page in `wiki/` and `loops/` appears in `index.md`, and every `index.md` entry points
at a real file.

**5. Contradictions**
Pages asserting incompatible things. Check especially where two sources compiled at
different times touched the same entity. Report; never resolve.

**6. Staleness — source-relative, not calendar-relative**
A claim is stale when **a newer source on the same entity exists and was not integrated**.
Do not flag pages merely for being old; a page untouched for six months because nothing
new arrived is healthy, and flagging it trains the user to ignore staleness warnings.

**7. Frontmatter conformance**
Mandatory fields present per `CLAUDE.md`. Report anything missing `sources:`, since that
field is what makes `/unsource` possible.

**8. Loop hygiene**
Open loops with no citation; loops open past their `due:`; loops with `surfaced:` ≥ 4 not
yet escalated; anything in `loops/open/` that reads as already done.

**9. Coverage gaps**
Entities mentioned across several pages with no page of their own (promote at 3 mentions).
Concepts referenced but never compiled. Questions the vault could not answer this week.

## Fix vs. report

**Fix silently:** index drift, frontmatter fields derivable from context, broken links where
the target obviously renamed, `surfaced:` counters.

**Report only, never touch:** contradictions, staleness, orphans, coverage gaps, anything in
`mem/`, and anything requiring judgement about what the user meant.

## Output

Counts first, then details grouped by check, worst first. End with the three things most
worth acting on. Append to `log.md`: `## [YYYY-MM-DD] lint | N issues, N fixed`.

Suggest new questions and missing sources at the end — a lint pass is also where the vault
tells you what to read next.
