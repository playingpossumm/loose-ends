---
name: capture
description: File something into the vault inbox — a link, a PDF, an image, a thought, or the current Claude Code session. Use when the user says "capture this", "file this", "save this to my brain", or wants to keep something from the conversation. Does not compile; that is /ingest.
---

# capture

Put something into `raw/inbox/` so `/ingest` can compile it later. Capture is deliberately
dumb and fast — it files, it does not think. Friction here kills the whole system, so never
interrogate the user before filing.

This is one of several doors into `raw/inbox/` — alongside the Telegram script, the Obsidian
Web Clipper, `brain_capture` over MCP, and plain drag-and-drop. They all land in the same
folder and produce the same shape of file, so `/ingest` never needs to care which was used.

## What to file

The argument, or if there is none, infer from context:

| Input | Action |
|---|---|
| URL | fetch it, save as markdown with the original URL in frontmatter |
| Local file path | copy into `raw/inbox/`, keep the original name |
| Image / screenshot | copy in, **and write a text transcription alongside it** — the transcription is what gets compiled; the image stays as provenance |
| Free text / a thought | write it verbatim as a note. Preserve the user's wording. |
| "this session" / "this conversation" | write the substance of the conversation so far as a transcript |

## How

1. Generate an id: `YYYY-MM-DD-<short-slug>`.
2. Write `raw/inbox/<id>.md` with this frontmatter, then the content verbatim:

```yaml
---
id: <id>
captured: YYYY-MM-DD
kind: article | pdf | image | note | transcript
origin: <url, file path, or "conversation">
title: <short human title>
status: uncompiled
---
```

3. For images: save the image file beside it as `<id>.<ext>`, add `image: <id>.<ext>` to
   the frontmatter, and put your transcription in the body. Note in the body that the text
   is a transcription, so `/ingest` cites the image rather than treating the text as
   original.
4. Confirm in one line: what was filed, its id, and that it is uncompiled.

## Rules

- **Preserve wording.** Never summarise or clean up at capture time. Compilation is where
  interpretation happens; capture is a photocopier.
- **Never edit anything already in `raw/`.** It is immutable.
- **Do not compile.** Do not write to `wiki/`, `loops/`, or `index.md`. That is `/ingest`.
- **If it already exists** (same content hash or same origin URL), say so and do not
  duplicate — but note the re-encounter in the existing file's body with today's date. A
  repeat encounter is a signal that the material matters.
- **Refuse** passwords, API keys, credentials, and health records. Say you refused and why.
- Never ask more than one clarifying question, and only if you genuinely cannot tell what
  to file.
