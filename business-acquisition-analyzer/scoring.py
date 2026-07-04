"""Ken Mack-style acquisition scoring for a passive, low/zero-cash-down NZ buyer.

Five weighted pillars (0-100 each), a Debt Service Coverage Ratio (DSCR)
financing-feasibility check on top, hard caps for deal-killer situations, and
a red-flag detector. Nothing here talks to a network or a database - it's
pure functions over a Listing.
"""

from typing import List

import config
from models import Listing
from nz_benchmarks import SECTOR_BANDS, get_benchmark, match_sector

MOTIVATED_SELLER_TERMS = [
    "retire", "ill health", "illness", "relocat", "must sell", "succession",
    "estate", "divorce", "no partner",
]
KEY_PERSON_TERMS = ["owner-operator", "owner operator", "hands-on", "hands on", "key person"]
PASSIVE_LANGUAGE_TERMS = ["manager in place", "fully staffed", "semi-passive", "semi passive", "absentee"]
DECLINE_TERMS = ["declining", "down on last year", "down on prior year", "lost a contract", "lost contract"]

OWNER_INVOLVEMENT_BASE = {
    "absentee": 100,
    "part_time": 55,
    "full_time": 15,
    "unknown": 40,
}

MANAGER_DEDUCTION_FACTOR = {
    "absentee": 0.0,
    "part_time": 0.5,
    "full_time": 1.0,
    "unknown": 0.75,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _linear_scale(value: float, low: float, high: float) -> float:
    """0 at `low`, 100 at `high`, clamped to [0, 100]. Handles low == high."""
    if high == low:
        return 100.0 if value >= high else 0.0
    return _clamp(100.0 * (value - low) / (high - low))


def _contains_any(text: str, terms: List[str]) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in terms)


def manager_adjusted_ebitda(listing: Listing) -> float:
    """Strip a full-time manager's cost out of owner-reported earnings.

    NZ main-street listings quote SDE/EBPITD (owner's wage added back), which
    overstates profit for a buyer who won't work in the business. If a
    manager is already in place, no deduction is needed - that cost is
    already reflected in the reported earnings.
    """
    if listing.earnings_value is None:
        return 0.0

    factor = MANAGER_DEDUCTION_FACTOR.get(listing.owner_involvement, MANAGER_DEDUCTION_FACTOR["unknown"])

    if listing.manager_in_place:
        deduction = 0
    elif listing.earnings_basis == "SDE":
        deduction = config.REPLACEMENT_MANAGER_COST
    else:
        deduction = config.REPLACEMENT_MANAGER_COST * factor

    return listing.earnings_value - deduction


def score_owner_independence(listing: Listing) -> float:
    """The 'don't buy a job' filter."""
    score = OWNER_INVOLVEMENT_BASE.get(listing.owner_involvement, OWNER_INVOLVEMENT_BASE["unknown"])
    text = f"{listing.raw_text} {listing.notes}"

    if _contains_any(text, KEY_PERSON_TERMS):
        score -= 25
    if _contains_any(text, PASSIVE_LANGUAGE_TERMS):
        score += 15
    if listing.manager_in_place:
        score = max(score, 90)

    return _clamp(score)


def score_profit_quality(passive_ebitda: float, listing: Listing) -> float:
    band = 100.0 if passive_ebitda >= config.TARGET_EBITDA_MIN else _linear_scale(
        passive_ebitda, config.EBITDA_FLOOR, config.TARGET_EBITDA_MIN
    )

    if listing.revenue and listing.revenue > 0:
        margin_ratio = passive_ebitda / listing.revenue
        margin = _linear_scale(margin_ratio, 0.10, 0.30)
    else:
        margin = 0.0

    return _clamp(0.65 * band + 0.35 * margin)


