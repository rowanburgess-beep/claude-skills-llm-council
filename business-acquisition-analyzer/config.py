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

# --- Track record (years trading) -------------------------------------------
YEARS_ESTABLISHED_BONUS_THRESHOLD = 10   # some credit for an established business
YEARS_ESTABLISHED_PROVEN_THRESHOLD = 15  # full credit for a genuinely proven track record
YOUNG_BUSINESS_THRESHOLD = 5             # below this, flag the shorter operating history

# --- Financing feasibility (low/zero-cash-down acquisition test) -----------
# Can the manager-adjusted (passive) EBITDA actually service a loan on the
# asking price? This is a Debt Service Coverage Ratio (DSCR) test: financing
# FINANCED_PORTION of the asking price at LOAN_INTEREST_RATE over
# LOAN_TERM_YEARS, then checking passive EBITDA covers the annual payment
# with a MIN_DSCR safety margin. All four are editable - these are the
# assumptions a bank or vendor-finance deal would actually underwrite to.
LOAN_INTEREST_RATE = 0.10   # blended bank / vendor-finance rate assumption
LOAN_TERM_YEARS = 7         # NZ acquisition loans commonly run 5-10 years
FINANCED_PORTION = 1.0      # 1.0 = fully financed (true zero-cash-down)
MIN_DSCR = 1.25             # minimum coverage ratio most lenders underwrite to

# --- Alerting ----------------------------------------------------------------
ALERT_COMPOSITE_MIN = 70

# --- PipeTech-relevant keywords (bolt-on synergy with the buyer's existing
# civil/drainage business - largest bonus in resilience_fit pillar) ---------
PIPETECH_KEYWORDS = [
    "drainage", "civil", "water", "three waters", "pipeline", "trenchless",
    "infrastructure", "council", "wastewater", "stormwater", "excavation",
    "contracting", "plumbing",
]

# --- Self-running / essential brick-and-mortar keywords (separate thesis:
# pure passive diversification rather than a PipeTech bolt-on - same bonus
# weight in resilience_fit, since it's an equally valid target archetype) --
ESSENTIAL_SELF_RUN_KEYWORDS = [
    "laundromat", "coin laundry", "self-service laundry", "self serve laundry",
    "self storage", "storage units", "storage facility",
    "vending machine", "vending route", "car wash",
    "unmanned", "coin-operated", "coin operated",
]

# --- Broader asset-rich / high-barrier B2B keywords (smaller bonus) --------
# Lenders and vendors both favour these over thin-margin retail/hospitality -
# they're more financeable and more resilient, even outside the PipeTech lane.
ASSET_RICH_B2B_KEYWORDS = [
    "logistics", "freight", "trucking", "transport", "distribution", "wholesale",
    "manufactur", "fabrication", "machining", "industrial", "warehousing", "b2b",
]

# Sectors lenders are historically more cautious about financing - thin asset
# base, higher failure rates. Not disqualifying, just worth a flag.
LENDING_CAUTION_SECTORS = ["hospitality_cafe", "retail"]

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
