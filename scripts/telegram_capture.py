"""Pull messages you sent yourself on Telegram into the vault inbox.

The point of this script is that it does NOT need to be running when you send. Telegram
queues bot updates for 24 hours, so you message your bot from anywhere, and next time you
open your laptop this drains the backlog into raw/inbox/. No always-on host, no VPS, and
Telegram's bot API is official — unlike the WhatsApp route, there is no ban risk.

It captures only. It does not compile, and it does not answer questions — answering needs
a model, and that lives in Claude Code where /ingest and /ask already are.

Usage:
    python scripts/telegram_capture.py --once     # drain the backlog and exit
    python scripts/telegram_capture.py --watch    # keep polling until Ctrl-C
    python scripts/telegram_capture.py --setup    # print your chat id, for first-time config

Stdlib only, deliberately — this runs unattended and should not rot when a dependency does.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("BRAIN_VAULT", ROOT / "vault")).resolve()
INBOX = VAULT / "raw" / "inbox"
STATE = ROOT / ".telegram-offset"
API = "https://api.telegram.org"

# Telegram holds undelivered updates for 24h. Anything older is gone regardless.
LONG_POLL = 50


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


def call(token: str, method: str, **params) -> dict:
    url = f"{API}/bot{token}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=LONG_POLL + 15) as r:
        return json.loads(r.read().decode("utf-8"))


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:48] or "message").rstrip("-")


def unique(path: Path) -> Path:
    if not path.exists():
        return path
    n = 2
    while (p := path.with_stem(f"{path.stem}-{n}")).exists():
        n += 1
    return p


def download(token: str, file_id: str, dest_dir: Path, stem: str) -> Path | None:
    """Fetch an attachment. Returns the saved path, or None if Telegram refused."""
    info = call(token, "getFile", file_id=file_id)
    if not info.get("ok"):
        return None
    remote = info["result"]["file_path"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = unique(dest_dir / f"{stem}{Path(remote).suffix}")
    with urllib.request.urlopen(f"{API}/file/bot{token}/{remote}", timeout=120) as r:
        dest.write_bytes(r.read())
    return dest


def save(msg: dict, token: str) -> Path | None:
    """Write one Telegram message into raw/inbox/. Returns the page written."""
    text = msg.get("text") or msg.get("caption") or ""
    sent = datetime.fromtimestamp(msg["date"]).isoformat(timespec="seconds")
    today = date.today().isoformat()

    # A forward keeps its origin; that provenance matters more than the fact you forwarded it.
    origin = "telegram"
    fwd = msg.get("forward_origin") or {}
    if fwd:
        who = fwd.get("sender_user", {}).get("first_name") or fwd.get("sender_user_name")
        origin = f"telegram (forwarded from {who})" if who else "telegram (forwarded)"

    kind, attachment = "note", None
    stem = f"{today}-{slug(text) if text else 'attachment'}"

    if doc := msg.get("document"):
        kind = "pdf" if str(doc.get("mime_type", "")).endswith("pdf") else "file"
        stem = f"{today}-{slug(Path(doc.get('file_name', 'file')).stem)}"
        attachment = download(token, doc["file_id"], VAULT / "raw" / "pdfs", stem)
    elif photos := msg.get("photo"):
        kind = "image"
        attachment = download(token, photos[-1]["file_id"], VAULT / "raw" / "images", stem)
    elif msg.get("voice") or msg.get("audio"):
        # C5: voice notes are out of scope. Keep the text, say the audio was dropped.
        text = (text + "\n\n[voice note received — transcription is out of scope]").strip()

    if not text and not attachment:
        return None

    title = (text.splitlines()[0] if text else stem)[:70] or stem
    INBOX.mkdir(parents=True, exist_ok=True)
    page = unique(INBOX / f"{stem}.md")

    front = [
        "---",
        f"id: {page.stem}",
        f"captured: {today}",
        f"sent: {sent}",
        f"kind: {kind}",
        f"origin: {origin}",
        f"title: {title}",
        "status: uncompiled",
    ]
    if attachment:
        front.append(f"attachment: {attachment.relative_to(VAULT).as_posix()}")
    front.append("---")

    body = text or f"(no text — see attachment: {attachment.name})"
    if attachment and text:
        body += f"\n\nAttachment: `{attachment.relative_to(VAULT).as_posix()}`"

    page.write_text("\n".join(front) + "\n\n" + body + "\n", encoding="utf-8")
    return page


def drain(token: str, chat_id: str, watch: bool) -> int:
    offset = int(STATE.read_text().strip()) if STATE.is_file() else 0
    saved = skipped = 0

    while True:
        res = call(token, "getUpdates", offset=offset, timeout=LONG_POLL if watch else 0)
        if not res.get("ok"):
            sys.exit(f"Telegram error: {res}")
        updates = res["result"]

        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message") or u.get("channel_post")
            if not msg:
                continue
            # Only your own chat. Without this, anyone who finds the bot writes to your vault.
            if str(msg.get("chat", {}).get("id")) != str(chat_id):
                skipped += 1
                continue
            if page := save(msg, token):
                saved += 1
                print(f"  {page.relative_to(VAULT).as_posix()}")

        STATE.write_text(str(offset), encoding="utf-8")

        if not watch:
            if not updates:
                break
            continue  # keep pulling until Telegram has nothing left

    if skipped:
        print(f"Ignored {skipped} message(s) from other chats.")
    return saved


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true", help="drain the backlog and exit")
    g.add_argument("--watch", action="store_true", help="keep long-polling until Ctrl-C")
    g.add_argument("--setup", action="store_true", help="print your chat id for first-time config")
    args = ap.parse_args()

    env = load_env()
    token = env.get("BRAIN_TELEGRAM_TOKEN")
    if not token:
        sys.exit("Missing BRAIN_TELEGRAM_TOKEN. See .env.example.")

    if args.setup:
        me = call(token, "getMe")
        if not me.get("ok"):
            sys.exit(f"Bad token: {me}")
        print(f"Bot: @{me['result']['username']}")
        res = call(token, "getUpdates", timeout=0)
        chats = {
            str(m["chat"]["id"]): m["chat"].get("first_name") or m["chat"].get("title", "?")
            for u in res.get("result", [])
            if (m := u.get("message"))
        }
        if not chats:
            print("\nNo messages yet. Send your bot any message, then run --setup again.")
        else:
            print("\nAdd this to .env:")
            for cid, name in chats.items():
                print(f"  BRAIN_TELEGRAM_CHAT_ID={cid}    # {name}")
        return

    chat_id = env.get("BRAIN_TELEGRAM_CHAT_ID")
    if not chat_id:
        sys.exit("Missing BRAIN_TELEGRAM_CHAT_ID. Run --setup to find it.")

    if args.watch:
        print("Watching Telegram. Ctrl-C to stop.")
    n = drain(token, chat_id, watch=args.watch)
    print(f"Captured {n} message(s) into raw/inbox/. Run /ingest to compile.")


if __name__ == "__main__":
    main()