def score_valuation(listing: Listing, low: float, typ: float, high: float) -> float:
    if not listing.asking_price or not listing.earnings_value:
        return 0.0

    multiple = listing.asking_price / listing.earnings_value
    control_points = [(0.0, 100.0), (low, 100.0), (typ, 65.0), (high, 25.0), (high * 1.3, 10.0)]

    if multiple <= low:
        return 100.0
    if multiple >= high * 1.3:
        return 10.0

    for (x0, y0), (x1, y1) in zip(control_points, control_points[1:]):
        if x0 <= multiple <= x1:
            if x1 == x0:
                return y0
            return _clamp(y0 + (y1 - y0) * (multiple - x0) / (x1 - x0))

    return 10.0


def score_deal_structure(listing: Listing) -> float:
    score = 40.0
    if _contains_any(listing.reason_for_sale, MOTIVATED_SELLER_TERMS):
        score += 30
    if listing.vendor_finance_offered:
        score += 25
    if listing.days_on_market is not None and listing.days_on_market > 120:
        score += 10
    if listing.years_established is not None and listing.years_established >= 10:
        score += 5
    return _clamp(score)


def score_resilience_fit(listing: Listing) -> float:
    score = 40.0
    if listing.recurring_revenue:
        score += 20
    if listing.contracts_in_place:
        score += 15

    concentration = listing.customer_concentration_pct
    if concentration is not None:
        if concentration <= 15:
            score += 10
        elif concentration >= 30:
            score -= 20

    text = f"{listing.sector} {listing.raw_text} {listing.notes}".lower()
    if any(keyword in text for keyword in config.PIPETECH_KEYWORDS):
        score += 20
    elif any(keyword in text for keyword in config.ASSET_RICH_B2B_KEYWORDS):
        score += 10

    return _clamp(score)


def amortized_annual_payment(principal: float, annual_rate: float = None, years: int = None) -> float:
    """Standard monthly-amortized loan payment, annualized."""
    annual_rate = config.LOAN_INTEREST_RATE if annual_rate is None else annual_rate
    years = config.LOAN_TERM_YEARS if years is None else years
    n_payments = years * 12
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / years
    monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -n_payments)
    return monthly_payment * 12


def debt_service_feasibility(listing: Listing, passive_ebitda: float) -> dict:
    """Can a low/zero-cash-down purchase actually service its own debt?

    Finances FINANCED_PORTION of the asking price at LOAN_INTEREST_RATE over
    LOAN_TERM_YEARS, then checks whether *passive* (manager-adjusted) EBITDA
    covers the annual payment at MIN_DSCR - the coverage ratio most lenders
    underwrite to. Using passive EBITDA rather than raw reported earnings
    matters: a manager's wage already comes out of the cash flow before the
    loan gets serviced, for a genuinely passive buyer.
    """
    if not listing.asking_price:
        return {"risk": "UNKNOWN", "reason": "Missing asking price - can't compute debt service.",
                "annual_debt_service": None, "dscr": None}

    loan_amount = listing.asking_price * config.FINANCED_PORTION
    annual_debt_service = amortized_annual_payment(loan_amount)
    dscr = passive_ebitda / annual_debt_service if annual_debt_service else None
    feasible = dscr is not None and dscr >= config.MIN_DSCR

    return {
        "risk": "PASS" if feasible else "HIGH_RISK",
        "reason": (
            f"DSCR {dscr:.2f}x >= {config.MIN_DSCR:.2f}x minimum"
            if feasible
            else f"DSCR {dscr:.2f}x < {config.MIN_DSCR:.2f}x minimum - passive EBITDA can't safely cover the loan"
        ),
        "annual_debt_service": round(annual_debt_service, 0),
        "dscr": round(dscr, 2) if dscr is not None else None,
    }


