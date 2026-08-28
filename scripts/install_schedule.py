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


def harden(name: str, wake: bool = False) -> None:
    """Undo Windows' laptop-hostile defaults.

    Out of the box a scheduled task refuses to start on battery, aborts if you unplug
    mid-run, and silently skips a missed occurrence forever. On a laptop that means the
    brief quietly never happens — which is worse than not scheduling it at all, because
    you think it is handled.

    `wake` additionally lets the task wake a sleeping machine. Worth it for the brief,
    which happens weekly; not for the daily capture, which is not worth waking a laptop
    for. Wake timers are typically allowed on mains power and disabled on battery, so on
    battery this degrades to StartWhenAvailable — late rather than never.
    """
    ps = (
        f"$s = New-ScheduledTaskSettingsSet "
        f"-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable "
        f"{'-WakeToRun ' if wake else ''}"
        f"-MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 1); "
        f"Set-ScheduledTask -TaskName '{name}' -Settings $s | Out-Null"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"    warning: could not adjust settings — {(r.stderr or '').strip()[:200]}")


def create(name: str, mode: str, sched: list[str], when: str, wake: bool = False) -> bool:
    remove(name)
    cmd = f'"{PY}" "{AUTOPILOT}" {mode}'
    code, out = schtasks(["/create", "/tn", name, "/tr", cmd,
                          *sched, "/st", when, "/f"])
    print(f"  {'created' if code == 0 else 'FAILED'}: {name} — {when}")
    if code != 0:
        print(f"    {out[:300]}")
        return False
    harden(name, wake=wake)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cadence", default="weekly",
                    choices=["daily", "weekly", "fortnightly"],
                    help="how often the brief writes and sends itself")
    ap.add_argument("--day", default="MON", choices=DAYS,
                    help="which day (ignored when --cadence daily)")
    ap.add_argument("--time", default="08:00", help="what time, HH:MM")
    ap.add_argument("--capture-time", default="18:00", help="daily Telegram drain, HH:MM")
    ap.add_argument("--no-capture", action="store_true", help="skip the daily capture task")
    ap.add_argument("--remove", action="store_true", help="remove both tasks")
    args = ap.parse_args()

    if args.remove:
        print("Removing scheduled tasks:")
        remove(WEEKLY)
        remove(CAPTURE)
        return

    if not PY.is_file():
        sys.exit(f"No venv python at {PY}. Create it first — see README.")

    # Windows has no fortnightly; WEEKLY with /mo 2 means every other week.
    sched = {
        "daily":       ["/sc", "DAILY"],
        "weekly":      ["/sc", "WEEKLY", "/d", args.day],
        "fortnightly": ["/sc", "WEEKLY", "/mo", "2", "/d", args.day],
    }[args.cadence]

    when = {
        "daily":       f"every day at {args.time}",
        "weekly":      f"every {args.day} at {args.time}",
        "fortnightly": f"every other {args.day} at {args.time}",
    }[args.cadence]

    print("Registering scheduled tasks:")
    ok = create(WEEKLY, "--weekly", sched, args.time, wake=True)
    if not args.no_capture:
        ok &= create(CAPTURE, "--capture", ["/sc", "DAILY"], args.capture_time)

    if ok:
        print(f"\nThe brief now writes and emails itself {when}.")
        print("\nChange your mind — just re-run with different flags:")
        print("  python scripts/install_schedule.py --cadence daily --time 07:30")
        print("  python scripts/install_schedule.py --cadence weekly --day SAT --time 09:00")
        print("\nRun it now:  schtasks /run /tn SecondBrain-WeeklyBrief")
        print("Stop it:     python scripts/install_schedule.py --remove")
    else:
        sys.exit("Some tasks failed to register — see above.")


if __name__ == "__main__":
    main()
