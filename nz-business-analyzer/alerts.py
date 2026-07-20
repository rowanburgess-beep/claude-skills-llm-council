"""Optional alert delivery for high-scoring listings.

Fires when a listing's composite score clears config.ALERT_COMPOSITE_MIN.
Reads webhook config from environment variables and is a strict no-op if none
are set — alerts must never crash the scoring pipeline.
"""
import json
import os
import urllib.request

import config
from scoring import ScoreResult


def maybe_alert(result: ScoreResult) -> bool:
    """Post an alert for `result` if it clears the threshold. Returns True if any channel fired."""
    if result.composite < config.ALERT_COMPOSITE_MIN:
        return False

    message = _format_message(result)
    sent = False

    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_url:
        sent = _post_json(slack_url, {"text": message}) or sent

    discord_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if discord_url:
        sent = _post_json(discord_url, {"content": message}) or sent

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        sent = _post_json(url, {"chat_id": chat_id, "text": message}) or sent

    return sent


def _post_json(url: str, payload: dict, timeout: int = 5) -> bool:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        return False


def _format_message(result: ScoreResult) -> str:
    listing = result.listing
    ebitda = f"${listing.passive_ebitda:,.0f}" if listing.passive_ebitda is not None else "unknown"
    return (
        f"[{result.verdict}] {listing.name} — composite {result.composite}/100, "
        f"passive EBITDA {ebitda}, sector {result.band.label}"
    )
