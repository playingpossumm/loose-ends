"""Your to-do list as a Telegram checklist: tap an item once it is done.

Each morning the bot sends what is due this week and anything overdue, one button per item.
A tap waits in Telegram's queue like any message, and the next drain (telegram_capture.py,
hourly on GitHub) closes that loop in the vault, writes the same "Done" record a /close
would, and turns the button into a tick. Tap the tick to undo it.

No model is involved. Each button carries the loop's file name, so a tap closes exactly that
loop and nothing is matched by guesswork. Only taps from BRAIN_TELEGRAM_CHAT_ID count, the
same guard capture uses.

A tap registers at the next drain, not at once: the bot is polled rather than pushed to,
which is what lets it run without a server. See docs/decisions.md, round 9.

Only open loops with a date are listed. Undated ones, and the birthdays and deadlines in
loops/dates, stay in the brief and the reminder emails.

    python scripts/telegram_checklist.py --dry-run   # print the checklist
    python scripts/telegram_checklist.py             # send it

Stdlib only, like telegram_capture.py, which imports it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()
API = "https://api.telegram.org"

OPEN = "loops/open"
CLOSED = "loops/closed"

# Telegram caps a button's callback data at 64 bytes. A loop's file name fits; one that does
# not goes as a short hash, found again by hashing the names on disk.
MAX_KEY = 60

# Written into the Done section, and checked before an undo: a tick can only undo itself,
# never a loop closed some other way.
TICK_NOTE = "Ticked in Telegram, from the to-do checklist."


def load_env() -> dict[str, str]:
    env = dict(os.environ)
    f = ROOT / ".env"
    if f.is_file():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip("'\""))
    return env


def post(token: str, method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API}/bot{token}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


# --- reading loops ------------------------------------------------------------------------


def frontmatter(text: str) -> str:
    """The YAML block alone, so a field name in the body never matches."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else ""


def field(text: str, name: str) -> str:
    m = re.search(rf"^{name}:[ \t]*(.*?)[ \t]*\r?$", frontmatter(text), re.M)
    return m.group(1).strip("\"'") if m else ""


def todos(today: date) -> list[dict]:
    """Open loops due by this Sunday, overdue ones first."""
    sunday = today + timedelta(days=6 - today.weekday())
    out = []
    for p in sorted((VAULT / OPEN).glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        due = field(text, "due")
        if field(text, "status") != "open" or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due):
            continue
        if date.fromisoformat(due) <= sunday:
            out.append({"stem": p.stem, "title": field(text, "title") or p.stem,
                        "due": date.fromisoformat(due)})
    return sorted(out, key=lambda i: (i["due"], i["title"]))


# --- buttons ------------------------------------------------------------------------------


def key_for(stem: str) -> str:
    return stem if len(stem) <= MAX_KEY else "#" + hashlib.sha1(stem.encode()).hexdigest()[:16]


def stem_for(key: str) -> str | None:
    if not key.startswith("#"):
        return key
    for folder in (OPEN, CLOSED):
        for p in (VAULT / folder).glob("*.md"):
            if key_for(p.stem) == key:
                return p.stem
    return None


def short(d: date) -> str:
    return f"{d.day} {d:%b}"


def open_button(stem: str, title: str, due: date | None) -> dict:
    when = f" · {short(due)}" if due else ""
    return {"text": f"☐ {title}{when}", "callback_data": f"d:{key_for(stem)}"}


def done_button(stem: str, title: str) -> dict:
    return {"text": f"☑ {title} · done", "callback_data": f"u:{key_for(stem)}"}


def gone_button(stem: str) -> dict:
    # "x" is an action nothing handles, so a tap on it changes nothing.
    return {"text": f"✕ {stem} · not in the vault", "callback_data": "x"}


def header(today: date) -> str:
    return (f"Your to-dos, {today:%A} {today.day} {today:%B}\n"
            "Tap one when it's done, and again to undo. Ticks reach the vault within the hour.")


# --- applying a tap -----------------------------------------------------------------------


def set_fields(text: str, values: dict[str, str]) -> str:
    """Set frontmatter fields, adding any that are missing. The body is left alone."""
    fm = frontmatter(text)
    body = text[len(fm):]
    for name, value in values.items():
        line = f"{name}: {value}"
        fm, n = re.subn(rf"^{name}:.*$", line, fm, count=1, flags=re.M)
        if not n:
            fm = fm.rstrip("\n") + "\n" + line
    return fm + body


def append_log(entry: str) -> None:
    """One line in log.md, in the prefix format grep and /lint rely on."""
    p = VAULT / "log.md"
    raw = p.read_bytes().decode("utf-8") if p.is_file() else ""
    nl = "\r\n" if "\r\n" in raw else "\n"
    p.write_bytes((raw.rstrip("\r\n") + nl + nl + entry + nl).encode("utf-8"))


