# Writing style

The register used across this project's README, docs, skills and commit messages. Copy the
block below into another project's `CLAUDE.md`, or paste it into a session, to apply it there.

---

## Handoff prompt

```
Write everything in this project — documentation, README, comments, commit messages, and any
prose you produce — in the following register.

REGISTER

Neutral, straightforward and formal. It should read like a reference work or a well-edited
article: someone stating what is true, in order, without performing. Not marketing, not a
blog post, not a chat message.

ORDER, WHICH MATTERS MORE THAN ANY OTHER RULE HERE

Open every section with what the thing does, in the plainest words available. The reasoning
behind it comes second, in a line or two, or it does not appear at all.

The failure this prevents is a section that spends three sentences justifying a choice and
reaches the behaviour in the fourth. By then the reader has been asked to accept an argument
about a thing they have not yet been told the shape of.

  Bad:   Compiling every source by hand is friction, and compiling every source
         automatically risks a wrong date. The nightly pass splits the difference: a wrong
         page costs a regeneration, while a wrong date costs a reminder that never arrives,
         so only the first kind is written unattended.
  Good:  The daily 18:00 pass compiles what it can safely handle without you and leaves
         everything else alone, planning each source first and then deciding from what that
         plan would write.
         [table]
         A wrong page only costs a regeneration, whereas a wrong date costs a reminder that
         never arrives, which is why anything touching a date waits for you.

Where a feature is one the reader may never have seen before, the first sentence is what it
does for them in ordinary language, before any mechanism at all.

  Bad:   Silence is the point. A daily message that usually says nothing due trains you to
         ignore the channel.
  Good:  A nudge is a short deadline reminder arriving on the exact day something is due,
         and it sends the thing itself back to you rather than only naming it, so an article
         you saved and never opened comes with its link attached.

Explain how the thing works, not why it beats the alternative. A comparison gets one line at
the end if it earns one, and usually it does not.

ORWELL'S SIX RULES, WHICH OVERRIDE PREFERENCE

1. Never use a metaphor, simile or figure of speech you are used to seeing in print.
2. Never use a long word where a short one will do.
3. If it is possible to cut a word out, cut it out.
4. Never use the passive where you can use the active.
5. Never use a foreign phrase, a scientific word or a jargon word if there is an everyday
   English equivalent.
6. Break any of these rules sooner than say anything outright barbarous.

SENTENCES

Write full, elaborated sentences that carry a complete thought, and join related clauses with
"and", "so", "because" or "which" wherever the relationship between them is real. The default
should be a sentence with a subordinate clause in it, somewhere between fifteen and thirty
words, and length should vary within that band rather than sitting at one value.

A sentence under about eight words belongs joined to its neighbour. Two or three of them in a
row produce a clipped, lurching cadence that does not read as written by a person, and the
effect compounds when a very short sentence sits next to a long one. "Two repositories."
"Nothing recurring." "Capture only." Each of those was a paragraph opening, and each was
wrong.

Defer the colon. Use it to introduce a table, a list or a code block, and as a label marker,
but write the connection out in words rather than dropping a colon into the middle of a
sentence. A paragraph with two mid-sentence colons in it should be rewritten.

No em dashes anywhere. A comma or a full stop does the same work.

HEADINGS

A heading is a label, not a sentence and never a question. It names what the section
contains. "What arrives with a reminder" is wrong and "Escalation" is right; "How it works"
is wrong and "Architecture" is right. Prefer a single noun or a short noun phrase.

STRUCTURE

Prose is the default. Bullets and tables are exceptions and both should be rare.

- Use a table when the content is genuinely two-dimensional, meaning a comparison across the
  same axes, a glossary, or a reference index. A table with one row, or with a column that
  repeats the same value, should be a sentence.
- Use bullets when the items are strictly parallel and each is one line. Three or more, or it
  is a sentence with commas.
- Everything else is a paragraph. A document that is mostly tables is a spreadsheet.

Diagrams in fenced code blocks are welcome where a flow or a directory tree is clearer shown
than described.

Cut a section that does not earn its place rather than shortening it. A reader who wanted
that material would have gone looking for it somewhere more specific.

Do not repeat what an adjacent element already says. A detail line under a dated heading does
not restate the date, a paragraph under a logo does not restate the tagline, and a caption
does not name what the reader can already see.

FACTS

State the fact and stop. Do not soften it, do not build up to it, and do not restate it
afterwards in different words.

- Give the specific number, name or date. "Four items", not "a number of items". "Due Sunday
  6 September", not "the deadline is approaching".
- Where a system can be configured, describe the real configuration in front of you as the
  base case, with its actual days and times, and then say which values are adjustable.
  A description written in placeholders is one the reader cannot check.
- Absolute dates, never relative ones, in anything read more than once. "Tomorrow" means
  something different on Thursday from what it meant on Monday.
- Digits and standard symbols, so 75%, 20 minutes and $40, never "75 per cent".
- Do not do arithmetic on the reader's behalf. "Six working days, three of them away" is a
  calculation nobody asked for.
- Absence is not information. Do not write "no record exists" or "nothing has changed since"
  unless the absence is itself the subject.

WHAT NEVER APPEARS

- Opening lines about what the document covers, and closing summaries of what it just said.
- A closing clause arguing why the item matters. The reader knows why their own work matters,
  and saying it back to them is padding.
- Enthusiasm, encouragement, or adjectives rating the work as important, exciting or
  powerful. Something described accurately is convincing, and something described
  enthusiastically is not believed.
- Exclamation marks.
- Hedging that carries no information, such as "it might be worth considering whether to".
- Commentary on your own reasoning or process, unless the process is the subject.

EXPLAINING A DECISION

When something was chosen over an alternative, say what the alternative was and why it lost.
When something is a known weakness, say so plainly rather than omitting it. When a mistake was
corrected, record the mistake alongside the correction, because the error is usually the more
useful half.

EXAMPLES

  Bad:  This has been sitting unresolved for some time now.
  Good: Open since 12 August.

  Bad:  It might be worth considering whether to revisit the schema.
  Good: Decide whether the schema needs a title field.

  Bad:  How delivery is ensured
  Good: Reliability

  Bad:  We're excited to introduce a powerful new capability!
  Good: Nudges now go out twice a day rather than once.

  Bad:  Fast. Simple. Free. No server required.
  Good: It runs on your own machine, so there is no server to pay for and nothing to keep
        running between uses.

  Bad:  Two repositories. This one holds the system and no content; vault/ is a separate
        private one, gitignored here.
  Good: Your own knowledge and memory go into vault/, a private repository you set up
        separately and which is gitignored here.

  Bad:  At a few hundred pages an index file and grep are faster and easier to inspect than
        a vector store, and they fail visibly.
  Good: Two mechanisms work together, both of them reading plain files on disk. The first is
        index.md, a generated catalogue listing every page with its one-line summary and
        grouped by subject, which a question is matched against to narrow a few hundred
        pages down to a handful.
```
