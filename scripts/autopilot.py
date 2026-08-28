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


def run(cmd: list[str], label: str, timeout: int = 900) -> bool:
    log(f"{label}: starting")
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"{label}: TIMED OUT after {timeout}s")
        return False
    out = (r.stdout or "").strip()
    if out:
        for line in out.splitlines()[-6:]:
            log(f"  {line}")
    if r.returncode != 0:
        log(f"{label}: FAILED (exit {r.returncode}) {(r.stderr or '').strip()[:300]}")
        return False
    log(f"{label}: ok")
    return True


def capture() -> bool:
    return run([str(PY), str(ROOT / "scripts" / "telegram_capture.py"), "--once"],
               "telegram capture", timeout=180)


def weekly() -> bool:
    capture()  # fold in anything sent from the phone before writing the brief

    claude = find_claude()
    if not claude:
        log("weekly: FAILED — could not find the Claude Code binary")
        return False

    before = {p.name for p in (VAULT / "briefs").glob("*.md")}
    if not run([str(claude), "-p", BRIEF_PROMPT,
                "--permission-mode", "acceptEdits", "--output-format", "text"],
               "write brief", timeout=900):
        return False

    after = {p.name for p in (VAULT / "briefs").glob("*.md")}
    new = after - before
    if new:
        log(f"  new brief: {', '.join(sorted(new))}")
    else:
        # It may have updated an existing brief rather than creating one. Send anyway,
        # but say so — a silent no-op is the failure mode worth catching here.
        log("  no new brief file; sending the most recent one")

    return run([str(PY), str(ROOT / "scripts" / "send_brief.py")], "email brief", timeout=180)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--capture", action="store_true", help="drain Telegram into the inbox")
    g.add_argument("--weekly", action="store_true", help="drain, write the brief, email it")
    args = ap.parse_args()

    log("=" * 60)
    ok = capture() if args.capture else weekly()
    log(f"done: {'ok' if ok else 'FAILED'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
