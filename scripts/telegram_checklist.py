"""Your to-do list as a Telegram checklist: tap an item's number once it is done.

Each morning the bot sends what is due this week and anything overdue, as a numbered list in
the message, with one small button per number beneath it. The list is in the message rather
than on the buttons because Telegram centres button text and offers no way to change it.

With the relay set up (scripts/telegram_relay/Code.gs), a tap ticks the line at once and the
vault's GitHub workflow closes that loop a minute later, writing the same "Done" record a
/close would. Without it, the tap waits in Telegram's queue until the next drain
(telegram_capture.py) and both happen then. Tap the number again to undo it.

A loop more than two weeks past its date gets two more buttons, "next week" and "drop": one
tap moves its date to seven days from today, or closes it as dropped, so what the brief keeps
calling overdue can be settled from the phone. A dropped line is struck through with an undo
button beside it.

No model is involved. Each button carries the loop's file name, so a tap closes exactly that
loop and nothing is matched by guesswork. Only taps from BRAIN_TELEGRAM_CHAT_ID count, the
same guard capture uses.

The relay renders the message with the same rules as render() below, so the workflow's own
edit afterwards changes nothing unless the vault disagreed. See docs/decisions.md, round 9.

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
from datetime import date, datetime, timedelta
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
# never a loop closed some other way. The checklist's message number follows it, so a stale
# copy of an older checklist cannot reopen a loop ticked from a newer one.
TICK_NOTE = "Ticked in Telegram, from the to-do checklist."

# Written into the Killed section by a drop, and checked before a drop is undone, the same way.
DROP_NOTE = "Dropped in Telegram, from the to-do checklist."

# A loop more than this many days past its date gets "next week" and "drop" buttons. The brief
# moves an item into its Overdue group at the same point, and the reminder emails stop there.
LATE_DAYS = 14
LATE_NOTE = "More than two weeks late: move it to next week, or drop it."

# What each button asks for: d ticks and u unticks; s moves a late loop to seven days from
# today, k drops it, and r undoes a drop.
WANT = {"d": "done", "u": "open", "s": "moved", "k": "dropped", "r": "open"}

# The newest relay tap applied to each checklist, by message number. See reconcile().
APPLIED = VAULT / ".state" / "checklist.json"

FOOTER = "Tap a number once it's done, and again to undo."

# One line of the list, as Telegram sends the text back: box, number, title, then the due date,
# or "not in the vault". A ticked line keeps its date, so an undo can restore it without the
# vault, which the relay cannot read.
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


def late(due: date | None, today: date | None) -> bool:
    """More than two weeks past its date."""
    return bool(due and today and (today - due).days > LATE_DAYS)


def rows_for(items: list[dict], today: date | None = None) -> list[dict]:
    return [{"n": n, "key": key_for(i["stem"]), "title": i["title"], "when": short(i["due"]),
             "state": "open", "late": late(i["due"], today)} for n, i in enumerate(items, 1)]


def esc(s: str) -> str:
    """Escape for Telegram's HTML. Quotes stay as they are: they only matter in attributes."""
    return html.escape(s, quote=False)


def render(head: str, rows: list[dict]) -> tuple[str, list]:
    """The message, as Telegram HTML, and the buttons beneath it: a number for each line, then a
    row of "next week" and "drop" for each line more than two weeks late."""
    lines = [esc(head), ""]
    buttons, late_rows = [], []
    for r in rows:
        n, title, when = r["n"], esc(r["title"]), esc(r["when"])
        if r["state"] == "done":
            lines.append(f"☑ {n}  <s>{title} · {when}</s>")
            buttons.append({"text": f"✓{n}", "callback_data": f"u:{r['key']}"})
        elif r["state"] == "dropped":
            lines.append(f"✕ {n}  <s>{title} · {when}</s>")
            buttons.append({"text": f"↺{n}", "callback_data": f"r:{r['key']}"})
        elif r["state"] == "gone":
            lines.append(f"✕ {n}  {title} · not in the vault")
            buttons.append({"text": f"✕{n}", "callback_data": "x"})
        else:
            lines.append(f"☐ {n}  {title} · {when}")
            buttons.append({"text": str(n), "callback_data": f"d:{r['key']}"})
            if r.get("late"):
                late_rows.append([{"text": f"{n} · next week", "callback_data": f"s:{r['key']}"},
                                  {"text": f"{n} · drop", "callback_data": f"k:{r['key']}"}])
    lines += ["", esc(FOOTER)] + ([esc(LATE_NOTE)] if late_rows else [])
    keyboard = [buttons[i:i + PER_ROW] for i in range(0, len(buttons), PER_ROW)]
    return "\n".join(lines), keyboard + late_rows


