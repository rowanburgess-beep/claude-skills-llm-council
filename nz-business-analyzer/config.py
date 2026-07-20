"""Editable constants for the NZ Business Acquisition Analyzer.

Everything a buyer might want to recalibrate (target profit band, pillar
weights, verdict thresholds, the cost of a replacement manager) lives here so
the rest of the codebase never hardcodes a number.
"""

# --- Passive-EBITDA calculation ---------------------------------------------
# Annual NZD cost to install a full-time manager, used to strip "owner's wage"
# back out of SDE-quoted listings so a passive buyer isn't overpaying for a job.
REPLACEMENT_MANAGER_COST = 110_000

# When earnings are already reported closer to a "true" EBITDA (not SDE) and no
# manager is in place yet, only a fraction of the replacement cost applies,
# scaled by how involved the current owner already is.
OWNER_INVOLVEMENT_FACTORS = {
    "absentee": 0.0,
    "part_time": 0.5,
    "full_time": 1.0,
    "unknown": 0.75,
}

# --- Target acquisition profile ---------------------------------------------
TARGET_EBITDA_MIN = 200_000
TARGET_EBITDA_MAX = 300_000
EBITDA_FLOOR = 100_000
MIN_MARGIN = 0.20

# --- Pillar weights (must sum to 1.0) ---------------------------------------
WEIGHTS = {
    "owner_independence": 0.30,
    "profit_quality": 0.25,
    "valuation": 0.20,
    "deal_structure": 0.15,
    "resilience_fit": 0.10,
}

# --- Verdict thresholds ------------------------------------------------------
VERDICT_SWING = 70
VERDICT_WATCH = 50
ALERT_COMPOSITE_MIN = 70

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "WEIGHTS must sum to 1.0"
