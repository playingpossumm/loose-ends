"""Point git at the version-controlled hooks in scripts/hooks.

    python scripts/install_hooks.py
    python scripts/install_hooks.py --check    # report, change nothing

Git looks for hooks inside .git/hooks, which is local to one clone and cannot be committed.
A hook that guards a public repository against publishing private content is worth having in
every clone, so it lives in scripts/hooks and this points core.hooksPath at it.

Run once per clone. Fresh clones start with no hooks at all, which is exactly the state that
let a vault export reach the public repository on 8 September 2026.
"""

from __future__ import annotations

import argparse
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"


def git(*args: str) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report whether the hooks are active, and change nothing")
    args = ap.parse_args()

    if not (HOOKS / "pre-commit").is_file():
        sys.exit(f"No hooks to install. Expected {HOOKS / 'pre-commit'}")

    code, current = git("config", "--get", "core.hooksPath")
    active = code == 0 and current.strip() == "scripts/hooks"

    if args.check:
        print("hooks active" if active else
              f"hooks NOT active (core.hooksPath = {current or 'unset'})")
        sys.exit(0 if active else 1)

    code, out = git("config", "core.hooksPath", "scripts/hooks")
    if code != 0:
        sys.exit(f"Could not set core.hooksPath: {out}")

    # Git on Windows ignores the executable bit, but the same checkout gets used from WSL
    # and from Git Bash, where a hook without +x is skipped in silence. Silence is the one
    # failure mode a guard like this cannot afford.
    for hook in HOOKS.iterdir():
        if hook.is_file():
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print("Hooks installed. pre-commit now blocks vault content, exports and .env files.")
    print("Verify with:  python scripts/install_hooks.py --check")


if __name__ == "__main__":
    main()