def parse(msg: dict) -> tuple[str, list[dict]] | None:
    """A checklist's rows, rebuilt from the message as Telegram sends it back with a tap.

    None for a checklist sent before the list moved into the message, whose buttons carried
    the titles themselves.
    """
    lines = (msg.get("text") or "").splitlines()
    listed = {int(m.group(1)): (m.group(2), m.group(3)) for l in lines if (m := LINE.match(l))}
    if not lines or not listed:
        return None
    rows: dict[int, dict] = {}
    for b in (b for row in (msg.get("reply_markup") or {}).get("inline_keyboard", []) for b in row):
        digits = re.sub(r"\D", "", b.get("text", ""))
        action, _, key = (b.get("callback_data") or "").partition(":")
        if not digits or int(digits) not in listed:
            continue
        n = int(digits)
        r = rows.setdefault(n, {"n": n, "key": key, "title": listed[n][0], "when": listed[n][1],
                                "state": "open", "late": False})
        if action in ("s", "k"):
            r["late"] = True
        else:
            r["key"] = key
            r["state"] = {"u": "done", "x": "gone", "r": "dropped"}.get(action, "open")
    return lines[0], [rows[n] for n in sorted(rows)]


def shown_date(when: str, today: date) -> date | None:
    """A date as the checklist draws it, "10 Nov", read back in the year nearest today."""
    try:
        d = datetime.strptime(when, "%d %b")
    except ValueError:
        return None
    options = []
    for y in (today.year - 1, today.year, today.year + 1):
        try:
            options.append(date(y, d.month, d.day))
        except ValueError:
            pass
    return min(options, key=lambda c: abs((c - today).days)) if options else None


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


def closed_state(path: Path) -> str:
    """How a closed loop is drawn: struck through as done, or crossed out as dropped."""
    return "dropped" if field(path.read_text(encoding="utf-8"), "status") == "killed" else "done"


def close(stem: str, today: date, mid: int | None, status: str) -> tuple[str, str, str, date | None]:
    """Close a loop as done or killed. Returns (output line, state, title, due)."""
    src, dst = VAULT / OPEN / f"{stem}.md", VAULT / CLOSED / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            title, due = facts(dst, stem)
            state = closed_state(dst)
            return f"  already {state}: {title}", state, title, due
        return f"  not found: {stem}", "gone", stem, None
    title, due = facts(src, stem)
    heading, note, verb = (("Done", TICK_NOTE, "done, ticked") if status == "done"
                           else ("Killed", DROP_NOTE, "dropped"))
    note += f" Message {mid}." if mid is not None else ""
    move(src, dst, {"status": status, "folder": CLOSED, "updated": today.isoformat()},
         f"## {heading} — {today.isoformat()}\n\n{note}")
    append_log(f"## [{today.isoformat()}] close | {title} — {verb} in Telegram")
    return (f"  ticked: {title}" if status == "done" else f"  dropped: {title}",
            "done" if status == "done" else "dropped", title, due)


def tick(stem: str, today: date, mid: int | None = None) -> tuple[str, str, str, date | None]:
    """Close a loop as done. Returns (output line, state, title, due)."""
    return close(stem, today, mid, "done")


def drop(stem: str, today: date, mid: int | None = None) -> tuple[str, str, str, date | None]:
    """Close a loop as dropped. Returns (output line, state, title, due)."""
    return close(stem, today, mid, "killed")


