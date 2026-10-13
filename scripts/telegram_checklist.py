"""Your to-do list as a Telegram checklist: tap an item's number once it is done.

Each morning the bot sends what is due this week and anything overdue, as a numbered list in
the message, with one small button per number beneath it. The list is in the message rather
than on the buttons because Telegram centres button text and offers no way to change it.

A tap waits in Telegram's queue like any message, and the next drain (telegram_capture.py,
hourly on GitHub) closes that loop in the vault, writes the same "Done" record a /close
would, and ticks the line. Tap the number again to undo it.

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
import html
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

# Number buttons per row beneath the list.
PER_ROW = 6

# Written into the Done section, and checked before an undo: a tick can only undo itself,
# never a loop closed some other way.
TICK_NOTE = "Ticked in Telegram, from the to-do checklist."

FOOTER = "Tap a number once it's done, and again to undo. Ticks reach the vault within the hour."

# One line of the list, as Telegram sends the text back: box, number, title, then a date,
# "done", or "not in the vault".
LINE = re.compile(r"^[☐☑✕] (\d+)  (.+) · (.+)$")


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


# --- the message --------------------------------------------------------------------------


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


def header(today: date) -> str:
    return f"Your to-dos, {today:%A} {today.day} {today:%B}"


def rows_for(items: list[dict]) -> list[dict]:
    return [{"n": n, "key": key_for(i["stem"]), "title": i["title"], "when": short(i["due"]),
             "state": "open"} for n, i in enumerate(items, 1)]


def esc(s: str) -> str:
    """Escape for Telegram's HTML. Quotes stay as they are: they only matter in attributes."""
    return html.escape(s, quote=False)


def render(head: str, rows: list[dict]) -> tuple[str, list]:
    """The message, as Telegram HTML, and the number buttons beneath it."""
    lines = [esc(head), ""]
    buttons = []
    for r in rows:
        title = esc(r["title"])
        if r["state"] == "done":
            lines.append(f"☑ {r['n']}  <s>{title}</s> · done")
            buttons.append({"text": f"✓{r['n']}", "callback_data": f"u:{r['key']}"})
        elif r["state"] == "gone":
            lines.append(f"✕ {r['n']}  {title} · not in the vault")
            buttons.append({"text": f"✕{r['n']}", "callback_data": "x"})
        else:
            lines.append(f"☐ {r['n']}  {title} · {esc(r['when'])}")
            buttons.append({"text": str(r["n"]), "callback_data": f"d:{r['key']}"})
    lines += ["", esc(FOOTER)]
    return "\n".join(lines), [buttons[i:i + PER_ROW] for i in range(0, len(buttons), PER_ROW)]


def parse(msg: dict) -> tuple[str, list[dict]] | None:
    """A checklist's rows, rebuilt from the message as Telegram sends it back with a tap.

    None for a checklist sent before the list moved into the message, whose buttons carried
    the titles themselves.
    """
    lines = (msg.get("text") or "").splitlines()
    listed = {int(m.group(1)): (m.group(2), m.group(3)) for l in lines if (m := LINE.match(l))}
    if not lines or not listed:
        return None
    rows = []
    for b in (b for row in (msg.get("reply_markup") or {}).get("inline_keyboard", []) for b in row):
        digits = re.sub(r"\D", "", b.get("text", ""))
        action, _, key = (b.get("callback_data") or "").partition(":")
        if not digits or int(digits) not in listed:
            continue
        title, when = listed[int(digits)]
        state = {"u": "done", "x": "gone"}.get(action, "open")
        rows.append({"n": int(digits), "key": key, "title": title, "when": when, "state": state})
    return lines[0], rows


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


def facts(path: Path, stem: str) -> tuple[str, date | None]:
    text = path.read_text(encoding="utf-8")
    due = field(text, "due")
    return field(text, "title") or stem, date.fromisoformat(due) if due else None


def tick(stem: str, today: date) -> tuple[str, str, str, date | None]:
    """Close a loop. Returns (output line, state, title, due)."""
    src, dst = VAULT / OPEN / f"{stem}.md", VAULT / CLOSED / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            title, due = facts(dst, stem)
            return f"  already done: {title}", "done", title, due
        return f"  not found: {stem}", "gone", stem, None
    title, due = facts(src, stem)
    move(src, dst, {"status": "done", "folder": CLOSED, "updated": today.isoformat()},
         f"## Done — {today.isoformat()}\n\n{TICK_NOTE}")
    append_log(f"## [{today.isoformat()}] close | {title} — done, ticked in Telegram")
    return f"  ticked: {title}", "done", title, due


