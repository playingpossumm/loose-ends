# How this differs

Six write-ups were used as benchmarks for this project, plus the wider category of
Obsidian-based personal knowledge systems. This document says plainly what is new here, what
was borrowed, and where the alternatives are better — because a comparison that only flatters
the thing you built is not worth writing down.

## The short version

This is the same *category* as the others — a persistent personal memory layer — and it does
not pretend otherwise. Everyone here wants the same four things: you never start from zero,
one archive you can interrogate, reachable wherever you work, and understanding that
compounds.

What differs is the combination of guarantees underneath:

- **Provenance is mandatory and machine-checked**, not a prompt instruction. Every claim
  traces to a source and a locator, and `/lint` fails the vault when one does not.
- **Compilation is reversible.** A source can be removed and its influence reverted across
  every page it touched. Nothing else in the comparison offers this.
- **Commitments persist, and arrive half-done.** Others surface open items when asked; here
  they are tracked objects with a status, an ignore-counter, and an escalation rule — and
  the nudge comes with the artifact that closes it. This is the real dividing line: every
  other system in the comparison ends at *telling you*. **They store; this one is built to
  make you act.**
- **Reach is agent-agnostic by design** — an MCP server over plain markdown, not a plugin
  bound to one editor or one vendor.

None of those is a new idea in isolation. The claim is that the four together, at a scale
where the machinery stays simple enough to read, is a different thing from any one of the
alternatives.

---

## What is genuinely new

Only four things. Everything else on this page was assembled from prior work.

### 1. Loops as first-class, persisted objects

Others surface open items *at query time*, derived on demand. GBrain does this well — ask it
about a meeting and it will tell you what is still outstanding. But that is a derivation, not
a tracked object: nothing persists, nothing counts how long it has been ignored, and nothing
comes back on its own.

Here a loop is a file in `loops/open/` with `status`, a `surfaced` counter, provenance back
to the source that produced it, and an escalation rule. It survives sessions. It returns
weekly whether or not you ask. After four ignored appearances it is promoted to a
decide-now block: kill it, schedule it, or demote it.

The motivating case — *"I said I wanted to learn this, filed the PDF, never read it"* — is
not a question anyone would think to ask a knowledge base. That is exactly why it needs to
be pushed rather than queried.

It is a capability of the memory layer, not the reason for it. The memory has to be worth
having on its own; loops are what you can do once it is.

### 1b. The nudge arrives with the work started

Tracking a commitment is cheap and nobody's differentiator. What none of the six do is
**remove the friction that kept the loop open in the first place.**

A loop you have ignored four times does not need a fifth reminder — the reminder was never
the bottleneck. So the brief hands you the drafted email in your own voice with the vault's
context already in it, or the event details ready to paste, or a summary of the PDF so you
can decide whether you still care without reopening it.

GBrain will tell you that Alice owes you a security review and you owe her pricing. It will
not write the follow-up. That is the gap this fills.

**Drafts only** — nothing is sent, nothing is written to a calendar, and that boundary holds
because the system has no credentials that could do otherwise. The judgement of whether to
send stays where it belongs.

### 2. Decompilation

Compilation spreads one source across ten to fifteen pages. Source #1 states the problem
outright — *"a bad source in a compiler has touched fifteen pages before you notice"* — and
offers no remedy. None of the six do.

`/unsource` is the remedy. Because every page records the source ids that shaped it,
removing a source and reverting its influence claim-by-claim is a real operation. `git
revert` cannot do this: later good edits sit on top of the bad ones, so reverting the commit
destroys everything compiled since.

It is also the deletion mechanism. Removing what the system knows about a person is the same
operation as removing a bad source.

### 3. The two-store asymmetry, enforced

Most systems have both a knowledge base and some profile file. Few treat them as
categorically different things.

|  | `wiki/` — world knowledge | `mem/` — self knowledge |
|---|---|---|
| Author | the model | you |
| Rebuildable from `raw/` | yes | **no** |
| Contradictions are | findings — flag, keep both | bugs — surface, human fixes |
| Compiler may | write freely | **propose only, never write** |

The consequence that matters: a contradiction between two articles is interesting and gets
preserved. A contradiction between your stated goal and your actual commitments is a problem
and gets escalated. Same word, two entirely different mechanisms — and conflating them is
what makes these systems feel vague.

### 4. The brief is the product

Every benchmark treats the wiki as the deliverable and a summary as a nice-to-have. Here it
is inverted: the wiki is substrate, and the weekly brief is the thing the project is judged
on. Hence the ten-line cap, the ranking against your actual stated goals, and **nudge
precision** as the headline metric.

---

## What was borrowed, and from whom

Stated plainly, because the novel surface above is narrow and pretending otherwise would be
dishonest.

