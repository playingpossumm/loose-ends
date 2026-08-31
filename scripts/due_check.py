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
from datetime import date, datetime, timedelta
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
            # The `title:` field if the compiler wrote one, since a loop heading is a
            # description ("Foundation — start go-to-market planning (Monday)") and a
            # subject line needs a name. clean_title salvages the heading otherwise.
            m = TITLE.search(text)
            title = m.group(1).strip() if m else clean_title(next(
                (l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")),
                p.stem,
            ))
            out.append({
                "path": p.relative_to(VAULT).as_posix(),
                "title": title,
                "due": date.fromisoformat(due.group(1)),
                "body": body_of(text),
                "link": link_of(text),
                "window": window_of(text, date.fromisoformat(due.group(1)), date.today()),
            })
    return out


TITLE = re.compile(r"^title:\s*(.+)$", re.M)
SUMMARY = re.compile(r"^summary:\s*(.+)$", re.M)
NUDGE = re.compile(r"^nudge:\s*(morning|evening)\s*$", re.M | re.I)
LINK = re.compile(r"<(https?://[^>]+)>|\[[^\]]*\]\((https?://[^)]+)\)|(?<![(<])(https?://\S+)")


def body_of(text: str) -> str:
    """The loop's own one-line summary, or nothing.

    Earlier versions took the first few lines of the page instead. That page is written for
    the vault: it cites its sources by path, argues its own ranking, and narrates the user
    in the third person, so a reminder built from it read "His own date, stated 2026-08-31".
    No amount of stripping fixes the pronouns, so the compiler now writes a `summary:` line
    addressed to the reader, and this returns that or says nothing at all.
    """
    m = SUMMARY.search(text)
    return m.group(1).strip() if m else ""


def link_of(text: str) -> str:
    """The first URL on the page, so a reminder to read something includes the thing."""
    m = LINK.search(text)
    return next((g for g in m.groups() if g), "") if m else ""


def window_of(text: str, due: date, today: date) -> str:
    """Which of the two daily sends this item belongs in: morning or evening.

    A reminder is only useful at the hour you can act on it. Something due today needs the
    working day in front of it, so it goes at 07:00. Something due tomorrow needs an evening
    of preparation, so it goes at 19:30 while there is still a night to use. Overdue items
    go in the morning, where the day is longest.

    The compiler overrides this per loop with `nudge: morning` or `nudge: evening` when the
    nature of the item disagrees with the date — an article to read is an evening item on
    any date, and a booking that needs an office to be open is a morning one.
    """
    m = NUDGE.search(text)
    if m:
        return m.group(1).lower()
    return "evening" if due == today + timedelta(days=1) else "morning"


# Words that carry no meaning once the due date is printed beside the title. Compared as
# whole tokens rather than by regex: a pattern needing word boundaries does not survive
# being written through a shell heredoc, and this file is read far more often than it runs.
DATEWORDS = frozenset("""
monday tuesday wednesday thursday friday saturday sunday
january february march april may june july august september october november december
jan feb mar apr jun jul aug sep sept oct nov dec
to and of by on due from before after early mid late end start next this week
""".split())


def is_date_clause(text: str) -> bool:
    """True when every word in the clause belongs to a date expression."""
    words = [w.strip(".,()").lower() for w in text.split() if w.strip(".,()")]
    return bool(words) and all(
        w in DATEWORDS or w.rstrip("stndrh").isdigit() for w in words)


def clean_title(raw: str) -> str:
    """Loop headings are descriptions, not titles. Trim them to something a subject line can
    carry: no trailing parenthetical, and no trailing clause that only repeats the due date,
    which the reminder already prints beside the title.

    The clause survives whenever it carries meaning, as in "for GMAP SEA", and whenever
    dropping it would leave a single generic word, since "Trip" names nothing.
    """
    title = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
    head, sep, tail = title.rpartition(chr(8212))
    head = head.strip()
    if sep and len(head.split()) >= 2 and is_date_clause(tail):
        return head
    return title


# How long an overdue item keeps sending daily reminders. After this it appears in the brief
# only. Reminding every day forever is how a channel becomes noise, and a channel you ignore
# is worse than one that never existed.
OVERDUE_NAG_DAYS = 14


def buckets(items: list[dict], today: date, window: str) -> dict[str, list[dict]]:
    """Overdue, today, tomorrow, restricted to one of the two daily sends.

    Nothing further out: the brief covers that.
    """
    items = [i for i in items if i["window"] == window]
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
            stamp = (f"{when} ({overdue_by} day{'s' if overdue_by != 1 else ''} ago)"
                     if overdue_by > 0 else when)
            text += [f"  {i['title']} {chr(8212)} {stamp}"]
            if i["body"]:
                text.append(f"    {i['body']}")
            if i["link"]:
                text.append(f"    {i['link']}")
            text.append("")
            head = (f"<a href='{i['link']}'>{i['title']}</a>" if i["link"] else i["title"])
            html.append(
                f"<h3>{head}</h3><p><span class='when'>{stamp}</span>"
                + (f"<br>{i['body']}" if i["body"] else "") + "</p>"
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
    ap.add_argument("--window", choices=("morning", "evening"), default=None,
                    help="which daily send this is. Defaults to whichever is nearer now.")
    args = ap.parse_args()

    today = date.today()
    window = args.window or ("morning" if datetime.now().hour < 13 else "evening")
    groups = buckets(read_dated(), today, window)

    if not any(groups.values()):
        print(f"{today} {window}: nothing to send.")
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