def detect_red_flags(listing: Listing, passive_ebitda: float, financing: dict = None) -> List[str]:
    flags = []
    text = f"{listing.raw_text} {listing.notes}"

    if listing.owner_involvement == "full_time" and not listing.manager_in_place:
        flags.append("Full-time owner with no manager in place - likely a job, not a passive asset.")
    if listing.earnings_basis in ("SDE", "unknown"):
        flags.append("Earnings basis is SDE/unknown - verify it's true EBITDA before relying on the multiple.")
    if listing.customer_concentration_pct is not None and listing.customer_concentration_pct >= 25:
        flags.append(f"Customer concentration is {listing.customer_concentration_pct:.0f}% - revenue risk if that customer leaves.")
    if listing.asking_price is None or listing.earnings_value is None:
        flags.append("Missing asking price or earnings figure - can't compute a reliable multiple.")
    if _contains_any(text, DECLINE_TERMS):
        flags.append("Listing language suggests declining performance - dig into recent trend before proceeding.")
    if passive_ebitda < config.EBITDA_FLOOR:
        flags.append(f"Manager-adjusted EBITDA (${passive_ebitda:,.0f}) is below the ${config.EBITDA_FLOOR:,.0f} floor.")
    if financing and financing["risk"] == "HIGH_RISK":
        flags.append(
            f"Financing looks infeasible at {config.LOAN_INTEREST_RATE:.0%}/{config.LOAN_TERM_YEARS}yr on "
            f"{config.FINANCED_PORTION:.0%} financed ({financing['reason']}) - would need more cash down, "
            f"better terms, or a bigger vendor note."
        )
    if listing.sector in config.LENDING_CAUTION_SECTORS:
        flags.append(
            "Retail/hospitality businesses are historically harder to finance affordably (thin asset base, "
            "higher failure rates) - expect tighter lender terms than assumed here."
        )

    return flags


def score_listing(listing: Listing) -> dict:
    """Score a single listing across all five pillars and return the full result."""
    passive_ebitda = manager_adjusted_ebitda(listing)
    listing.passive_ebitda = passive_ebitda
    listing.multiple = (
        listing.asking_price / listing.earnings_value
        if listing.asking_price and listing.earnings_value
        else None
    )

    if listing.sector in SECTOR_BANDS:
        sector = listing.sector
    else:
        sector = match_sector(f"{listing.sector} {listing.raw_text}")
    basis, low, typ, high, is_fallback = get_benchmark(sector)

    pillars = {
        "owner_independence": score_owner_independence(listing),
        "profit_quality": score_profit_quality(passive_ebitda, listing),
        "valuation": score_valuation(listing, low, typ, high),
        "deal_structure": score_deal_structure(listing),
        "resilience_fit": score_resilience_fit(listing),
    }

    composite = sum(pillars[name] * weight for name, weight in config.WEIGHTS.items())

    financing = debt_service_feasibility(listing, passive_ebitda)

    # Hard caps - deal-killers for a passive, low/zero-cash-down buyer, regardless of weighted score.
    if listing.owner_involvement == "full_time" and not listing.manager_in_place:
        composite = min(composite, 45)
    if passive_ebitda <= 0:
        composite = min(composite, 25)
    if financing["dscr"] is not None and financing["dscr"] < 1.0:
        composite = min(composite, 35)  # can't even fully cover the loan payment from passive cash flow

    if composite >= config.VERDICT_SWING:
        verdict = "SWING"
    elif composite >= config.VERDICT_WATCH:
        verdict = "WATCHLIST"
    else:
        verdict = "PASS"

    red_flags = detect_red_flags(listing, passive_ebitda, financing)

    return {
        "listing": listing,
        "passive_ebitda": passive_ebitda,
        "multiple": listing.multiple,
        "sector": sector,
        "sector_basis": basis,
        "sector_band": (low, typ, high),
        "sector_band_is_fallback": is_fallback,
        "pillars": pillars,
        "financing": financing,
        "composite": round(composite, 1),
        "verdict": verdict,
        "red_flags": red_flags,
    }


def rank(listings: List[Listing]) -> List[dict]:
    """Score every listing and return results sorted best-to-worst."""
    results = [score_listing(listing) for listing in listings]
    return sorted(results, key=lambda r: r["composite"], reverse=True)
