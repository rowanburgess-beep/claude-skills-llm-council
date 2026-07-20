"""Five-pillar scoring engine for the NZ Business Acquisition Analyzer.

See BLUEPRINT.md for how each pillar maps to Ken Mack's acquisition principles.
Constants are read off the `config` module (not imported by value) so a caller
— e.g. the Streamlit sidebar — can override config.REPLACEMENT_MANAGER_COST
etc. at runtime and have it take effect on the next score_listing() call.
"""
from dataclasses import dataclass, field
from typing import List, Tuple

import config
from models import Listing
from nz_benchmarks import SectorBand, match_sector


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _interp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """Linearly interpolate y for x between (x0, y0) and (x1, y1)."""
    if x1 == x0:
        return y1 if x >= x1 else y0
    frac = (x - x0) / (x1 - x0)
    return y0 + frac * (y1 - y0)


def manager_adjusted_ebitda(listing: Listing) -> float:
    """Strip a full-time replacement manager's cost out of reported earnings.

    NZ main-street listings quote SDE (owner's wage added back), which
    overstates profit for a buyer who won't work in the business. If a
    manager is already in place there's nothing to add back. Otherwise, an
    SDE-basis listing gets the full replacement-manager cost deducted; an
    EBITDA/net_profit/unknown-basis listing gets a partial deduction scaled
    by how involved the current owner already is (config.OWNER_INVOLVEMENT_FACTORS).
    """
    if listing.earnings_value is None:
        return 0.0
    factor = config.OWNER_INVOLVEMENT_FACTORS.get(
        listing.owner_involvement, config.OWNER_INVOLVEMENT_FACTORS["unknown"]
    )
    if listing.manager_in_place:
        deduction = 0.0
    elif listing.earnings_basis == "SDE":
        deduction = config.REPLACEMENT_MANAGER_COST
    else:
        deduction = config.REPLACEMENT_MANAGER_COST * factor
    return listing.earnings_value - deduction


_OWNER_INDEPENDENCE_BASE = {"absentee": 100, "part_time": 55, "full_time": 15, "unknown": 40}
_HANDS_ON_PHRASES = ("owner-operator", "owner operator", "hands-on", "hands on", "key person", "key-person")
_PASSIVE_PHRASES = ("manager in place", "fully staffed", "semi-passive", "semi passive", "absentee")


def score_owner_independence(listing: Listing) -> float:
    """The "don't buy a job" filter — rewards businesses that already run without the owner."""
    score = _OWNER_INDEPENDENCE_BASE.get(listing.owner_involvement, _OWNER_INDEPENDENCE_BASE["unknown"])
    text = f"{listing.raw_text} {listing.notes}".lower()
    if listing.manager_in_place:
        score = max(score, 90)
    if any(p in text for p in _HANDS_ON_PHRASES):
        score -= 25
    if any(p in text for p in _PASSIVE_PHRASES):
        score += 15
    return _clamp(score)


def score_profit_quality(listing: Listing) -> float:
    """0.65 * (how close passive EBITDA is to the target band) + 0.35 * (margin quality)."""
    passive = listing.passive_ebitda or 0.0
    if passive >= config.TARGET_EBITDA_MIN:
        band = 100.0
    else:
        band = _clamp(_interp(passive, config.EBITDA_FLOOR, config.TARGET_EBITDA_MIN, 0, 100))
    if listing.revenue and listing.revenue > 0:
        margin_ratio = passive / listing.revenue
        margin = _clamp(_interp(margin_ratio, 0.10, 0.30, 0, 100))
    else:
        margin = 0.0
    return _clamp(0.65 * band + 0.35 * margin)


def score_valuation(listing: Listing, band: SectorBand) -> Tuple[float, List[str]]:
    """Score asking_price / earnings_value against the sector's own quoting basis.

    A mismatch between the listing's reported earnings_basis and the sector's
    typical quoting basis is flagged rather than silently blended — SDE and
    EBITDA multiples for the same business are not interchangeable, and mixing
    them would make an average business look artificially cheap or expensive.
    """
    flags: List[str] = []
    if not listing.asking_price or not listing.earnings_value:
        return 50.0, ["Insufficient price/earnings data to score valuation — treated as neutral."]

    multiple = listing.asking_price / listing.earnings_value

    if listing.earnings_basis != "unknown" and listing.earnings_basis != band.basis:
        flags.append(
            f"Earnings reported on a {listing.earnings_basis} basis, but {band.label} listings are "
            f"typically quoted on {band.basis} — this multiple is not directly comparable to the band."
        )

    if multiple <= band.low:
        score = 100.0
    elif multiple <= band.typ:
        score = _interp(multiple, band.low, band.typ, 100, 65)
    elif multiple <= band.high:
        score = _interp(multiple, band.typ, band.high, 65, 25)
    elif multiple <= band.high * 1.3:
        score = _interp(multiple, band.high, band.high * 1.3, 25, 10)
    else:
        score = _interp(multiple, band.high * 1.3, band.high * 1.6, 10, 0)

    return _clamp(score), flags


