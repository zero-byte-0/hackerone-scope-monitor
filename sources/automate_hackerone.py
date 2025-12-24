import json
import hashlib
from pathlib import Path
from typing import Dict, List

from hackerone_client import HackerOneClient
from telegram_notify import TelegramBot



H1_USERNAME = "HACKERONE_USERNAME"
H1_TOKEN = "HACKERONE_TOKEN"


TG_TOKEN = "TELEGTRAM_BOT_TOKEN"
TG_CHAT_ID = "TELEGRAM_BOT_CHAT_ID"

SNAPSHOT = Path("data/hackerone_snapshot.json")


def normalize_scope(scopes: List[Dict]) -> List[Dict]:
    normalized = []
    for s in scopes:
        attr = s["attributes"]
        normalized.append(
            {
                "asset_type": attr["asset_type"],
                "identifier": attr["asset_identifier"],
                "eligible_for_bounty": attr["eligible_for_bounty"],
                "eligible_for_submission": attr["eligible_for_submission"],
            }
        )
    return sorted(normalized, key=lambda x: (x["asset_type"], x["identifier"]))


def hash_scope(scope: List[Dict]) -> str:
    raw = json.dumps(scope, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def load_snapshot() -> Dict:
    if SNAPSHOT.exists():
        return json.loads(SNAPSHOT.read_text())
    return {}


def save_snapshot(data: Dict) -> None:
    SNAPSHOT.parent.mkdir(exist_ok=True)
    SNAPSHOT.write_text(json.dumps(data, indent=2))


def main():
    h1 = HackerOneClient(H1_USERNAME, H1_TOKEN)
    tg = TelegramBot(TG_TOKEN, TG_CHAT_ID)

    previous = load_snapshot()
    current = {}
    alerts = []

    for handle in h1.list_programs():
        scopes = h1.get_structured_scopes(handle)
        normalized = normalize_scope(scopes)
        scope_hash = hash_scope(normalized)

        if handle not in previous:
            alerts.append(f"🆕 New HackerOne program: {handle}")
        elif previous[handle] != scope_hash:
            alerts.append(f"🔄 Scope updated: {handle}")

        current[handle] = scope_hash

    if alerts:
        tg.send("🎯 HackerOne Updates\n\n" + "\n".join(alerts))
    else:
        tg.send("ℹ️ HackerOne: no scope changes detected")

    save_snapshot(current)


if __name__ == "__main__":
    main()