def push_on(stem: str, today: date, to: date) -> tuple[str, str, str, date | None]:
    """Move an open loop's date to `to`. Returns (output line, state, title, due)."""
    p = VAULT / OPEN / f"{stem}.md"
    if not p.is_file():
        closed = VAULT / CLOSED / f"{stem}.md"
        if closed.is_file():
            title, due = facts(closed, stem)
            state = closed_state(closed)
            return f"  already {state}: {title}", state, title, due
        return f"  not found: {stem}", "gone", stem, None
    title, due = facts(p, stem)
    if due == to:
        return f"  already moved: {title}", "open", title, due
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = set_fields(raw.replace("\r\n", "\n"), {"due": to.isoformat(), "updated": today.isoformat()})
    was = f", from {due.isoformat()}" if due else ""
    text = (text.rstrip("\n") + f"\n\n---\n\n## Moved — {today.isoformat()}\n\n"
            f"Moved to {to.isoformat()}{was}, from the Telegram checklist.\n")
    p.write_bytes(text.replace("\n", nl).encode("utf-8"))
    append_log(f"## [{today.isoformat()}] loop | {title} — moved to {to.isoformat()} in Telegram")
    return f"  moved: {title}, to {short(to)}", "open", title, to


def untick(stem: str, today: date,
           only_message: int | None = None) -> tuple[str, str, str, date | None]:
    """Reopen a loop the checklist closed, by a tick or a drop. Returns (output line, state,
    title, due).

    With `only_message`, reopen it only if that checklist message closed it.
    """
    src, dst = VAULT / CLOSED / f"{stem}.md", VAULT / OPEN / f"{stem}.md"
    if not src.is_file():
        if dst.is_file():
            title, due = facts(dst, stem)
            return f"  already open: {title}", "open", title, due
        return f"  not found: {stem}", "gone", stem, None
    title, due = facts(src, stem)
    state = closed_state(src)
    text = src.read_text(encoding="utf-8")
    last = max(text.rfind("\n## Done — "), text.rfind("\n## Killed — "))
    section = text[last:] if last != -1 else ""
    how = ("tick" if section.startswith("\n## Done — ") and TICK_NOTE in section else
           "drop" if section.startswith("\n## Killed — ") and DROP_NOTE in section else None)
    if how is None or "\n## Reopened — " in section:
        return f"  left closed: {title}, closed some other way", state, title, due
    if only_message is not None and f"Message {only_message}." not in section:
        return f"  left closed: {title}, closed from another checklist", state, title, due
    move(src, dst, {"status": "open", "folder": OPEN, "updated": today.isoformat()},
         f"## Reopened — {today.isoformat()}\n\n{how.capitalize()} undone in Telegram.")
    append_log(f"## [{today.isoformat()}] close | {title} — reopened, {how} undone in Telegram")
    return f"  undone: {title}", "open", title, due


def last_applied(mid) -> int:
    try:
        return int(json.loads(APPLIED.read_text(encoding="utf-8")).get(str(mid), -1))
    except (OSError, ValueError):
        return -1


