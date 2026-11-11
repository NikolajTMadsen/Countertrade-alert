"""Sender en kort Teams-besked, når Energinet publicerer ny countertrade."""
import json
import os
import sys
import urllib.request
from pathlib import Path

API_URL = "https://api.energidataservice.dk/dataset/CountertradeIntraday_v2?start=now-P1D&limit=0"
DATA_URL = "https://www.energidataservice.dk/tso-electricity/CountertradeIntraday_v2"
STATE_FILE = Path(__file__).with_name("state.json")


def fetch_records():
    with urllib.request.urlopen(API_URL, timeout=30) as resp:
        return json.load(resp)["records"]


def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_publication": None}


def count_hours(records):
    # En time tæller, hvis mindst ét kvarter i den har volumen > 0
    hours = {
        r["TimeDK"][:13]
        for r in records
        if (r["VolumeUpMW"] or 0) > 0 or (r["VolumeDownMW"] or 0) > 0
    }
    return len(hours)


def build_card(hours):
    return {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [{
                    "type": "TextBlock",
                    "text": f"Ny countertrade publiceret: {hours} timer",
                    "weight": "Bolder",
                    "size": "Medium",
                    "wrap": True,
                }],
                "actions": [{"type": "Action.OpenUrl", "title": "Se data", "url": DATA_URL}],
            },
        }],
    }


def send_to_teams(webhook_url, payload):
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"Teams svarede {resp.status}")


def main():
    dry_run = "--dry-run" in sys.argv
    records = fetch_records()
    if not records:
        print("Ingen countertrade-data.")
        return

    latest = max(r["PublicationDate"] for r in records)
    state = load_state()
    last = state.get("last_publication")
    if last and latest <= last and not dry_run:
        print(f"Ingen nye data (senest {latest}).")
        return

    batch = [r for r in records if r["PublicationDate"] == latest]
    hours = count_hours(batch)
    payload = build_card(hours)

    if dry_run:
        print(f"Publiceret {latest}: {hours} timer")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        sys.exit("TEAMS_WEBHOOK_URL er ikke sat.")
    send_to_teams(webhook_url, payload)

    STATE_FILE.write_text(json.dumps({"last_publication": latest}, indent=2) + "\n", encoding="utf-8")
    print(f"Besked sendt: {hours} timer (publiceret {latest}).")


if __name__ == "__main__":
    main()
