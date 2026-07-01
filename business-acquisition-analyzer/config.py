"""Calibration constants for the NZ Business Acquisition Analyzer.

Everything a user is likely to want to tune lives here, so scoring logic in
scoring.py never needs to change just because the target profile does.
"""

import os

# --- Target profile -------------------------------------------------------
TARGET_EBITDA_MIN = 200_000
TARGET_EBITDA_MAX = 300_000
EBITDA_FLOOR = 100_000
MIN_MARGIN = 0.20

# --- Manager-adjustment ----------------------------------------------------
# NZD annual cost of hiring a full-time manager to replace the owner. This is
# what gets stripped out of SDE/EBPITD to arrive at a truly passive EBITDA.
REPLACEMENT_MANAGER_COST = 110_000

# --- Pillar weights (must sum to 1.0) --------------------------------------
WEIGHTS = {
    "owner_independence": 0.30,
    "profit_quality": 0.25,
    "valuation": 0.20,
    "deal_structure": 0.15,
    "resilience_fit": 0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "WEIGHTS must sum to 1.0"

# --- Verdict thresholds ------------------------------------------------
VERDICT_SWING = 70
VERDICT_WATCH = 50

# --- Alerting ----------------------------------------------------------------
ALERT_COMPOSITE_MIN = 70

# --- PipeTech-relevant keywords (bonus in resilience_fit pillar) -----------
PIPETECH_KEYWORDS = [
    "drainage", "civil", "water", "three waters", "pipeline", "trenchless",
    "infrastructure", "council", "wastewater", "stormwater", "excavation",
    "contracting", "plumbing",
]

# --- Optional LLM-assisted parsing -----------------------------------------
# Override with an env var if your account uses a different model alias.
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# --- Optional persistence ---------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# --- Optional alert webhooks -------------------------------------------------
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
