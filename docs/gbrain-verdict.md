# Do we build on GBrain?

**No.** Use it as a source of three ideas, not as a foundation.

## Why not

**1. Scale mismatch — this is the decisive one.**
GBrain's entire differentiator is vector search plus a typed knowledge graph, which it
benchmarks at +31.4 points P@5 over its graph-disabled variant. That gain is real *at
155,795 pages*. You have zero pages and will plausibly have a few hundred (B2: no existing
corpus, hobby and side-project scale). At that size `grep` over an `index.md` beats a
vector store on every axis that matters — latency, cost, debuggability, and the ability to
read your own system. You would be installing the solution to a problem you do not have.

**2. Shape mismatch.**
GBrain models people, companies, deals, meetings, and edges like `works_at` and
`invested_in`. That is a VC's CRM brain, and its showcase output is meeting prep. Your core
object (A1) is an **open loop** — "I said I would learn this and never did." GBrain has no
representation for that. You would spend your time fighting its schema rather than building
the one thing you actually want.

**3. Architecture conflict.**
GBrain is database-first (PGLite). You want markdown-as-truth, which is what makes the vault
readable in Obsidian, portable across models, and diffable in git. Retrofitting
markdown-truth onto a DB-first system is more work than starting from markdown.

**4. It undercuts A2.**
You said portfolio still matters, if less than for `rag-project`. Adopting a finished brain
wholesale means the interesting engineering belongs to someone else. Your first repo was
strong precisely because the decisions in it were yours and measured.

**5. Dependency risk on a system you intend to live in for years.**
Personal knowledge infrastructure is the worst place to inherit someone else's roadmap.

## What to steal

| From GBrain | Take it as |
|---|---|
| **Gap analysis** — "here is what the brain does *not* know yet" | The best single idea in all six sources. Every answer and every weekly brief ends with a coverage note. |
| **Typed edges** | Keep the concept, drop the graph database. Types live in frontmatter (`relates_to`, `authored_by`, `supersedes`). |
| **Synthesised answer + citations** | The answer *is* the deliverable, not a ranked list of pages. |

## Revisit if

- The corpus passes ~5,000 pages and `grep` measurably degrades, or
- You decide you want the always-on OpenClaw/Hermes deployment and would rather not build
  the glue yourself.

Neither is true today, and both are cheap to reverse into later because the retrieval layer
sits behind a single interface from day one.
