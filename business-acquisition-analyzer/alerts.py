"""Optional outbound alerts for high-scoring listings.

All webhooks are opt-in via environment variables. If none are configured,
maybe_alert() is a no-op - the app must never crash because alerting isn't
set up.
"""

import json
import urllib.request

import config


def maybe_alert(result: dict) -> None:
    """Fire configured webhooks if the listing's composite score clears the
    alert threshold. Silently does nothing if no webhook is configured."""
    if result["composite"] < config.ALERT_COMPOSITE_MIN:
        return

    message = _format_message(result)

    if config.SLACK_WEBHOOK_URL:
        _post_json(config.SLACK_WEBHOOK_URL, {"text": message})
    if config.DISCORD_WEBHOOK_URL:
        _post_json(config.DISCORD_WEBHOOK_URL, {"content": message})
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        _post_json(url, {"chat_id": config.TELEGRAM_CHAT_ID, "text": message})


def _format_message(result: dict) -> str:
    listing = result["listing"]
    header = f"[{result['verdict']}] {listing.name} - composite {result['composite']}/100"
    detail = f"Passive EBITDA: ${result['passive_ebitda']:,.0f} | Sector: {result['sector']}"
    if listing.asking_price:
        detail += f" | Asking: ${listing.asking_price:,.0f}"
    return f"{header}\n{detail}"


def _post_json(url: str, payload: dict) -> None:
    try:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(request, timeout=5)
    except Exception:
        # Alerting must never crash the scoring flow - log and move on.
        print(f"[alerts] failed to post to {url}")