_MOTIVATED_SELLER_KEYWORDS = (
    "retire", "ill health", "illness", "health reasons", "relocat",
    "must sell", "succession", "estate", "divorce",
)


def score_deal_structure(listing: Listing) -> float:
    """Rewards the conditions that make a low-money-down, vendor-assisted deal possible."""
    score = 40.0
    reason = (listing.reason_for_sale or "").lower()
    if any(kw in reason for kw in _MOTIVATED_SELLER_KEYWORDS):
        score += 30
    if listing.vendor_finance_offered:
        score += 25
    if listing.days_on_market and listing.days_on_market > 120:
        score += 10
    if listing.years_established and listing.years_established >= 10:
        score += 5
    return _clamp(score)


_PIPETECH_KEYWORDS = (
    "drainage", "civil", "water", "three waters", "pipeline", "trenchless",
    "infrastructure", "council", "wastewater", "stormwater", "excavation",
    "contracting", "plumbing",
)


def score_resilience_fit(listing: Listing) -> float:
    score = 40.0
    if listing.recurring_revenue:
        score += 20
    if listing.contracts_in_place:
        score += 15
    cc = listing.customer_concentration_pct
    if cc is not None:
        if cc <= 15:
            score += 10
        elif cc >= 30:
            score -= 20
    text = f"{listing.sector} {listing.raw_text} {listing.notes}".lower()
    if any(kw in text for kw in _PIPETECH_KEYWORDS):
        score += 20
    return _clamp(score)


def red_flags(listing: Listing) -> List[str]:
    flags = []
    if listing.owner_involvement == "full_time" and not listing.manager_in_place:
        flags.append("Full-time owner-operator with no manager in place — this is a job, not a passive asset.")
    if listing.passive_ebitda is not None and listing.passive_ebitda <= 0:
        flags.append("Manager-adjusted EBITDA is zero or negative once a replacement manager is costed in.")
    if listing.customer_concentration_pct is not None and listing.customer_concentration_pct >= 30:
        flags.append(f"High customer concentration ({listing.customer_concentration_pct:.0f}% from top customer(s)).")
    if listing.revenue and listing.passive_ebitda is not None and listing.revenue > 0:
        margin = listing.passive_ebitda / listing.revenue
        if margin < config.MIN_MARGIN:
            flags.append(f"Passive-adjusted margin ({margin:.0%}) is below the {config.MIN_MARGIN:.0%} comfort floor.")
    if listing.earnings_basis == "unknown":
        flags.append("Earnings basis not disclosed — treat any multiple with caution.")
    return flags


@dataclass
class ScoreResult:
    listing: Listing
    pillars: dict
    composite: float
    verdict: str
    band: SectorBand
    red_flags: List[str] = field(default_factory=list)


def score_listing(listing: Listing) -> ScoreResult:
    listing.passive_ebitda = manager_adjusted_ebitda(listing)
    band = match_sector(listing.sector, listing.raw_text)
    listing.multiple = (
        listing.asking_price / listing.earnings_value
        if listing.asking_price and listing.earnings_value
        else None
    )

    valuation_score, valuation_flags = score_valuation(listing, band)
    pillars = {
        "owner_independence": score_owner_independence(listing),
        "profit_quality": score_profit_quality(listing),
        "valuation": valuation_score,
        "deal_structure": score_deal_structure(listing),
        "resilience_fit": score_resilience_fit(listing),
    }

    composite = sum(pillars[k] * config.WEIGHTS[k] for k in config.WEIGHTS)

    # Hard caps: no pillar combination should rescue a deal a passive buyer can't live with.
    if listing.owner_involvement == "full_time" and not listing.manager_in_place:
        composite = min(composite, 45)
    if listing.passive_ebitda is not None and listing.passive_ebitda <= 0:
        composite = min(composite, 25)

    if composite >= config.VERDICT_SWING:
        verdict = "SWING"
    elif composite >= config.VERDICT_WATCH:
        verdict = "WATCHLIST"
    else:
        verdict = "PASS"

    flags = red_flags(listing) + valuation_flags

    return ScoreResult(
        listing=listing,
        pillars={k: round(v, 1) for k, v in pillars.items()},
        composite=round(composite, 1),
        verdict=verdict,
        band=band,
        red_flags=flags,
    )


def rank(listings: List[Listing]) -> List[ScoreResult]:
    results = [score_listing(l) for l in listings]
    results.sort(key=lambda r: r.composite, reverse=True)
    return results