def move(src: Path, dst: Path, values: dict[str, str], section: str) -> None:
    raw = src.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = set_fields(raw.replace("\r\n", "\n"), values)
    text = text.rstrip("\n") + "\n\n---\n\n" + section.strip("\n") + "\n"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(text.replace("\n", nl).encode("utf-8"))
    src.unlink()


def tick(stem: str, today: date) -> tuple[str, dict]:
    src, dst = VAULT / OPEN / f"{stem}.md", VAULT / CLOSED / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            title = field(dst.read_text(encoding="utf-8"), "title") or stem
            return f"  already done: {title}", done_button(stem, title)
        return f"  not found: {stem}", gone_button(stem)
    title = field(src.read_text(encoding="utf-8"), "title") or stem
    move(src, dst, {"status": "done", "folder": CLOSED, "updated": today.isoformat()},
         f"## Done — {today.isoformat()}\n\n{TICK_NOTE}")
    append_log(f"## [{today.isoformat()}] close | {title} — done, ticked in Telegram")
    return f"  ticked: {title}", done_button(stem, title)


def untick(stem: str, today: date) -> tuple[str, dict]:
    src, dst = VAULT / CLOSED / f"{stem}.md", VAULT / OPEN / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            text = dst.read_text(encoding="utf-8")
            title, due = field(text, "title") or stem, field(text, "due")
            return (f"  already open: {title}",
                    open_button(stem, title, date.fromisoformat(due) if due else None))
        return f"  not found: {stem}", gone_button(stem)
    text = src.read_text(encoding="utf-8").replace("\r\n", "\n")
    title, due = field(text, "title") or stem, field(text, "due")
    last = text.rfind("\n## Done — ")
    if last == -1 or TICK_NOTE not in text[last:] or "\n## Reopened — " in text[last:]:
        return f"  left closed: {title}, closed some other way", done_button(stem, title)
    move(src, dst, {"status": "open", "folder": OPEN, "updated": today.isoformat()},
         f"## Reopened — {today.isoformat()}\n\nTick undone in Telegram.")
    append_log(f"## [{today.isoformat()}] close | {title} — reopened, tick undone in Telegram")
    return f"  undone: {title}", open_button(stem, title, date.fromisoformat(due) if due else None)


def handle(token: str, chat_id: str, cq: dict, boards: dict, today: date) -> str | None:
    """Apply one tap from a checklist. Returns a line for the drain's output, or None when
    the tap is not one of ours or not from your chat.

    `boards` carries each message's buttons across one drain, so several taps on the same
    checklist build on each other instead of each starting from the buttons as they were
    when that tap was made.
    """
    msg = cq.get("message") or {}
    if (str(cq.get("from", {}).get("id")) != str(chat_id)
            or str(msg.get("chat", {}).get("id")) != str(chat_id)):
        return None
    action, _, key = (cq.get("data") or "").partition(":")
    if action not in ("d", "u") or not key:
        return None

    stem = stem_for(key)
    if stem is None:
        line, button = f"  not found: {key}", gone_button(key)
    elif action == "d":
        line, button = tick(stem, today)
    else:
        line, button = untick(stem, today)

    mid = msg.get("message_id")
    board = boards.setdefault(mid, (msg.get("reply_markup") or {}).get("inline_keyboard", []))
    for row in board:
        for b in row:
            if b.get("callback_data") in (f"d:{key}", f"u:{key}"):
                b.clear()
                b.update(button)

    # Both can fail without harm: an answer more than a few seconds late is refused, and an
    # edit that changes nothing is an error. The vault is already right either way.
    for method, payload in (
        ("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": mid,
                                    "reply_markup": {"inline_keyboard": board}}),
        ("answerCallbackQuery", {"callback_query_id": cq.get("id")}),
    ):
        try:
            post(token, method, payload)
        except Exception:  # noqa: BLE001
            pass
    return line


# --- sending ------------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print instead of sending")
    args = ap.parse_args()
    # The buttons carry box characters a Windows console cannot print in its own codepage.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    today = date.today()
    items = todos(today)
    if not items:
        print(f"{today}: nothing due this week, no checklist sent.")
        return

    keyboard = [[open_button(i["stem"], i["title"], i["due"])] for i in items]
    if args.dry_run:
        print(header(today))
        for row in keyboard:
            print(f"  [{row[0]['text']}]  ->  {row[0]['callback_data']}")
        return

    env = load_env()
    token, chat_id = env.get("BRAIN_TELEGRAM_TOKEN"), env.get("BRAIN_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("Missing BRAIN_TELEGRAM_TOKEN or BRAIN_TELEGRAM_CHAT_ID. See .env.example.")
    res = post(token, "sendMessage", {"chat_id": chat_id, "text": header(today),
                                      "reply_markup": {"inline_keyboard": keyboard}})
    if not res.get("ok"):
        sys.exit(f"Telegram error: {res}")
    print(f"Sent the checklist: {len(items)} item(s).")


if __name__ == "__main__":
    main()