def untick(stem: str, today: date) -> tuple[str, str, str, date | None]:
    """Reopen a loop the checklist closed. Returns (output line, state, title, due)."""
    src, dst = VAULT / CLOSED / f"{stem}.md", VAULT / OPEN / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            title, due = facts(dst, stem)
            return f"  already open: {title}", "open", title, due
        return f"  not found: {stem}", "gone", stem, None
    title, due = facts(src, stem)
    text = src.read_text(encoding="utf-8")
    last = text.rfind("\n## Done — ")
    if last == -1 or TICK_NOTE not in text[last:] or "\n## Reopened — " in text[last:]:
        return f"  left closed: {title}, closed some other way", "done", title, due
    move(src, dst, {"status": "open", "folder": OPEN, "updated": today.isoformat()},
         f"## Reopened — {today.isoformat()}\n\nTick undone in Telegram.")
    append_log(f"## [{today.isoformat()}] close | {title} — reopened, tick undone in Telegram")
    return f"  undone: {title}", "open", title, due


def handle(token: str, chat_id: str, cq: dict, boards: dict, today: date) -> str | None:
    """Apply one tap from a checklist. Returns a line for the drain's output, or None when
    the tap is not one of ours or not from your chat.

    `boards` carries each message's state across one drain, so several taps on the same
    checklist build on each other instead of each starting from the message as it was when
    that tap was made.
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
        line, state, title, due = f"  not found: {key}", "gone", key, None
    elif action == "d":
        line, state, title, due = tick(stem, today)
    else:
        line, state, title, due = untick(stem, today)

    mid = msg.get("message_id")
    if mid not in boards:
        boards[mid] = parse(msg) or ("", (msg.get("reply_markup") or {}).get("inline_keyboard", []))
    head, rows = boards[mid]

    if head:
        for r in rows:
            if r["key"] == key:
                r["state"], r["title"] = state, title
                if due:
                    r["when"] = short(due)
        text, keyboard = render(head, rows)
        edit = ("editMessageText", {"chat_id": chat_id, "message_id": mid, "text": text,
                                    "parse_mode": "HTML",
                                    "reply_markup": {"inline_keyboard": keyboard}})
    else:
        # A checklist from before the list moved into the message: relabel its button.
        label = {"done": f"☑ {title} · done",
                 "gone": f"✕ {title} · not in the vault"}.get(
                     state, f"☐ {title}" + (f" · {short(due)}" if due else ""))
        data = {"done": f"u:{key}", "gone": "x"}.get(state, f"d:{key}")
        for b in (b for row in rows for b in row):
            if b.get("callback_data") in (f"d:{key}", f"u:{key}"):
                b.update({"text": label, "callback_data": data})
        edit = ("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": mid,
                                           "reply_markup": {"inline_keyboard": rows}})

    # Both can fail without harm: an answer more than a few seconds late is refused, and an
    # edit that changes nothing is an error. The vault is already right either way.
    for method, payload in (edit, ("answerCallbackQuery", {"callback_query_id": cq.get("id")})):
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
    # The list carries box characters a Windows console cannot print in its own codepage.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    today = date.today()
    items = todos(today)
    if not items:
        print(f"{today}: nothing due this week, no checklist sent.")
        return

    text, keyboard = render(header(today), rows_for(items))
    if args.dry_run:
        print(text)
        print("  " + "  ".join(f"[{b['text']}]" for row in keyboard for b in row))
        return

    env = load_env()
    token, chat_id = env.get("BRAIN_TELEGRAM_TOKEN"), env.get("BRAIN_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("Missing BRAIN_TELEGRAM_TOKEN or BRAIN_TELEGRAM_CHAT_ID. See .env.example.")
    res = post(token, "sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML",
                                      "reply_markup": {"inline_keyboard": keyboard}})
    if not res.get("ok"):
        sys.exit(f"Telegram error: {res}")
    print(f"Sent the checklist: {len(items)} item(s).")


if __name__ == "__main__":
    main()
