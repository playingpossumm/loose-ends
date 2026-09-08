"""Run the brain unattended.

Without this, nothing pushes you — you have to remember to run /brief, which is exactly
the problem the weekly brief exists to solve. This is what makes the system act on its own.

    python scripts/autopilot.py --capture          # drain Telegram, compile what is safe
    python scripts/autopilot.py --weekly           # drain, write the brief, email it
    python scripts/autopilot.py --weekly-catchup   # second attempt the next morning

--weekly and --weekly-catchup drive Claude Code headlessly to run the /brief skill and then
send the result. Permission mode is acceptEdits: they may write to the vault, nothing more.

--weekly-catchup does one of three things, depending on what happened the night before:

  last night failed        run the full pass and send. The safety net.
  succeeded, nothing new   drain Telegram, send nothing.
  succeeded, new material  ask whether it changes what the reader would do, and revise
                           and resend only if it does.

Every mode waits for the network first. If a run fails for any other reason it emails a
report, because a job you only notice by its absence is not automation.

Install as scheduled tasks with scripts/install_schedule.py.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()
PY = ROOT / ".venv" / "Scripts" / "python.exe"
LOG = ROOT / "autopilot.log"
STATE = ROOT / ".last-brief"

# A catch-up run does nothing if a brief was sent within this many hours. The evening run
# and the morning run are the same delivery, attempted twice — the second exists only to
# cover the first having failed. Running the system twice costs nothing; sending the same
# brief twice costs attention, which is the scarce thing.
CATCHUP_WINDOW_HOURS = 18

# The hour the Apps Script trigger releases a queued brief. Must match the triggers installed
# by scripts/gmail_scheduler/Code.gs. The morning pass uses it to decide whether a revision
# can still catch the release — before it, re-queue and one corrected email goes out; after
# it, the brief has already been delivered and a revision is necessarily a second email.
RELEASE_HOUR = 7

UPDATE_PROMPT = (
    "Run the /brief skill in update mode. A brief already exists in briefs/ for this "
    "period and was sent last night. Material has arrived since. Read the latest brief, "
    "read what is new, and decide whether the new material changes anything a reader would "
    "act on differently — a new deadline, something now due, a loop that is now resolved.\n\n"
    "If it does not, reply with the single word NOCHANGE and write nothing. Captured items "
    "sitting uncompiled are not by themselves a reason to resend; the existing brief already "
    "counts them.\n\n"
    "If it does, revise that same brief file in place, add one line at the top saying what "
    "changed since last night, and follow the skill otherwise. Do not ask me anything; I am "
    "not at the keyboard."
)

INGEST_PROMPT = (
    "Run the /ingest-all skill against the inbox, unattended. Apply the triage in that "
    "skill exactly: plan the whole batch, then write only the sources whose plan touches "
    "`wiki/` alone. Hold every source that would write a dated loop, change a date already "
    "recorded, touch `mem/`, contradict an existing claim, or that reads more than one "
    "way. "
    "Held sources stay in raw/inbox untouched — do not move them, mark them, or write a "
    "holding file. What remains in the inbox is what waited. "
    "For a source that is knowledge and commitment at once, write the source page and hold "
    "the loop. "
    "Do not ask me anything; I am not at the keyboard. A question you would have asked is a "
    "reason to hold, not a reason to guess. Finish by printing one line per source saying "
    "written or held, and for held, which rule caught it. If the inbox is empty, print "
    "NOTHING TO DO and stop."
)

BRIEF_PROMPT = (
    "Run the /brief skill. Write the brief to briefs/ in the vault, following the skill "
    "exactly — the title format, the opening paragraph, and only the sections the skill "
    "defines. Do not ask me anything; I am not at the keyboard. If there is nothing worth "
    "reporting, still write the brief and say so in one sentence."
)


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_claude() -> Path | None:
    """Locate the Claude Code binary. The VS Code extension path carries a version, so
    take the newest rather than pinning one that vanishes on update."""
    for p in (Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claude" / "claude.exe",
              Path.home() / ".local" / "bin" / "claude.exe"):
        if p.is_file():
            return p
    ext = Path.home() / ".vscode" / "extensions"
    if ext.is_dir():
        found = sorted(ext.glob("anthropic.claude-code-*/resources/native-binary/claude.exe"))
        if found:
            return found[-1]
    return None


# How long to wait for a network before giving up. This is a ceiling, not an interval: when
# the machine is online — the normal case — the check passes in well under a second and
# nothing waits at all.
#
# It exists because a task that wakes a sleeping machine starts before Wi-Fi associates,
# which is how the 31 August brief was lost. Running in the evening, while the machine is
# already awake, makes that case rare. Ten minutes covers a slow reconnection; a machine
# that has been awake and offline for ten minutes is not about to come back.
NETWORK_WAIT = 10 * 60
POLL_EVERY = 15


def wait_for_network(limit: int = NETWORK_WAIT) -> bool:
    """Block until the machine can reach the internet. Returns False only if it never does.

    There is no point continuing without a network: every stage needs one, and so does the
    failure email. So the caller stops rather than proceeding to fail on each stage in turn.
    """
    deadline = time.monotonic() + limit
    waited = 0
    while True:
        try:
            urllib.request.urlopen("https://api.anthropic.com/", timeout=8)
            if waited:
                log(f"network: up after waiting {waited}s")
            return True
        except urllib.error.HTTPError:
            # Any HTTP response proves the connection works, whatever the status code.
            if waited:
                log(f"network: up after waiting {waited}s")
            return True
        except Exception:
            if time.monotonic() >= deadline:
                log(f"network: unreachable for {limit // 60} minutes — stopping without "
                    f"running. The next scheduled run will pick this up.")
                return False
            if waited == 0:
                log("network: not up yet, waiting")
            elif waited % 300 == 0:
                log(f"network: still waiting ({waited // 60} min)")
            time.sleep(POLL_EVERY)
            waited += POLL_EVERY


def run(cmd: list[str], label: str, timeout: int = 900, retries: int = 0) -> bool:
    for attempt in range(retries + 1):
        if attempt:
            log(f"{label}: retry {attempt} of {retries} in 30s")
            time.sleep(30)
        log(f"{label}: starting")
        try:
            # PYTHONIOENCODING because a child printing an em-dash to a captured pipe
            # otherwise uses the Windows console codepage, and the log fills with U+FFFD.
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        except subprocess.TimeoutExpired:
            log(f"{label}: TIMED OUT after {timeout}s")
            continue
        out = (r.stdout or "").strip()
        if out:
            for line in out.splitlines()[-6:]:
                log(f"  {line}")
        if r.returncode == 0:
            log(f"{label}: ok")
            return True
        log(f"{label}: FAILED (exit {r.returncode}) {(r.stderr or '').strip()[:300]}")
    return False


def report_failure(stage: str) -> None:
    """Email the failure. A job you only notice by its absence is not automation.

    Uses the same single-recipient sender as everything else, so this cannot reach anyone
    but the owner. Never raises: a failure to report a failure must not hide the log.
    """
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import smtplib
        from email.message import EmailMessage
        from send_brief import REQUIRED, load_env

        env = load_env()
        if [k for k in REQUIRED if not env.get(k)]:
            log("report: skipped, mail is not configured")
            return

        # Deliberately short. This email exists to say one thing — the run happened and
        # broke, so waiting will not fix it — and the log is on disk for anyone who wants
        # detail. It used to carry 25 lines of log tail, which made a failure look like
        # something to read rather than something to act on.
        expired = "oauth" in LOG.read_text(encoding="utf-8")[-4000:].lower()
        fix = ("Run `claude` once and sign in again; the login expired."
               if expired else f"Run: .venv\\Scripts\\python.exe scripts\\autopilot.py --{stage.split()[0]}")

        msg = EmailMessage()
        msg["Subject"] = f"Loose ends — {stage} did not run"
        msg["From"] = env["BRAIN_SMTP_USER"]
        msg["To"] = env["BRAIN_EMAIL_TO"]
        msg["Importance"] = "High"
        msg.set_content(
            f"The {stage} ran at {datetime.now():%H:%M} and failed, so the next scheduled "
            f"run will fail the same way until this is dealt with.\n\n"
            f"{fix}\n\n"
            f"Detail: {LOG}\n"
        )
        with smtplib.SMTP(env["BRAIN_SMTP_HOST"],
                          int(env.get("BRAIN_SMTP_PORT", "587")), timeout=30) as s:
            s.starttls()
            s.login(env["BRAIN_SMTP_USER"], env["BRAIN_SMTP_PASS"])
            s.send_message(msg)
        log("report: failure email sent")
    except Exception as e:  # noqa: BLE001 — reporting must never mask the original error
        log(f"report: could not send failure email — {type(e).__name__}: {e}")


def last_brief_sent() -> datetime | None:
    try:
        return datetime.fromisoformat(STATE.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def mark_brief_sent() -> None:
    STATE.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")


def capture() -> bool:
    return run([str(PY), str(ROOT / "scripts" / "telegram_capture.py"), "--once"],
               "telegram capture", timeout=180, retries=2)


def ingest() -> bool:
    """Compile what is safe to compile, and leave the rest for a person.

    Capture runs unattended and compiling did not, so material accumulated in the inbox
    until someone opened an editor. The triage in the /ingest-all skill makes unattended
    compiling safe by scope rather than by trust: a source whose plan touches only `wiki/`
    is rebuildable from raw/ and cannot cause a reminder to fire wrongly, so it writes
    itself. Anything touching a date, a loop, `mem/`, or an existing claim waits.

    What is left in the inbox afterwards is what waited, which is what the brief reports.
    """
    claude = find_claude()
    if not claude:
        log("ingest: FAILED - could not find the Claude Code binary")
        return False
    before = inbox_count()
    ok = run([str(claude), "-p", INGEST_PROMPT,
              "--permission-mode", "acceptEdits", "--output-format", "text"],
             "ingest", timeout=1800, retries=1)
    if ok:
        log(f"  inbox {before} -> {inbox_count()} ({before - inbox_count()} written, "
            f"{inbox_count()} held)")
    return ok


def staleness() -> str:
    """How long since the vault was last compiled, and how much is waiting.

    Computed here rather than left to the model. The brief skill asks it to check `log.md`
    and work out whether the last ingest was seven or more days ago, which is date
    arithmetic on a file it has to read anyway — reliable most of the time and wrong
    silently the rest. The scheduled brief is the one nobody is watching, so it gets the
    numbers handed to it.
    """
    log_file = VAULT / "log.md"
    if not log_file.is_file():
        return ""
    dates = re.findall(r"^## \[(\d{4}-\d{2}-\d{2})\] ingest",
                       log_file.read_text(encoding="utf-8", errors="replace"), re.M)
    if not dates:
        return ""
    days = (datetime.now().date() - date.fromisoformat(max(dates))).days
    waiting = inbox_count()
    if days < 7 and waiting <= 5:
        return ""
    return (f"\n\nFACTS FOR THE STALENESS LINE, already computed — do not recalculate: "
            f"the vault was last compiled {days} day{'s' if days != 1 else ''} ago, and "
            f"{waiting} item{'s are' if waiting != 1 else ' is'} waiting in the inbox. "
            f"Follow the Staleness section of the skill.")


def due_check(window: str) -> bool:
    """The daily nudge. Routed through here rather than scheduled directly, so it gets the
    same network wait, retry and failure report as the brief. A reminder that dies silently
    on a cold network is the exact failure the brief was rebuilt to prevent."""
    return run([str(PY), str(ROOT / "scripts" / "due_check.py"), "--window", window],
               f"due check ({window})", timeout=180, retries=2)


def inbox_count() -> int:
    return len(list((VAULT / "raw" / "inbox").glob("*.md")))


def refresh(last: datetime) -> bool:
    """Morning pass when last night's brief was queued or delivered.

    Drains Telegram, then updates the brief only if the new material changes what a reader
    would do. Run before the release hour it re-queues, so Gmail delivers the revised brief
    instead of the one written last night and only one email arrives. Run after it, the brief
    is already in the inbox and the revision follows as a second one. The model makes that call — it is the same judgement the brief
    already makes about what is worth reporting. Anything else means a second email most
    mornings, which is how the channel stops being read.
    """
    before = inbox_count()
    capture()
    arrived = inbox_count() - before
    if arrived <= 0:
        log(f"refresh: brief sent {last:%H:%M}, nothing new since — done")
        return True

    log(f"refresh: {arrived} item(s) arrived overnight, checking whether they change the brief")
    claude = find_claude()
    if not claude:
        log("refresh: FAILED — could not find the Claude Code binary")
        return False

    r = subprocess.run([str(claude), "-p", UPDATE_PROMPT + staleness(),
                        "--permission-mode", "acceptEdits", "--output-format", "text"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    out = (r.stdout or "").strip()
    for line in out.splitlines()[-4:]:
        log(f"  {line}")
    if r.returncode != 0:
        log(f"refresh: FAILED (exit {r.returncode}) {(r.stderr or '').strip()[:300]}")
        return False
    if "NOCHANGE" in out.upper():
        log("refresh: nothing that changes what you would do — not resending")
        return True

    in_time = datetime.now().hour < RELEASE_HOUR
    cmd = [str(PY), str(ROOT / "scripts" / "send_brief.py")] + (["--queue"] if in_time else [])
    if in_time:
        log(f"refresh: before the {RELEASE_HOUR:02d}:00 release — re-queuing the revision")
    if run(cmd, "queue update" if in_time else "email update", timeout=180, retries=2):
        mark_brief_sent()
        return True
    return False


def weekly(queue: bool = False) -> bool:
    """Write the brief and mail it.

    queue=True tags the message so Gmail holds it back and an Apps Script trigger releases
    it at 07:00 the next morning. That is the evening run, whose whole purpose is to have
    the brief written before the machine is shut. The morning catch-up passes queue=False:
    by then the release trigger has already fired, so a queued message would wait a week.
    """
    capture()  # fold in anything sent from the phone before writing the brief

    claude = find_claude()
    if not claude:
        log("weekly: FAILED — could not find the Claude Code binary")
        return False

    before = {p.name for p in (VAULT / "briefs").glob("*.md")}
    if not run([str(claude), "-p", BRIEF_PROMPT + staleness(),
                "--permission-mode", "acceptEdits", "--output-format", "text"],
               "write brief", timeout=900, retries=1):
        return False

    after = {p.name for p in (VAULT / "briefs").glob("*.md")}
    new = after - before
    if new:
        log(f"  new brief: {', '.join(sorted(new))}")
    else:
        # It may have updated an existing brief rather than creating one. Send anyway,
        # but say so — a silent no-op is the failure mode worth catching here.
        log("  no new brief file; sending the most recent one")

    cmd = [str(PY), str(ROOT / "scripts" / "send_brief.py")] + (["--queue"] if queue else [])
    if not run(cmd, "queue brief" if queue else "email brief", timeout=180, retries=2):
        return False
    mark_brief_sent()
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--capture", action="store_true",
                   help="drain Telegram, then compile what is safe to compile")
    g.add_argument("--due-check", choices=("morning", "evening"), metavar="WINDOW",
                   help="email the nudges belonging to this window: morning or evening")
    g.add_argument("--weekly", action="store_true", help="drain, write the brief, email it")
    g.add_argument("--weekly-catchup", action="store_true",
                   help="same as --weekly, but do nothing if a brief was already sent in "
                        "the last %d hours. Schedule this the morning after the main run "
                        "so a failed evening still gets delivered." % CATCHUP_WINDOW_HOURS)
    args = ap.parse_args()

    log("=" * 60)
    if not wait_for_network():
        # No network means no work and no way to report it. Exit non-zero so the failure is
        # visible in Task Scheduler, but send nothing — the email could not leave either.
        log("done: SKIPPED (no network)")
        sys.exit(1)

    if args.weekly_catchup:
        last = last_brief_sent()
        if last and (datetime.now() - last).total_seconds() < CATCHUP_WINDOW_HOURS * 3600:
            ok = refresh(last)
            log(f"done: {'ok' if ok else 'FAILED'}")
            if not ok:
                report_failure("brief refresh")
            sys.exit(0 if ok else 1)
        log("catch-up: no brief went out last night, running the full pass")

    if args.capture:
        # Drain, then compile what is safe to compile. Draining alone left the inbox
        # growing until someone opened an editor, which is the friction the triage exists
        # to remove.
        stage, ok = "capture", capture() and ingest()
    elif args.due_check:
        stage, ok = f"due check ({args.due_check})", due_check(args.due_check)
    else:
        # The evening run queues for a 07:00 release; the catch-up has missed that window
        # and sends directly, which is the point of it.
        stage, ok = "brief", weekly(queue=args.weekly)
    log(f"done: {'ok' if ok else 'FAILED'}")
    if not ok:
        report_failure(stage)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