| Borrowed | From |
|---|---|
| `raw/` immutable, separate from LLM-owned derived pages | Karpathy, llm-wiki |
| Compile-at-ingest rather than derive-at-query | Karpathy, llm-wiki |
| `index.md` as catalogue, `log.md` greppable and append-only | Karpathy, llm-wiki |
| `CLAUDE.md` as the schema that makes the model a disciplined maintainer | Karpathy, llm-wiki |
| Gap analysis — every answer states what is *not* known | GBrain |
| Synthesised answer with citations, not a ranked page list | GBrain |
| Typed relations between entities | GBrain (concept only; no graph DB here) |
| One-question-at-a-time bootstrap interview | @aiedge_ prompt OS |
| Stable vs. temporary facts; mark assumptions; date what expires | @aiedge_ prompt OS |
| Split profile files rather than one monolithic context file | @aiedge_ prompt OS |
| Markdown as truth, Obsidian as viewer, git for history | the whole category |

---

## Head to head

### vs. GBrain (Garry Tan)

The most capable system in the comparison, and built for a different job.

| | GBrain | this |
|---|---|---|
| Scale | 155,795 pages, 24,589 people | zero, targeting hundreds |
| Retrieval | vector + typed graph over PGLite | `index.md` + grep |
| Truth lives in | a database | markdown files |
| Autonomy | 24/7 daemon, 66 cron jobs | weekly, run by hand |
| Entity model | people, companies, deals, meetings | papers, tools, concepts, projects, people |
| Multi-user | yes, ACL-scoped per login | single user by decision |
| Open commitments | derived at query time | persisted, counted, escalated |
| Remove a bad source | not offered | `/unsource` |

GBrain is a VC's institutional memory — it enriches people and companies, prepares you for
meetings, and scales to a team. Its `+31.4 points P@5` graph advantage is real *at its scale*.
At a few hundred pages that machinery is overhead: grep is faster, cheaper, and debuggable by
reading it.

**The honest summary:** GBrain is more capable and more proven. It is aimed at a problem this
project does not have, and lacks the one layer this project is for.

### vs. Karpathy's llm-wiki

Not a competitor — the direct ancestor. It is an idea file, explicitly abstract, meant to be
handed to an agent that then builds a specific version with you. This is one such version.

Divergences: it has no notion of tracked commitments; it is query-driven where this is
push-driven; it does not address removing a source. On retrieval it is followed exactly —
it says an index file suffices at ~100 sources, and at this scale that is right.

### vs. Obsidian + Claude tutorials

These are setup guides: install Obsidian, wire an MCP plugin, write a `CLAUDE.md`, schedule a
daily task. Cheaper to adopt, and a reasonable place to start.

Differences: they file and retrieve but do not track intent; contradiction handling is a
prompt instruction rather than an enforced rule; citation is optional where here it is
mandatory and machine-checked; and they depend on Obsidian's REST plugin running, which is
the most fragile part of every one of those guides. Here Obsidian can be uninstalled without
consequence.

### vs. prompt-based operating systems (@aiedge_ and similar)

A structured profile of you — `PROFILE.md`, `GOALS.md`, `PROJECTS.md`, `RULES.md` — built by
interview. Excellent at what it does, and its discipline was adopted wholesale into `mem/`.

It is a *context layer*, not a knowledge base: there is no `raw/`, no compilation, no
accumulation from sources. It answers "who am I and how should you work with me", not "what
have I read". This project runs it as one of two stores rather than the whole system.

### vs. generic PKM (PARA, Zettelkasten, packaged skill sets)

Packaged Obsidian skill sets — 40-plus commands, PARA folders, progressive summarisation,
semantic search — are more featureful than the seven commands here.

They impose a filing taxonomy, which is the thing that historically rots: the maintenance
burden is what kills personal wikis, and a taxonomy adds to it. There is no PARA here and no
Zettelkasten. Pages exist because a source created them; structure emerges from citations
rather than from a folder scheme you have to maintain.

---

## Where the alternatives are better

- **GBrain** — vastly more capable at scale, has multi-user ACLs, autonomous enrichment,
  measured retrieval benchmarks, and years of production use. If the corpus ever passes
  ~5,000 pages, revisit.
- **Packaged skill sets** — dozens of ready commands and cross-agent support (Claude, Codex,
  Gemini). This has seven commands and is shaped for Claude Code.
- **The tutorials** — an evening to set up, no custom skills to maintain.
- **Karpathy's pattern** — more portable precisely because it is abstract. This is one
  opinionated instantiation, and opinions age.

The case for building this anyway: none of them notices that you said you would read
something, twice, and then didn't. That is the one thing this is for.

---

## Which to pick

| Situation | Use |
|---|---|
| A team, tens of thousands of pages, people and companies | GBrain |
| Want the pattern, will shape it yourself | Karpathy's llm-wiki |
| Want something working tonight with no custom code | an Obsidian + Claude tutorial |
| Want Claude to know who you are, nothing more | a prompt OS like @aiedge_'s |
| Want your notes to chase you about what you said you'd do | this |
