"""Send the most recent weekly brief to exactly one address: yourself.

THE IMPORTANT PROPERTY OF THIS FILE
-----------------------------------
There is no recipient parameter. Not in the function signature, not on the command line,
not anywhere. The destination is read once from BRAIN_EMAIL_TO and nothing can override it.

That is deliberate. The vault drafts emails to other people (see /close), and the rule is
that those are handed to you, never transmitted. Once a system holds SMTP credentials, an
instruction saying "don't send to third parties" is only a suggestion — a confused or
compromised agent can ignore prose. It cannot ignore a missing code path.

So: this module can reach exactly one mailbox, and it is yours.

Usage:
    python scripts/send_brief.py --dry-run    # print what would be sent
    python scripts/send_brief.py              # send it
"""

from __future__ import annotations

import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

VAULT = Path(os.environ.get("BRAIN_VAULT", Path(__file__).resolve().parent.parent)).resolve()

REQUIRED = ("BRAIN_SMTP_HOST", "BRAIN_SMTP_USER", "BRAIN_SMTP_PASS", "BRAIN_EMAIL_TO")


def load_env() -> dict[str, str]:
    """Read .env from the vault root. No dependency on python-dotenv."""
    env = dict(os.environ)
    envfile = VAULT / ".env"
    if envfile.is_file():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip("'\""))
    return env


def latest_brief() -> Path:
    briefs = sorted((VAULT / "briefs").glob("*.md"))
    if not briefs:
        sys.exit("No briefs yet. Run /brief in the vault first.")
    return briefs[-1]


def build(brief: Path, to: str, sender: str) -> EmailMessage:
    body = brief.read_text(encoding="utf-8")
    msg = EmailMessage()
    msg["Subject"] = f"Brain — {brief.stem}"
    msg["From"] = sender
    msg["To"] = to  # the only assignment to this header in the codebase
    msg.set_content(body)
    return msg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print the message instead of sending")
    args = ap.parse_args()

    env = load_env()
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        sys.exit(
            "Missing config: "
            + ", ".join(missing)
            + f"\nCopy {VAULT / '.env.example'} to .env and fill it in."
        )

    brief = latest_brief()
    msg = build(brief, to=env["BRAIN_EMAIL_TO"], sender=env["BRAIN_SMTP_USER"])

    if args.dry_run:
        print(f"--- would send {brief.name} to {env['BRAIN_EMAIL_TO']}")
        print(f"--- via {env['BRAIN_SMTP_HOST']}:{env.get('BRAIN_SMTP_PORT', '587')}\n")
        print(msg)
        return

    port = int(env.get("BRAIN_SMTP_PORT", "587"))
    with smtplib.SMTP(env["BRAIN_SMTP_HOST"], port, timeout=30) as s:
        s.starttls()
        s.login(env["BRAIN_SMTP_USER"], env["BRAIN_SMTP_PASS"])
        s.send_message(msg)
    print(f"Sent {brief.name} to {env['BRAIN_EMAIL_TO']}")


if __name__ == "__main__":
    main()
