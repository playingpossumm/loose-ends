"""Run the brain unattended.

Without this, nothing pushes you — you have to remember to run /brief, which is exactly
the problem the weekly brief exists to solve. This is what makes the system act on its own.

    python scripts/autopilot.py --capture   # drain Telegram into the inbox
    python scripts/autopilot.py --weekly    # drain, write the brief, email it

--weekly drives Claude Code headlessly to run the /brief skill, then sends the result.
Permission mode is acceptEdits: it may write to the vault, nothing more.

Install as scheduled tasks with scripts/install_schedule.py.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()
PY = ROOT / ".venv" / "Scripts" / "python.exe"
LOG = ROOT / "autopilot.log"

BRIEF_PROMPT = (
    "Run the /brief skill. Write the weekly brief to briefs/ in the vault, following the "
    "skill exactly — including the decide-now section with closing artifacts, and the "
    "coverage note. Do not ask me anything; I am not at the keyboard. If there is nothing "
    "worth reporting, still write the brief and say so plainly."
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
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
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

        tail = "\n".join(LOG.read_text(encoding="utf-8").splitlines()[-25:])
        msg = EmailMessage()
        msg["Subject"] = f"Loose ends — {stage} did not run"
        msg["From"] = env["BRAIN_SMTP_USER"]
        msg["To"] = env["BRAIN_EMAIL_TO"]
        msg["Importance"] = "High"
        msg.set_content(
            f"The scheduled {stage} failed at {datetime.now():%Y-%m-%d %H:%M}.\n\n"
            f"Nothing was sent. The last 25 log lines:\n\n{tail}\n\n"
            f"To retry by hand:\n"
            f"  cd {ROOT}\n"
            f"  .venv\\Scripts\\python.exe scripts\\autopilot.py --weekly\n\n"
            f"If the log mentions OAuth, run `claude` once interactively to sign in again.\n"
        )
        with smtplib.SMTP(env["BRAIN_SMTP_HOST"],
                          int(env.get("BRAIN_SMTP_PORT", "587")), timeout=30) as s:
            s.starttls()
            s.login(env["BRAIN_SMTP_USER"], env["BRAIN_SMTP_PASS"])
            s.send_message(msg)
        log("report: failure email sent")
    except Exception as e:  # noqa: BLE001 — reporting must never mask the original error
        log(f"report: could not send failure email — {type(e).__name__}: {e}")


def capture() -> bool:
    return run([str(PY), str(ROOT / "scripts" / "telegram_capture.py"), "--once"],
               "telegram capture", timeout=180, retries=2)


def weekly() -> bool:
    capture()  # fold in anything sent from the phone before writing the brief

    claude = find_claude()
    if not claude:
        log("weekly: FAILED — could not find the Claude Code binary")
        return False

    before = {p.name for p in (VAULT / "briefs").glob("*.md")}
    if not run([str(claude), "-p", BRIEF_PROMPT,
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

    return run([str(PY), str(ROOT / "scripts" / "send_brief.py")],
               "email brief", timeout=180, retries=2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--capture", action="store_true", help="drain Telegram into the inbox")
    g.add_argument("--weekly", action="store_true", help="drain, write the brief, email it")
    args = ap.parse_args()

    log("=" * 60)
    if not wait_for_network():
        # No network means no work and no way to report it. Exit non-zero so the failure is
        # visible in Task Scheduler, but send nothing — the email could not leave either.
        log("done: SKIPPED (no network)")
        sys.exit(1)

    stage = "capture" if args.capture else "brief"
    ok = capture() if args.capture else weekly()
    log(f"done: {'ok' if ok else 'FAILED'}")
    if not ok:
        report_failure(stage)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
