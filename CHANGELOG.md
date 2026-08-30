# Changelog

Notable changes, newest first. Started 30 August 2026; earlier work is in the git history
and in [`docs/decisions.md`](docs/decisions.md).

## 2026-08-30

### Added — due-date reminders

The brief runs on a fixed schedule and reports what is coming. That left a gap: an item due
on Friday appeared in Monday's brief, then nothing happened on Friday itself.

`scripts/due_check.py` runs daily at 07:30 and emails only when something is **overdue, due
today, or due tomorrow**. On any other day it sends nothing.

Silence is the point. A daily message that usually says "nothing due" teaches you to ignore
the channel, and then the one that matters is ignored too.

An overdue item stops sending daily reminders after **14 days** and appears in the brief
only. Reminding forever is the same failure by a slower route.

Registered by `install_schedule.py` alongside the other tasks. `--due-time` changes when it
runs; `--no-due-check` skips it.

### Changed — brief format and register

The brief reported on the system's own activity. It now reports on your work.

Removed: page and source counts, commentary on the compiler's reasoning, headings that
existed only to say a section was empty, file paths in the summary, and restatements of what
you had already told it.

Sections are now `Now`, `Soon`, `Still open`, `Worth knowing`, ordered by deadline rather
than by category. The summary fits a phone screen; drafted artifacts sit below it and are
uncapped.

`brief`, `close` and `ask` now follow a fixed register: neutral and plain, following Orwell's
six rules. No stock figures of speech, shorter words over longer, active over passive,
everyday English over jargon, and every removable word removed.

### Added — `/ingest-all`

Compiles the whole inbox with one approval rather than one per source. It plans the batch
first, which also lets it see across sources: three notes about the same thing produce one
loop rather than three, and an entity mentioned once in each of three sources crosses the
promotion threshold only when they are considered together.

It stops and asks if a source would touch more than 15 pages, if a file is unreadable, or if
two sources in the same batch contradict each other.

Prefer `/ingest` until you have watched the compiler handle twenty or so sources correctly.

### Changed — the brief email

It sent raw markdown, so mail clients displayed the asterisks, backticks and the YAML
frontmatter. It now strips the frontmatter, renders the markdown, and sends HTML with the
markdown as a plain-text alternative.

Flagged high priority. The subject gains `· decisions waiting` when an unresolved decide-now
section exists. Outlook, Apple Mail and Thunderbird honour priority flags; Gmail largely
ignores them, so a filter on the subject is more reliable there.

### Fixed

- **`/ingest` ignored `attachment:`.** A PDF captured through Telegram would have compiled
  from its one-line stub, never opening the document. The frontmatter contract is now
  documented in `CLAUDE.md` and read at the start of every compile.
- **Scheduled tasks would not run on battery**, aborted if unplugged, and skipped a missed
  occurrence permanently — Windows' defaults, which on a laptop mean the brief silently never
  happens. All three corrected, and the brief may now wake a sleeping machine.
- **The brief never looked at the inbox.** Capture is automatic and compilation is not, so
  material could accumulate unseen. The brief now counts uncompiled items and reports
  anything waiting more than two weeks.
- **Telegram bot commands became notes.** `/start`, `/revoke` and similar are now skipped.
- `CLAUDE.md` was missing `/bootstrap` and `/close` from its operations table and still
  carried build-order markers from when the skills were being written.
- Three skills asserted a weekly cadence, which the user sets.
- `init_vault.py --help` ran the script instead of printing help.

### Changed — project name

`second-brain` became **`loose-ends`**. The old name is shared with thousands of
repositories and says nothing about what this one does differently. Repository, MCP server
and email subject all renamed.