def record_applied(mid, update_id: int) -> None:
    try:
        seen = json.loads(APPLIED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        seen = {}
    seen[str(mid)] = update_id
    APPLIED.parent.mkdir(parents=True, exist_ok=True)
    APPLIED.write_text(json.dumps(seen, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def moved_to(row: dict, due: date | None, today: date) -> date | None:
    """Where a tap this picture includes, but the vault has not seen, moved a late loop: its
    line drawn later than the vault's date and without the buttons it had while late."""
    if row.get("late") or not late(due, today):
        return None
    shown = shown_date(row["when"], today)
    return shown if shown and shown > due else None


def reconcile(token: str, chat_id: str, msg: dict, parsed: tuple, action: str, key: str,
              today: date, update_id: int | None, rendered: bool = True) -> str:
    """Make the vault match the checklist as it stood just after this tap.

    A relay tap carries the message as it was on screen, every earlier tick already drawn,
    so the list after this tap is the whole of what he meant, not only this toggle. That is
    what makes overlapping taps safe. The workflow applies taps one at a time, and when
    several wait GitHub keeps only the newest, whose picture holds the ones it replaced. A
    tap older than the newest applied is skipped, so a late one cannot undo a newer one.

    Rows he did not touch on this message are only ticked, never reopened, unless this same
    message ticked them: an old copy of a checklist must not undo what a newer one did. A drop
    is applied from the picture the same way, and so is a move, read from a line drawn with a
    later date than the vault's.

    `rendered` is false when the relay did not draw this tap. An older relay cannot draw a
    move, a drop or its undo, and draws any tap on a checklist with late lines wrongly, so in
    those cases the message is drawn here instead.
    """
    mid = msg.get("message_id")
    if update_id is not None and update_id <= last_applied(mid):
        return f"  skipped a tap older than one already applied, on checklist {mid}"
    head, rows = parsed
    out, corrected = [], False
    # An older relay draws a late line's extra buttons as more lines, so it is redrawn here.
    had_late = any(r.get("late") for r in rows)
    for r in rows:
        if r["state"] == "gone":
            continue
        tapped = r["key"] == key
        want = WANT[action] if tapped else r["state"]
        stem = stem_for(r["key"])
        if stem is None:
            r["state"], corrected = "gone", True
            continue
        if want == "done":
            line, state, title, due = tick(stem, today, mid)
        elif want == "dropped":
            line, state, title, due = drop(stem, today, mid)
        elif want == "moved":
            line, state, title, due = push_on(stem, today, today + timedelta(days=7))
            want = "open"
        else:
            line, state, title, due = untick(stem, today, None if tapped else mid)
            to = moved_to(r, due, today) if state == "open" else None
            if to and to != due:
                line, state, title, due = push_on(stem, today, to)
        if not line.strip().startswith("already"):
            out.append(line)
        now_late = state == "open" and late(due, today)
        # What the relay drew for the tapped line: a move clears its late buttons, the undo of
        # a drop brings them back, and an untick draws none.
        drawn_late = {"s": False, "r": True}.get(action, r.get("late")) if tapped else r.get("late")
        corrected = corrected or state != want or (state == "open" and now_late != drawn_late)
        r.update(state=state, title=title, late=now_late)
        if due:
            r["when"] = short(due)
    if update_id is not None:
        record_applied(mid, update_id)
    if corrected or (not rendered and (action in ("s", "k", "r") or had_late)):
        text, keyboard = render(head, rows)
        try:
            post(token, "editMessageText", {"chat_id": chat_id, "message_id": mid, "text": text,
                                            "parse_mode": "HTML",
                                            "reply_markup": {"inline_keyboard": keyboard}})
        except Exception:  # noqa: BLE001
            pass
    return "\n".join(out) if out else f"  checklist {mid}: the vault already matches"


def handle(token: str, chat_id: str, cq: dict, boards: dict, today: date,
           pushed: bool = False, update_id: int | None = None,
           rendered: bool = True) -> str | None:
    """Apply one tap from a checklist. Returns a line for the drain's output, or None when
    the tap is not one of ours or not from your chat.

    `boards` carries each message's state across one drain, so several taps on the same
    checklist build on each other instead of each starting from the message as it was when
    that tap was made.

    `pushed` means the relay already answered the tap and ticked the message the moment it
    was made. The message is then edited only when the vault disagrees, a tick on a loop
    that was gone or an undo of one closed some other way, because this tap's copy of the
    message predates any taps made after it, and redrawing from it would untick them.
    """
    msg = cq.get("message") or {}
    if (str(cq.get("from", {}).get("id")) != str(chat_id)
            or str(msg.get("chat", {}).get("id")) != str(chat_id)):
        return None
    action, _, key = (cq.get("data") or "").partition(":")
    if action not in WANT or not key:
        return None

    if pushed and (parsed := parse(msg)):
        return reconcile(token, chat_id, msg, parsed, action, key, today, update_id, rendered)

    stem = stem_for(key)
    if stem is None:
        line, state, title, due = f"  not found: {key}", "gone", key, None
    elif action == "d":
        line, state, title, due = tick(stem, today, msg.get("message_id"))
    elif action == "k":
        line, state, title, due = drop(stem, today, msg.get("message_id"))
    elif action == "s":
        line, state, title, due = push_on(stem, today, today + timedelta(days=7))
    else:
        line, state, title, due = untick(stem, today)

    mid = msg.get("message_id")
    if mid not in boards:
        boards[mid] = parse(msg) or ("", (msg.get("reply_markup") or {}).get("inline_keyboard", []))
    head, rows = boards[mid]

    expected = {"d": "done", "k": "dropped"}.get(action, "open")
    if pushed and head and state == expected:
        return line

    if head:
        for r in rows:
            if r["key"] == key:
                r.update(state=state, title=title, late=state == "open" and late(due, today))
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
    calls = [edit] if pushed else [edit, ("answerCallbackQuery", {"callback_query_id": cq.get("id")})]
    for method, payload in calls:
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

    text, keyboard = render(header(today), rows_for(items, today))
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
