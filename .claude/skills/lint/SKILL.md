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
Pages with no inbound links. Often means a related page was not updated on
ingest.

**4. Missing summaries**
`index.md` is generated from each page's `summary:` field, so a page without one appears in
the index as a bare title. Report any page in `wiki/` or `loops/` that has no `summary:`.

Index drift itself is no longer a class of fault: `scripts/build_index.py` rebuilds the file
from the vault, so it cannot disagree with what is on disk. Run it if the index looks stale.

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
yet escalated; anything in `loops/open/` that reads as already done. Also loops missing `title:` or
`summary:`, or whose `summary:` narrates the user in the third person — the nudge email is
built from that line alone and silently sends nothing without it.

**9. Synthesis gaps**
Run `python scripts/synthesis.py`. It lists every name in `mem/` mentioned across three or
more sources with no entity page, and every `category:` carrying three or more sources with
no concept page. Write the pages it names.

This is the check most likely to find something. The promotion rule in `/ingest` cannot fire
on its own — one source at a time sees no counts — so gaps accumulate silently while the
source count grows.

**10. Coverage gaps**
Entities mentioned across several pages with no page of their own (promote at 3 mentions).
Concepts referenced but never compiled. Questions the vault could not answer this week.

## Fix vs. report

**Fix silently:** a stale index (rebuild it), frontmatter fields derivable from context, broken links where
the target obviously renamed, `surfaced:` counters.

**Report only, never touch:** contradictions, staleness, orphans, coverage gaps, anything in
`mem/`, and anything requiring judgement about what the user meant.

## Output

Counts first, then details grouped by check, worst first. End with the three things most
worth acting on. Append to `log.md`: `## [YYYY-MM-DD] lint | N issues, N fixed`.

Suggest new questions and missing sources at the end — a lint pass is also where the vault
tells you what to read next.
