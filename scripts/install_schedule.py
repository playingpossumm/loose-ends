"""Register the autopilot as Windows scheduled tasks.

Nothing pushes you until this runs. Without it you have to remember to run /brief, which is
the exact habit the weekly brief exists to replace.

    python scripts/install_schedule.py                       # defaults: Mon 08:00 weekly, daily 18:00 capture
    python scripts/install_schedule.py --day TUE --time 09:30
    python scripts/install_schedule.py --weekly-only
    python scripts/install_schedule.py --remove

Tasks run whether or not Claude Code is open. They do not run while the machine is off —
Windows fires a missed task at next login, so a laptop closed on Monday gets its brief on
Tuesday rather than never.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / ".venv" / "Scripts" / "python.exe"
AUTOPILOT = ROOT / "scripts" / "autopilot.py"

WEEKLY = "SecondBrain-WeeklyBrief"
CAPTURE = "SecondBrain-Capture"
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def schtasks(args: list[str]) -> tuple[int, str]:
    r = subprocess.run(["schtasks"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def remove(name: str) -> None:
    code, out = schtasks(["/delete", "/tn", name, "/f"])
    print(f"  {'removed' if code == 0 else 'not present'}: {name}")


def create(name: str, mode: str, sched: list[str], when: str) -> bool:
    remove(name)
    cmd = f'"{PY}" "{AUTOPILOT}" {mode}'
    code, out = schtasks(["/create", "/tn", name, "/tr", cmd,
                          *sched, "/st", when, "/f"])
    print(f"  {'created' if code == 0 else 'FAILED'}: {name} — {when}")
    if code != 0:
        print(f"    {out[:300]}")
    return code == 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--day", default="MON", choices=DAYS, help="weekly brief day")
    ap.add_argument("--time", default="08:00", help="weekly brief time, HH:MM")
    ap.add_argument("--capture-time", default="18:00", help="daily Telegram drain, HH:MM")
    ap.add_argument("--weekly-only", action="store_true", help="skip the daily capture task")
    ap.add_argument("--remove", action="store_true", help="remove both tasks")
    args = ap.parse_args()

    if args.remove:
        print("Removing scheduled tasks:")
        remove(WEEKLY)
        remove(CAPTURE)
        return

    if not PY.is_file():
        sys.exit(f"No venv python at {PY}. Create it first — see README.")

    print("Registering scheduled tasks:")
    ok = create(WEEKLY, "--weekly", ["/sc", "WEEKLY", "/d", args.day], args.time)
    if not args.weekly_only:
        ok &= create(CAPTURE, "--capture", ["/sc", "DAILY"], args.capture_time)

    if ok:
        print(f"\nThe brief now writes and emails itself every {args.day} at {args.time}.")
        print("Check it worked:  schtasks /query /tn SecondBrain-WeeklyBrief")
        print("Run it now:       schtasks /run /tn SecondBrain-WeeklyBrief")
        print("Stop it:          python scripts/install_schedule.py --remove")
    else:
        sys.exit("Some tasks failed to register — see above.")


if __name__ == "__main__":
    main()
