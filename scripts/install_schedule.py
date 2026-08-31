"""Register the autopilot as Windows scheduled tasks.

Nothing pushes you until this runs. Without it you have to remember to run /brief, which is
the exact habit the weekly brief exists to replace.

    python scripts/install_schedule.py --day FRI,SUN --time 19:00
    python scripts/install_schedule.py --cadence daily --time 19:00
    python scripts/install_schedule.py --no-capture --no-due-check   # brief only
    python scripts/install_schedule.py --remove

Five tasks are registered:

  <name>-WeeklyBrief    writes and emails the brief, on the days and time you give
  <name>-BriefCatchup   the next morning: recovers a failed run, or folds in anything
                        that arrived overnight and changes what you would do
  <name>-Capture        drains Telegram into the inbox, daily
  <name>-NudgeMorning   07:00, daily: what is due today, and what is overdue
  <name>-NudgeEvening   19:30, daily: what is due tomorrow

Both nudges are silent unless something is due. A reminder is only useful at the hour you
can act on it, so what is due today arrives with the working day in front of it and what is
due tomorrow arrives with an evening left to prepare in. A loop overrides the split with
`nudge: morning` or `nudge: evening` when its nature disagrees with its date.

Schedule the brief for the EVENING BEFORE the morning you read it. A morning task on a
sleeping laptop depends on Windows wake timers, which Windows disables on battery, so the
run waits until the machine is next opened — possibly hours after it was useful. In the
evening the machine is already awake.

Tasks run whether or not Claude Code is open, on battery as well as mains, and the brief
may wake a sleeping machine. A laptop that is fully powered off runs the task at next
startup, so the brief arrives late rather than never.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / ".venv" / "Scripts" / "python.exe"
AUTOPILOT = ROOT / "scripts" / "autopilot.py"
DUE_CHECK = ROOT / "scripts" / "due_check.py"

WEEKLY = "SecondBrain-WeeklyBrief"
CAPTURE = "SecondBrain-Capture"
DUE_AM = "SecondBrain-NudgeMorning"
DUE_PM = "SecondBrain-NudgeEvening"
CATCHUP = "SecondBrain-BriefCatchup"

# Task names this script registered in earlier versions. Windows keeps a task after the
# script stops creating it, so an upgrade would leave the old one firing beside the new.
LEGACY = ["SecondBrain-DueCheck"]
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
        f"-MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2); "
        f"Set-ScheduledTask -TaskName '{name}' -Settings $s | Out-Null"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"    warning: could not adjust settings — {(r.stderr or '').strip()[:200]}")


def create(name: str, mode: str, sched: list[str], when: str, wake: bool = False,
           script: str | None = None) -> bool:
    remove(name)
    target = script or str(AUTOPILOT)
    cmd = f'"{PY}" "{target}" {mode}'.rstrip()
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
    ap.add_argument("--day", "--days", dest="day", default="MON", metavar="DAY[,DAY...]",
                    help="which day, or a comma-separated list for several deliveries a "
                         "week, e.g. SAT,MON (ignored when --cadence daily). schtasks "
                         "takes a day list on one task, so this stays a single task "
                         "rather than one per day.")
    ap.add_argument("--time", default="19:00",
                    help="what time, HH:MM. Use the evening before you read it.")
    ap.add_argument("--capture-time", default="18:00", help="daily Telegram drain, HH:MM")
    ap.add_argument("--nudge-morning", default="07:00", metavar="HH:MM",
                    help="the morning nudge: what is due today, and what is overdue.")
    ap.add_argument("--nudge-evening", default="19:30", metavar="HH:MM",
                    help="the evening nudge: what is due tomorrow, while there is still a "
                         "night to prepare in.")
    ap.add_argument("--catchup-time", default="08:00",
                    help="second attempt, the morning after the main run. Does nothing if "
                         "the brief already went out. HH:MM")
    ap.add_argument("--no-catchup", action="store_true", help="skip the second attempt")
    ap.add_argument("--no-due-check", action="store_true", help="skip both nudge tasks")
    ap.add_argument("--no-capture", action="store_true", help="skip the daily capture task")
    ap.add_argument("--remove", action="store_true", help="remove every task")
    args = ap.parse_args()

    if args.remove:
        print("Removing scheduled tasks:")
        remove(WEEKLY)
        remove(CATCHUP)
        remove(CAPTURE)
        remove(DUE_AM)
        remove(DUE_PM)
        for name in LEGACY:
            remove(name)
        return

    if not PY.is_file():
        sys.exit(f"No venv python at {PY}. Create it first — see README.")

    # Accept "SAT,MON" / "sat mon" / "SAT, MON". Deduplicate but keep the order given, so
    # the confirmation line reads back the way it was typed.
    days: list[str] = []
    for raw in re.split(r"[,\s]+", args.day.strip().upper()):
        if not raw:
            continue
        if raw not in DAYS:
            sys.exit(f"Not a day: {raw}. Use one or more of {', '.join(DAYS)}.")
        if raw not in days:
            days.append(raw)
    if not days:
        sys.exit("No day given.")
    daylist = ",".join(days)

    # Windows has no fortnightly; WEEKLY with /mo 2 means every other week.
    sched = {
        "daily":       ["/sc", "DAILY"],
        "weekly":      ["/sc", "WEEKLY", "/d", daylist],
        "fortnightly": ["/sc", "WEEKLY", "/mo", "2", "/d", daylist],
    }[args.cadence]

    when = {
        "daily":       f"every day at {args.time}",
        "weekly":      f"every {' and '.join(days)} at {args.time}",
        "fortnightly": f"every other week on {' and '.join(days)} at {args.time}",
    }[args.cadence]

    for name in LEGACY:
        code, _ = schtasks(["/query", "/tn", name])
        if code == 0:
            print(f"Superseded task found:")
            remove(name)

    print("Registering scheduled tasks:")
    ok = create(WEEKLY, "--weekly", sched, args.time, wake=True)
    if not args.no_catchup and args.cadence != "daily":
        # The morning after each delivery day. Same brief, second attempt: it exits at once
        # unless the evening run failed to send.
        after = [DAYS[(DAYS.index(d) + 1) % 7] for d in days]
        ok &= create(CATCHUP, "--weekly-catchup",
                     ["/sc", "WEEKLY", "/d", ",".join(dict.fromkeys(after))],
                     args.catchup_time, wake=True)
    if not args.no_capture:
        ok &= create(CAPTURE, "--capture", ["/sc", "DAILY"], args.capture_time)
    if not args.no_due_check:
        # Two sends, because a reminder is only useful at the hour you can act on it.
        # Morning carries what is due today and what is overdue; evening carries what is due
        # tomorrow, while there is still a night to prepare in. Each loop can override the
        # split with `nudge: morning` or `nudge: evening`.
        #
        # Through autopilot rather than due_check.py directly, so the nudge inherits the same
        # network wait, retries and failure email as the brief. It was scheduled directly
        # until 31 August, which meant a cold network killed the reminder in silence.
        ok &= create(DUE_AM, "--due-check morning", ["/sc", "DAILY"], args.nudge_morning)
        ok &= create(DUE_PM, "--due-check evening", ["/sc", "DAILY"], args.nudge_evening)

    if ok:
        print(f"\nThe brief now writes and emails itself {when}.")
        print("\nChange your mind — just re-run with different flags:")
        print("  python scripts/install_schedule.py --day FRI,SUN --time 19:00")
        print("  python scripts/install_schedule.py --cadence daily --time 19:00")
        print("  python scripts/install_schedule.py --day THU --time 20:00")
        print("\nRun it now:  schtasks /run /tn SecondBrain-WeeklyBrief")
        print("Stop it:     python scripts/install_schedule.py --remove")
    else:
        sys.exit("Some tasks failed to register — see above.")


if __name__ == "__main__":
    main()
