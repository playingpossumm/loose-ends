# second-brain — architecture Q&A

Status: **open**. Answer inline under each question. Nothing gets built until this
is closed and a project summary is agreed.

Inputs digested: 6 sources — 2 popularizations (#1, #2), 1 pattern spec (#4,
Karpathy's llm-wiki gist), 1 production system README (#3, GBrain), 1 prompt-based
operating system (#5, @aiedge_), 1 reference architecture diagram (#6).

**The central structural finding across all six:** there are *two* knowledge
stores, and every source that conflates them gets confused. **World knowledge**
(what you have read — sources, entities, concepts) is append-heavy, LLM-authored,
unbounded, and contradictions in it are *findings*. **Self knowledge** (who you
are — goals, projects, people, decision rules) is small, human-authored,
high-churn, authoritative, and contradictions in it are *bugs*. Sources #1–#4 only
build the first. Sources #5–#6 mostly build the second. This project needs both,
kept separate, with different machinery. See sections Q and R.

---

## A. Purpose and scope

**A1.** What is this brain *for*, in one sentence you would defend six months from
now? The four sources describe four different machines: a research companion (#4),
a life-admin assistant (#2), a relationship/executive memory (#3), a compounding
content engine (#1). They need different schemas.
*Default: personal research + project memory first; relationship memory second.*

**A2.** Daily-use tool, portfolio piece, or both? `rag-project` was built to be
defensible. If this is also portfolio, the eval harness is not optional and the
README needs a measured claim.
*Default: both — daily use as the primary test, measurement as the proof.*

**A3.** What is explicitly **out** of scope? Naming exclusions now is what stops
this becoming "an app for my whole life."
*Default out: task management, calendar writes, anything that sends messages on
your behalf, anything financial.*

**A4.** Single user forever, or does this ever become multi-user (#3's
company-brain shape)? Decides whether scoping is designed in on day one or bolted
on never.
*Default: single user, but every read path takes a scope argument from the start.*

---

## B. Corpus and ingest

**B1.** What are the real day-one sources? Rank by volume and by value — they are
not the same ranking. Candidates: Twitter/X saves, web clips, PDFs/papers, your
own notes, LLM chat transcripts, WhatsApp, email, calendar, voice memos, YouTube
transcripts.

**B2.** Roughly how many sources exist **today** that you would backfill, and how
many per week going forward? This one number decides B3 and all of section H.
*Threshold: under ~150 sources, `index.md` + grep is genuinely enough (#4 says so
explicitly). Above ~1,000 you need real retrieval (#3's shape).*

**B3.** Backfill the existing pile in one batch, or start empty and compile
forward?
*Default: start empty, compile forward ~2 weeks to shake out the schema, then
backfill — backfilling into an untested schema wastes the most expensive
operation in the system.*

**B4.** Are images/screenshots first-class? Your Twitter material is partly
images. #4 notes LLMs can't read markdown-with-images in one pass and calls the
workaround clunky.
*Default: yes — transcribed to text at ingest, the transcription is what gets
compiled, the image is kept as provenance.*

**B5.** Do LLM chat transcripts (your Claude Code sessions) get ingested? Highest
volume, lowest signal density of anything you have.
*Default: not automatically. Opt-in per session via an explicit "file this."*

**B6.** Who curates? #4 is emphatic that source selection stays human. Should the
system ever *find* its own sources (web search on a detected gap)?
*Default: it may propose during lint; it never ingests unasked.*

---

## C. WhatsApp

**C1.** Which of the three WhatsApp roles do you actually want? They are
independent, with very different cost and risk:
- (a) **inbound channel** — you forward a link or voice note to the brain
- (b) **query surface** — you message the brain, it answers
- (c) **corpus** — bulk-ingest chat history as knowledge

*Default: (a) and (b) in v1 via OpenClaw. (c) deferred — see C3.*

**C2.** OpenClaw is a *gateway/agent runtime*, not a brain. Confirm the layering:
the brain exposes an API + MCP server, OpenClaw is one client among several
(Claude Code, CLI, web). The alternative — building the brain *inside* OpenClaw —
couples you to it permanently.
*Default: decoupled. OpenClaw must be swappable without touching the brain.*

**C3.** (c) is the consent problem. WhatsApp history is mostly **other people's
words**, ingested into a system that compiles, links, and resurfaces them. Your
own chats only, group chats, client chats? And which jurisdiction are you in —
this is a real question, not a formality.
*Default: if (c) happens at all — self-chat and explicitly whitelisted threads
only, never group chats, and other participants' messages stored as verbatim
provenance rather than compiled into claims about them.*

**C4.** Write access: should the brain ever *send* WhatsApp messages, or is it
read-and-reply-to-you only? Source #2's one hard rule is "keys, not prompts" —
enforce at the permission layer, not by instruction.
*Default: replies to you only, on a dedicated number, no outbound to third
parties, enforced by scoped credentials.*

**C5.** Voice notes — transcribe and ingest, or ignore? High value, and the one
capture mode with near-zero friction.
*Default: transcribe, treat as first-class raw.*

---

## D. Storage and representation

**D1.** Markdown-on-disk (#1/#2/#4) or database (#3 uses PGLite)?
*Default: markdown is the source of truth, git-versioned; any DB is a derived,
rebuildable index. Keeps #4's portability and #3's query power without making the
DB precious.*

**D2.** Obsidian in the loop, or plain files plus your own viewer? Obsidian gives
graph view and the clipper for free; it also adds a plugin/REST dependency, and
the Obsidian wiring in Source #2 is the flakiest part of these four documents.
*Default: files stay Obsidian-compatible (wikilinks, frontmatter), but nothing in
the pipeline requires Obsidian running. Viewer, not dependency.*

**D3.** One vault or many? #2 pushes per-project vaults so the agent sees less.
*Default: one vault with scoped views — an agent gets a subtree, not a separate
repo. Separate vaults fragment exactly the cross-links you are building this for.*

**D4.** Vault in the same git repo as the code, or separate? Your notes will be
private in a way the code may not be.
*Default: separate repos. Code public-capable, vault private, vault path is
config.*

**D5.** Frontmatter schema — what is mandatory on every page?
*Default mandatory: `type`, `created`, `updated`, `sources[]`. This is what makes
section G possible at all.*

---

## E. The compilation model

**E1.** How supervised is ingest? #4 prefers one-at-a-time with a human reading
the result. #3 runs a fully autonomous overnight daemon. #1 sells the daemon.
*Default: supervised for the first ~50 sources (you are debugging the schema, not
the content), then autonomous with a morning brief you can reject.*

**E2.** When one source touches 10–15 pages, do you want to **review a diff**
before it lands? Biggest quality lever and biggest friction cost, same knob.
*Default: yes — every compile lands on a branch or staged commit, and the brief is
a real diff summary, not prose. Auto-merge once trust is earned.*

**E3.** Is compilation **idempotent**? Re-ingesting the same source — no-op, or
double-compile?
*Default: content-hash every raw source; re-ingest is a no-op unless forced.*

**E4.** Recompilation: when the schema changes, do you rebuild all pages from raw?
The expensive operation none of these four sources costs out.
*Default: design for it — every page records the schema version and model that
compiled it, so partial recompiles are possible.*

**E5.** Does the *human* ever write wiki pages? #4 says rarely or never.
*Default: you may, and human-authored pages are marked and never silently
overwritten by the compiler.*

**E6.** Do good query answers get filed back as pages (#4's "explorations
compound")?
*Default: yes, but into a separate `synthesis/` space marked derived-from-wiki
rather than derived-from-source, so the compiler never treats its own output as
evidence. Skip this and it becomes a hall of mirrors.*

---

## F. Schema and page taxonomy

**F1.** What page types exist? Proposed: `source/` (one per raw item), `entity/`
(person, company, tool), `concept/`, `thread/` (an evolving line of thinking),
`synthesis/`, plus `index.md` and `log.md`. Confirm, cut, or add.
*Note: #6 proposes `literature/` + `permanent-notes/` — that is Zettelkasten
vocabulary, and it is a real distinction (notes about a source vs. atomic claims
in your own words). Do you want that split, or is `source/` + `concept/` enough?*

**F2.** Naming and IDs — human-readable slugs, or stable IDs with slugs as
aliases? Renaming a page breaks every wikilink pointing at it.
*Default: stable ID in frontmatter, slug filename, links resolved by ID, lint pass
fixes broken slugs.*

**F3.** How opinionated is the compiler allowed to be? Does a concept page state
*your* evolving view, or only what sources say?
*Default: both, in explicitly separated sections — "What sources say" vs "Current
view." Conflating them is how these systems start lying to you.*

**F4.** Granularity: when does a mention become its own page? Too eager gives you
4,000 stubs; too lazy gives a thin graph.
*Default: promote at 3 independent source mentions, or on demand.*

---

## G. Provenance, contradiction, staleness

**G1.** Claim traceability — sentence-level, paragraph-level, or page-level?
*Default: claim-level citation to a `source/` page plus locator. Anything coarser
makes G3 impossible.*

**G2.** When a new source contradicts an existing page: overwrite, append with a
flag, or fork into a disputed state?
*Default: never overwrite. The page holds both with dates and sources, the
contradiction is logged, and resolution is a human act.*

**G3.** **Decompilation.** A bad source touches 15 pages before you notice —
Source #1 admits this outright and offers no solution. Can you remove a source and
cleanly revert its influence?
*Default: yes, and this is a headline feature. Every page edit is tagged with the
source that caused it, so "unsource X" is a real operation. Nothing in the four
sources does this; it may be the most defensible thing you could build here.*

**G4.** Staleness: time since update, or superseded by a newer source? #2 says "not
updated in 2 weeks," a proxy so crude it will flag your best pages.
*Default: source-relative — a claim is stale when a newer source on the same
entity exists and was not integrated. Not calendar-relative.*

**G5.** Does the brain report **what it does not know** (#3's gap analysis)? The
single best idea in the four sources.
*Default: yes — every answer ends with an explicit coverage note.*

---

## H. Retrieval, and the rag-project relationship

**H1.** The framing "compilation replaces RAG" (Source #1) is false — #3 does both.
Compilation is a *write-time* transform; retrieval is a *read-time* one. And
contradiction detection at ingest (G2) is itself a retrieval problem: you cannot
flag a conflict with a page you failed to find. Confirm you agree — the rest of H
depends on it.

**H2.** Reuse `rag-project`'s stack, or rebuild? Its findings were tuned on
500-word document chunks; wiki pages and note-sized chunks will invalidate several
of them, the 256-token truncation finding especially.
*Default: reuse the architecture and the eval discipline, re-measure every
parameter. That re-measurement is the README.*

**H3.** At what corpus size do we switch from `index.md` + grep to embeddings?
*Default: build both behind one interface from day one; grep is default; switch
when the eval says grep is losing, not when it feels slow.*

**H4.** Hybrid BM25 + vector + graph, or start simpler?
*Default: BM25 first — free, and strong on entity names, which dominate this
corpus. Add vector when eval justifies it. Add graph traversal for entity
questions specifically.*

**H5.** Retrieve over **raw sources** as well as **wiki pages**, or wiki only? #4
implies wiki-only; #3 indexes pages.
*Default: wiki-first with raw as fallback on a coverage gap — and that fallback
firing is itself a signal that compilation missed something.*

---

## I. Entity and graph layer

**I1.** Typed edges (#3: `attended`, `works_at`, `invested_in`) or untyped
wikilinks (#4)? #3 claims +31.4 points P@5 from the graph.
*Default: typed, extracted at write-time without an LLM call where possible —
untyped links cannot answer "who works at X."*

**I2.** Which entity types matter for *your* life? #3's are VC-shaped (people,
companies, deals). Yours may be papers, tools, concepts, projects, people.
**Not defaultable — needs your answer.**

**I3.** Entity resolution: a name, an email, and a phone number are one person. How
hard do we try?
*Default: alias table maintained by the compiler, human-correctable, no fuzzy
auto-merge.*

---

## J. Query and output surfaces

**J1.** Which surfaces in v1 — CLI, MCP server (so Claude Code queries it),
WhatsApp via OpenClaw, web UI, scheduled brief?
*Default: MCP server + CLI in v1, WhatsApp in v1.5, web UI last. You have two
Next.js repos already, so the UI is the known quantity, not the risky part.*

**J2.** Answer format: synthesized prose with citations (#3) or ranked page list?
#3's whole pitch is that the answer *is* the deliverable.
*Default: synthesized prose + citations + explicit gap note. Also the thing you
can evaluate.*

**J3.** Other artifacts — comparison tables, Marp decks, charts (#4)?
*Default: defer. Markdown answers only in v1.*

**J4.** The morning brief: what is in it, and does it exist to be read or acted on?
*Default: what compiled, what contradicted, what went stale, what needs your
decision. Max 10 lines, or it goes unread by week 3.*

---

## K. Automation and the loop

**K1.** Scheduled compile — daily, on-drop (filesystem watch), or manual?
*Default: on-drop for capture, nightly for the heavy pass (lint, contradiction
sweep, consolidation).*

**K2.** #3's "dream cycle" — overnight consolidation that rewrites and merges.
Genuinely valuable, or a way to corrupt your corpus while you sleep?
*Default: yes, but strictly additive at first — it may propose merges, not execute
them, until the eval trusts it.*

**K3.** Where does it run? Your machine (must be awake) or a small always-on
box/VPS? OpenClaw wants always-on.
*Default: local-first with a documented VPS path. Decide before any scheduler code
is written — it changes the whole ops story.*

**K4.** What is the kill switch? If the compiler goes wrong at 3am, what limits the
blast radius?
*Default: every autonomous run writes to a git branch, never main, plus a hard cap
on pages touched per run.*

---

## L. Security, privacy, consent

**L1.** Threat model — what is the worst realistic outcome? (Vault leaks; agent
sends something on your behalf; third-party WhatsApp content exposed.)

**L2.** Secrets — where do keys live, and does any of this ever go near a public
repo? `.env` is gitignored, but the vault is the real exposure.

**L3.** Encryption at rest for the vault? Plain markdown on disk is the whole point
*and* the whole exposure.
*Default: private repo, OS-level disk encryption, no app-layer crypto — it would
break every tool in the ecosystem.*

**L4.** Data about other people: retention policy, and can you delete a person from
the brain on request? Compilation makes this genuinely hard.
*Default: G3's decompilation is also the deletion mechanism. Same machinery.*

**L5.** Which models see this data, and are you comfortable with that? Local model
fallback for sensitive subtrees?
*Default: cloud for compilation, with a `sensitive: true` flag that routes those
pages to a local model or excludes them entirely.*

---

## M. Evaluation

**M1.** What is the measurable claim this project makes? `rag-project`'s was a
metrics table that overturned four of its own conclusions. What is the equivalent
here? Candidates: contradiction-detection precision/recall; answer groundedness;
"compiled wiki beats raw RAG on multi-source questions."

**M2.** **Highest-leverage question in this document.** Sources #1 and #4 both
assert that compilation beats retrieval, and neither measures it. You have a
working RAG baseline sitting in `rag-project`. You could be the person who
measures it.
*Default: make this the project's headline result — same corpus, two systems, one
golden set of multi-source questions.*

**M3.** What is the golden set and who builds it? `rag-project` had 84 labelled
cases, and the smaller version misled you.
*Default: 80–120 cases minimum, built from real questions you actually asked, not
synthesized ones.*

**M4.** How do we evaluate compilation *quality*, not just retrieval? Harder —
there is no ground truth for "good wiki page."
*Default: proxy metrics — citation validity (does every claim trace?), link
integrity, contradiction recall against a seeded set of known conflicts.*

**M5.** Track cost per source compiled and per query? #1 and #2 never mention cost;
#3 runs 66 cron jobs.
*Default: yes, logged per run. Real constraint at 1,000 sources.*

---

## N. Cost, models, performance

**N1.** Monthly API budget ceiling?

**N2.** Which model for compilation vs. query vs. cheap mechanical passes (entity
extraction, linting)?
*Default: strong model for compilation — it is the irreversible step — cheap for
lint/extract, mid for query. Never the reverse.*

**N3.** Acceptable ingest latency — seconds, or by morning?
*Default: by morning for the heavy pass, seconds for capture acknowledgement.*

---

## O. Stack and repo layout

**O1.** Python (matches `rag-project`, and the retrieval ecosystem lives there) or
TypeScript (matches your Next.js repos and OpenClaw's ecosystem)?
*Default: Python core, thin TS only if a web UI happens.*

**O2.** Monorepo (`brain/` core, `mcp/`, `cli/`, `web/`) or split?
*Default: monorepo, one repo, clear package boundaries.*

**O3.** Vault checked into this repo, referenced by config, or a git submodule?
*Default: config path. Submodules will hurt.*

**O4.** Does this depend on Claude Desktop / Claude Code specifically (as Sources
#1 and #2 assume), or is it model- and harness-agnostic?
*Default: agnostic core with an MCP server. Claude Code becomes a client, not a
requirement — which is also what keeps it alive when the tooling churns.*

---

## P. v0 scope and done criteria

**P1.** Smallest thing genuinely useful to you within a week?
*Default: drop a file in `raw/` → it compiles into linked wiki pages with
citations → ask a question in Claude Code via MCP → get a cited answer with a gap
note. No WhatsApp, no scheduler, no web UI, no graph.*

**P2.** What is the "this is working" signal at 1 month? At 3?
*Default: 1mo — you stop re-explaining context to Claude. 3mo — it surfaces a
connection you did not make, and the eval shows compiled beats raw RAG.*

**P3.** What would make you abandon it? Naming the failure condition now is what
lets you kill it honestly instead of letting it rot — the exact fate Source #1
describes for most second brains.

**P4.** Build order — confirm or reorder:
1. vault schema + frontmatter + git
2. ingest/compile loop, supervised, with provenance
3. eval harness + golden set (early — `rag-project`'s lesson)
4. retrieval: grep → BM25 → vector, gated by eval
5. MCP server + CLI
6. contradiction / staleness / lint passes
7. decompilation (G3)
8. WhatsApp via OpenClaw
9. scheduler / nightly loop
10. graph layer, web UI

---

## Q. The self-knowledge layer (from #5 and #6)

Sources #5 and #6 build something #1–#4 barely touch: a structured model of *you*.
#5 breaks the monolithic `CLAUDE.md` into `PROFILE.md`, `GOALS.md`, `PROJECTS.md`,
`PEOPLE.md`, `RULES.md`, `INBOX.md`, `REVIEW.md`. #6 calls the same thing `mem/`
(claude.md, preferences, goals, projects, people, history).

**Q1.** Confirm the two-store split (see header). Self-knowledge lives in `mem/`,
is human-authoritative, and the compiler may *propose* changes to it but never
writes it unattended. World knowledge lives in `wiki/` and is LLM-owned.
*Default: yes. This is the load-bearing decision of the whole design.*

**Q2.** One `CLAUDE.md` or #5's split files? A monolith is simpler; split files are
selectively loadable, which matters once it is long.
*Default: split, with `CLAUDE.md` as a thin index that points at them — you get
both, and you can load `PROJECTS.md` without loading `PEOPLE.md`.*

**Q3.** #5's interview is genuinely the right bootstrap — one question at a time,
push for concrete examples, no gap-filling with guesses. Do you want to run it as
the first real act of the project?
*Default: yes, and we capture the transcript as a `source/` so the reasoning
behind your profile is itself provenance.*

**Q4.** #5 mandates separating **stable facts from temporary state**, dating
anything that can expire, and marking uncertain items as assumptions. This is
strictly better than what #1–#4 do.
*Default: adopt verbatim as frontmatter — `stability: stable|temporary`,
`expires:`, `confidence: fact|assumption`.*

**Q5.** #5's rule: "do not turn preferences into permanent facts without
confirmation." What is the promotion path from an observed preference to a stated
one?
*Default: the compiler may log observed preferences to a staging area; promotion
to `PROFILE.md` requires an explicit yes from you.*

**Q6.** #5's `RULES.md` includes "actions AI must never take without asking."
Note this is documentation of intent, **not** enforcement — Source #2's "keys, not
prompts" rule is the enforcement. They are complements, not substitutes.
*Default: maintain both, and treat any rule in `RULES.md` that could be enforced
by a scoped credential instead as a bug to fix.*

**Q7.** #5's Phase 5 contradiction check is over *self* knowledge — goals that
conflict with commitments, projects with no next action, obligations with no
owner, decision rules that live only in your head. This is a completely different
mechanism from #1/#4's source-vs-source contradiction flagging (G2). Do you want
both?
*Default: yes, both, implemented separately. The self-check is a rules-based lint;
the world-check is a retrieval problem.*

**Q8.** #5's rule "do not pretend Claude has persistent memory outside the files"
is a good honesty constraint. Does anything in this system rely on model-side
memory features?
*Default: no. Files only. Everything else is a portability trap.*

**Q9.** #5's sensitive-material exclusion list (passwords, API keys, credentials,
health records) — adopt as a hard deny-list at ingest, not a guideline?
*Default: yes, with a detector that refuses to compile matching content and tells
you it refused.*

**Q10.** #1 and #2 both propose per-project folders with `Inputs/Process/Outputs/
Feedback` and a project-local `CLAUDE.md`. Does that survive contact with the
two-store split, or do projects just become entries in `PROJECTS.md` plus a `wiki/`
subtree?
*Default: the latter. Per-project folders fragment the graph (see D3); a project is
a view, not a silo.*

---

## R. Output and context layers (from #6)

#6 adds two directories that #1–#5 do not: `output/` (reports, presentations,
posts, documents, summaries, visuals) and `ctx/` (sessions, prompts, templates,
rules, snippets).

**R1.** Is `output/` in scope for v1? It is where the system stops being a
knowledge base and becomes a production tool — and it is also the main way a
second brain earns its keep visibly.
*Default: directory exists from day one, populated later. Outputs are versioned
and always carry a manifest of which wiki pages they drew on — otherwise you
cannot tell a stale deliverable from a current one.*

**R2.** Does anything in `output/` ever feed back into `wiki/`? #6's diagram draws
that loop; #4 endorses filing good answers back.
*Default: only via the `synthesis/` route in E6, never automatically. The loop in
#6's diagram is drawn more optimistically than it should be.*

**R3.** Is `ctx/` (prompts, templates, skills, snippets) part of this repo, or does
it live in `.claude/skills` where the harness already looks?
*Default: `.claude/` for anything the harness executes; `ctx/` in the vault only
for prompts you reuse by hand. Duplicating skill definitions in two places is a
maintenance trap.*

**R4.** #6 claims the system "scales with you, not with token limits." That is only
true if retrieval is real (section H) — a vault that must be fully loaded into
context scales exactly with token limits. Confirm retrieval is non-optional rather
than #6's "optional embedding index."
*Default: confirmed non-optional; only the *embedding* part is optional, gated by
eval (H3).*

**R5.** #6's five automations — Ingest, Write, Manage, Review, Maintain. #1–#4 only
really specify Ingest and Maintain. Which of Write / Manage / Review do you
actually want, and are they v1 or later?
*Default: Ingest + Maintain in v1. Review (the morning brief, J4) in v1.5. Write
and Manage later, if at all — they are where scope creep lives.*

---

## S. Reconciling the six sources

**S1.** Where the sources genuinely conflict, which way do we go? The live ones:

| Question | #4 (Karpathy) | #3 (GBrain) | Our default |
|---|---|---|---|
| Retrieval infra | index.md is enough | vector + typed graph + DB | both behind one interface, eval decides |
| Autonomy | supervised, one at a time | 24/7 daemon, 66 crons | supervised → earned autonomy |
| Storage | markdown files | PGLite database | markdown truth, DB as derived index |
| Scale assumed | ~100 sources | 155,795 pages | design for 10k, optimise for 500 |

**S2.** Sources #1 and #2 are popularizations and should be treated as such. #1
attributes two direct quotes to Karpathy that do not appear in the actual gist text
(#4). #2's setup steps contain errors — it describes a "Claude panel inside
Obsidian" that does not exist, and its MCP invocation and port are worth verifying
before following. Both are useful for *framing* and unreliable for *implementation*.
*Confirm you are happy to treat #3, #4, #5, #6 as the load-bearing sources.*

**S3.** The one claim all six make and none test: that compilation beats retrieval.
See M2. This remains the most valuable thing in the pile.
