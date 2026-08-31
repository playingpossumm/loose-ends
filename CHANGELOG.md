# Changelog

Notable changes, newest first. Started 30 August 2026; earlier work is in the git history
and in [`docs/decisions.md`](docs/decisions.md).

## 2026-08-31

### Changed — brief rewritten after first real use

Read against actual output, three faults were clear.

**Sentences broke mid-clause.** The markdown converter had `nl2br` enabled, which turns every
newline in the source into a line break. The source is hard-wrapped at 90 characters, so
every wrap became a visible break in the email. Removed.

**The title was a filename.** It is now `Morning Brief — Monday, 31 August 2026`, or
`Weekend Brief` at the weekend, and the email subject is taken from that heading rather than
the file stem.

**Two sections carried no information.** `Still open` and `Worth knowing` are gone, along
with every line of the form "the vault has no record", "no calendar event exists", "nothing
added since". Absence is not an action.

`Now` now means **today**: what is to be done today, or worked on continuously today.
Nothing further out. `Soon` covers this week, and early next week only when it needs
preparing for now.

**Don't forget** replaces the two that were cut. It resurfaces things captured and not
returned to — an article dumped and unread, a note about something to look into. Those are
the items that would otherwise be lost, which is what the system is for.

The brief also no longer explains the user's own work back to them. It states what and when,
not how.

### Added — capture refuses credentials

A bank password was sent to the vault and written to disk. The compiler refused to compile
it, which is the rule working, but that is one step too late: capture writes the file first,
and the vault is a git repository. A password is easier to never store than to remove.

Telegram capture now checks for labelled credentials before writing anything — `password:`,
`pin:`, `api key =`, seed phrases, PEM private key blocks, and provider token prefixes. A
match is refused, nothing is written, and the reason is printed.

The test errs toward refusing. It matches the labelled form rather than every high-entropy
string, because losing one note costs less than storing one password. Verified against twelve
messages, including the one that got through and the near misses that must not trip it:
"remind me to change my password", "token economics is interesting".

The vault records that a refusal happened without recording what was refused. That audit
trail is kept on purpose.

### Changed — delivery is now guaranteed in layers

The 31 August brief was lost and nothing said so. The absence was the only signal, which is
the same weakness as a brief you have to remember to run.

Six layers now stand between a scheduled brief and a missed one, each covering a way the
previous one fails:

1. **Run in the evening**, while the machine is awake, rather than in the morning when it
   may be asleep and Windows has disabled wake timers on battery.
2. **Wait up to ten minutes for the network**, because a task that wakes the machine starts
   before Wi-Fi associates.
3. **Stop rather than half-run** if the network never arrives. Every stage needs one, and so
   does the failure email.
4. **Retry each stage** — twice for capture and mail, once for the brief.
5. **A second attempt the next morning** if the evening failed for any reason.
6. **Report the failure by email** if it still fails, with the log tail and what to check.

Windows' defaults work against all of it, so the installer now overrides three: tasks may
start on battery, survive being unplugged, and run a missed occurrence at the next
opportunity rather than skipping it permanently. The task time limit went from one hour to
two to accommodate the network wait.

The same applies to the due-date reminder, which runs daily on the same schedule.

### Added — a second run the next morning

Running the system costs nothing, so the brief is attempted twice: 19:00 the evening before,
and 08:00 the next morning. What the morning run does depends on what happened overnight.

**If last night failed** — dead network, laptop shut early, expired login — it runs the full
pass and sends. That is the safety net.

**If last night succeeded**, it drains Telegram and then asks whether anything that arrived
overnight changes what you would actually do: a new deadline, something now due, a loop now
resolved. If not, it sends nothing. If so, it revises last night's brief in place, notes at
the top what changed, and sends the update.

The judgement is the model's, and it is the same one the brief already makes about what is
worth reporting. A fixed rule would mean a second email most mornings, since captured items
arrive most evenings — and that is how a channel stops being read. Items sitting uncompiled
are explicitly not a reason to resend; the existing brief already counts them.

This also recovers what the evening schedule gave up: a brief written at 19:00 cannot include
anything captured overnight, and now the morning pass folds it in when it matters.

`--catchup-time` moves it; `--no-catchup` skips it.

### Changed — the brief runs the evening before

It ran at 07:00 on the day you read it, which on a sleeping laptop depends on Windows wake
timers — and Windows disables those on battery. The run then waits until the machine is next
opened, possibly hours after it was useful.

It now runs at 19:00 the evening before, while the machine is awake and online, so the brief
is waiting in the morning. Capture runs at 18:00, an hour ahead, so the brief includes
everything from that day.

The cost is that an evening brief cannot include anything captured overnight. For a periodic
review that is not worth the loss of reliability.

`/bootstrap` now asks when you will *read* the brief rather than when to send it, and
schedules the run for the evening before.

### Fixed — the brief was lost to a cold network

The 07:00 run woke the machine and started before Wi-Fi associated. Telegram failed on a
connection error and Claude Code could not refresh its OAuth token. Both looked like faults
in the log; neither was. No brief was written and nothing said so — the absence was the only
signal.

`autopilot.py` now **waits for the network before doing anything**, polling for up to ten
minutes. If it never arrives the run stops without attempting: every stage needs a network,
and so does the failure email, so continuing only produces a cascade of misleading errors.
The scheduled task's time limit went from one hour to two to accommodate the wait.

Each stage now retries — twice for capture and mail, once for the brief.

If a run still fails, it **emails you**: what failed, the last 25 log lines, the command to
retry by hand, and a note to re-authenticate if the log mentions OAuth. Finding out by
noticing an absent email has the same weakness as a brief you have to remember to run.

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

### Changed — overdue items are forced to a decision

An item more than 14 days past its date now appears at the top of the brief with three
options and nothing else: drop it, set a new date, or do it now. The daily due check stops
reminding at 14 days so the brief can take over.

`/close` asks which of the three before drafting anything, and records the reason when
something is dropped. An item nobody has acted on for three weeks is either dead or
mis-dated; both are fine answers, and leaving it open is not.

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
