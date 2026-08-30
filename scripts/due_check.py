"""Email a reminder on the day something is due.

The brief runs on a fixed schedule and reports what is coming. That leaves a gap: an item
due on Friday is mentioned in Monday's brief, then nothing happens on Friday itself. This
closes that gap.

It runs daily and sends nothing unless something is overdue, due today, or due tomorrow.
Silence is the normal case. A daily email that usually says "nothing due" trains you to
ignore it, which would also make you ignore the one that matters.

Like scripts/send_brief.py, it has no recipient argument. The destination is read from
BRAIN_EMAIL_TO and cannot be overridden.

    python scripts/due_check.py --dry-run   # print what would be sent
    python scripts/due_check.py             # send if anything is due
"""

from __future__ import annotations

import argparse
import re
import smtplib
import sys
from datetime import date, timedelta
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from send_brief import CSS, REQUIRED, ROOT, VAULT, load_env  # noqa: E402


def read_dated() -> list[dict]:
    """Every open item carrying a due date, from loops/open and loops/dates."""
    out = []
    for folder in ("open", "dates"):
        d = VAULT / "loops" / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="replace")
            due = re.search(r"^due:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
            status = re.search(r"^status:\s*(\w+)", text, re.M)
            if not due or (status and status.group(1) != "open"):
                continue
            title = next(
                (l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")),
                p.stem,
            )
            out.append({
                "path": p.relative_to(VAULT).as_posix(),
                "title": title,
                "due": date.fromisoformat(due.group(1)),
                "body": body_of(text),
            })
    return out


def body_of(text: str) -> str:
    """The page's own text, minus frontmatter and heading — context for the reminder."""
    parts = text.split("---", 2)
    rest = parts[2] if len(parts) > 2 else text
    lines = [l for l in rest.splitlines() if l.strip() and not l.startswith("# ")]
    return "\n".join(lines[:6]).strip()


# How long an overdue item keeps sending daily reminders. After this it appears in the brief
# only. Reminding every day forever is how a channel becomes noise, and a channel you ignore
# is worse than one that never existed.
OVERDUE_NAG_DAYS = 14


def buckets(items: list[dict], today: date) -> dict[str, list[dict]]:
    """Overdue, today, tomorrow. Nothing further out — the brief covers that."""
    overdue = [
        i for i in items
        if i["due"] < today and (today - i["due"]).days <= OVERDUE_NAG_DAYS
    ]
    return {
        "Overdue": sorted(overdue, key=lambda i: i["due"]),
        "Due today": [i for i in items if i["due"] == today],
        "Due tomorrow": [i for i in items if i["due"] == today + timedelta(days=1)],
    }


def render(groups: dict[str, list[dict]], today: date) -> tuple[str, str, str]:
    """Returns subject, plain text, html."""
    counts = {k: len(v) for k, v in groups.items() if v}
    lead = groups["Overdue"] or groups["Due today"] or groups["Due tomorrow"]
    label = "Overdue" if groups["Overdue"] else ("Due today" if groups["Due today"] else "Due tomorrow")
    subject = f"{label}: {lead[0]['title']}" + (f" (+{sum(counts.values()) - 1} more)"
                                               if sum(counts.values()) > 1 else "")

    text, html = [f"{today.isoformat()}", ""], []
    for name, items in groups.items():
        if not items:
            continue
        text.append(f"{name.upper()}")
        html.append(f"<h2>{name}</h2>")
        for i in items:
            when = i["due"].isoformat()
            overdue_by = (today - i["due"]).days
            stamp = f"{when} ({overdue_by} day{'s' if overdue_by != 1 else ''} ago)" \
                if overdue_by > 0 else when
            text += [f"  {i['title']} — {stamp}", f"    {i['body'][:200]}", ""]
            html.append(
                f"<p><strong>{i['title']}</strong><br>"
                f"<span class='when'>{stamp}</span><br>{i['body'][:300]}</p>"
            )
        text.append("")

    text.append("Run /close in the project folder to finish one of these.")
    html.append("<p class='foot'>Run <code>/close</code> in the project folder to finish one.</p>")

    page = (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<style>{CSS} .when{{color:#8a929c;font-size:13px}}</style></head>"
        f"<body><div class='wrap'><div class='card'>{''.join(html)}</div></div></body></html>"
    )
    return subject, "\n".join(text), page


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print instead of sending")
    args = ap.parse_args()

    today = date.today()
    groups = buckets(read_dated(), today)

    if not any(groups.values()):
        print(f"{today}: nothing overdue, due today, or due tomorrow. No email sent.")
        return

    env = load_env()
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        sys.exit("Missing config: " + ", ".join(missing) + f"\nSee {ROOT / '.env.example'}.")

    subject, text, html = render(groups, today)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = env["BRAIN_SMTP_USER"]
    msg["To"] = env["BRAIN_EMAIL_TO"]  # the only assignment to this header
    msg["Importance"] = "High"
    msg["X-Priority"] = "1 (Highest)"
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    if args.dry_run:
        print(f"--- would send to {env['BRAIN_EMAIL_TO']}\n")
        print(text)
        return

    with smtplib.SMTP(env["BRAIN_SMTP_HOST"], int(env.get("BRAIN_SMTP_PORT", "587")), timeout=30) as s:
        s.starttls()
        s.login(env["BRAIN_SMTP_USER"], env["BRAIN_SMTP_PASS"])
        s.send_message(msg)
    n = sum(len(v) for v in groups.values())
    print(f"Sent: {subject} ({n} item{'s' if n != 1 else ''})")


if __name__ == "__main__":
    main()
