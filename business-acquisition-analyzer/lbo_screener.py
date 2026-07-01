"""
LBO / "Zero-Cash-Down" Acquisition Screener
============================================

A standalone screener for a *different* acquisition style than the NZ
passive-buyer tool elsewhere in this folder. That tool asks "can I own this
without working in it?" (Ken Mack, NZ SDE/EBPITD convention). This one asks a
narrower, US-style question: "can a 100%-debt-financed purchase of this
business service its own loan?" — the classic searchfund / ETA "zero-cash-
down" LBO test, aimed at BizBuySell-style listings or broker PDFs.

Four filters, applied in order:

1. FINANCIAL SIFT      — revenue, SDE, and margin inside a fundable band.
2. INDUSTRY FILTER      — asset-rich / B2B / high-barrier services preferred;
                          retail, restaurants, and pre-revenue tech are out.
3. MOTIVATION FLAGS     — keyword scan for a motivated seller (better terms).
4. FINANCING FEASIBILITY — can the business's own cash flow service a 100%-
                          financed loan on the asking price, with a safety
                          margin left over?

Nothing here talks to a network, a database, or an LLM — it's pure functions
over a Listing, the same design as scoring.py in this folder.
"""

from dataclasses import dataclass
from typing import List, Optional
import re

# ---------------------------------------------------------------------------
# Configuration — every assumption an analyst would want to tune sits here.
# ---------------------------------------------------------------------------

REVENUE_MIN = 1_000_000
REVENUE_MAX = 5_000_000
SDE_MIN = 200_000
SDE_MAX = 1_000_000
MIN_NET_MARGIN = 0.15  # net profit / revenue

LOAN_INTEREST_RATE = 0.10  # conservative rate for an Asset-Based or SBA-style loan
LOAN_TERM_YEARS = 5
# Note: 5 years is a short, aggressive term for a full acquisition loan - real
# SBA 7(a) loans for goodwill/business acquisition commonly run 10 years,
# which roughly halves the annual payment and is far easier to clear on DSCR.
# Kept at 5 per the brief; change here if you want the more typical 10-year term.
MAX_DEBT_SERVICE_SHARE = 0.80  # of SDE, at most, spent on annual debt service

# Capping debt service at 80% of SDE and requiring a 20% buffer for a hired
# manager are the same constraint stated two ways: they both reduce to
#     SDE / annual_debt_service >= 1 / MAX_DEBT_SERVICE_SHARE
# i.e. a Debt Service Coverage Ratio (DSCR) of >= 1.25x. That number isn't a
# coincidence - it's the minimum DSCR most SBA 7(a) lenders underwrite to, so
# this filter models real lending appetite rather than an arbitrary rule.
MIN_DSCR = 1 / MAX_DEBT_SERVICE_SHARE  # 1.25

INDUSTRY_WHITELIST = [
    "logistics", "freight", "trucking", "transport", "distribution", "wholesale",
    "hvac", "heating", "air conditioning", "mechanical contracting",
    "manufactur", "fabrication", "machining", "industrial", "warehousing",
    "b2b", "business-to-business", "field service", "facilities maintenance",
]

INDUSTRY_BLACKLIST = [
    "retail store", "retail shop", "restaurant", "cafe", "coffee shop", "bar",
    "e-commerce", "ecommerce", "online store",
    "pre-revenue", "pre revenue", "startup", "saas startup",
]

MOTIVATION_KEYWORDS = [
    "retirement", "retiring", "relocating", "relocation",
    "health forces sale", "health reasons", "no partner", "absentee owner",
]


@dataclass
class Listing:
    name: str
    source: str = ""
    industry: str = ""
    description: str = ""
    revenue: Optional[float] = None
    sde: Optional[float] = None  # SDE / EBITDA, used interchangeably per BizBuySell convention
    net_profit: Optional[float] = None
    asking_price: Optional[float] = None
    raw_text: str = ""


# ---------------------------------------------------------------------------
# Parsing — pull structured fields out of raw listing text or a broker PDF.
# ---------------------------------------------------------------------------

def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from a broker PDF. Requires `pip install pdfplumber`."""
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is required to parse PDFs: pip install pdfplumber") from exc
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _find_money(text: str, labels: List[str]) -> Optional[float]:
    for label in labels:
        pattern = re.compile(label + r"[^$\n]{0,25}\$\s?([\d,]+(?:\.\d+)?)\s*(k|m|million)?", re.IGNORECASE)
        m = pattern.search(text)
        if m:
            value = float(m.group(1).replace(",", ""))
            suffix = (m.group(2) or "").lower()
            if suffix == "k":
                value *= 1_000
            elif suffix in ("m", "million"):
                value *= 1_000_000
            return value
    return None


def parse_listing(raw_text: str, name: str = "Unnamed listing", source: str = "pasted") -> Listing:
    """Best-effort extraction from unstructured listing text. Always verify
    against the source document - this is a first pass, not ground truth."""
    text = raw_text or ""

    return Listing(
        name=name,
        source=source,
        industry="",
        description=text,
        revenue=_find_money(text, [r"revenue", r"gross revenue", r"annual revenue", r"sales"]),
        sde=_find_money(text, [r"sde", r"cash flow", r"ebitda", r"owner'?s? benefit"]),
        net_profit=_find_money(text, [r"net profit", r"net income"]),
        asking_price=_find_money(text, [r"asking", r"price"]),
        raw_text=text,
    )


# ---------------------------------------------------------------------------
# Filter 1: financial sift
# ---------------------------------------------------------------------------

def financial_sift(listing: Listing) -> (bool, List[str]):
    """Revenue, SDE, and margin must all sit inside a fundable band."""
    reasons = []

    if listing.revenue is None or not (REVENUE_MIN <= listing.revenue <= REVENUE_MAX):
        reasons.append(f"Revenue outside ${REVENUE_MIN:,}-${REVENUE_MAX:,} band (got {listing.revenue})")

    if listing.sde is None or not (SDE_MIN <= listing.sde <= SDE_MAX):
        reasons.append(f"SDE/EBITDA outside ${SDE_MIN:,}-${SDE_MAX:,} band (got {listing.sde})")

    if listing.net_profit is not None and listing.revenue:
        margin = listing.net_profit / listing.revenue
        if margin <= MIN_NET_MARGIN:
            reasons.append(f"Net margin {margin:.1%} <= {MIN_NET_MARGIN:.0%} minimum")
    else:
        reasons.append("Net profit margin unknown - can't confirm it clears 15%")

    return (len(reasons) == 0, reasons)


# ---------------------------------------------------------------------------
# Filter 2: industry filter
# ---------------------------------------------------------------------------

def industry_filter(listing: Listing) -> (str, str):
    """Returns (status, reason). status is one of:
    'qualified' (whitelist hit, no blacklist hit),
    'disqualified' (blacklist hit),
    'needs_review' (neither list matched - not auto-rejected, not confirmed)."""
    text = f"{listing.industry} {listing.description}".lower()

    for term in INDUSTRY_BLACKLIST:
        if term in text:
            return ("disqualified", f"Matched disqualifying industry term: '{term}'")

    for term in INDUSTRY_WHITELIST:
        if term in text:
            return ("qualified", f"Matched preferred industry term: '{term}'")

    return ("needs_review", "No industry keyword matched either list - classify manually")


# ---------------------------------------------------------------------------
# Filter 3: seller motivation
# ---------------------------------------------------------------------------

def seller_motivation_score(listing: Listing) -> (int, List[str]):
    """Counts motivated-seller language. Higher score = more room to
    negotiate price, terms, or a seller note."""
    text = f"{listing.description} {listing.raw_text}".lower()
    matched = [kw for kw in MOTIVATION_KEYWORDS if kw in text]
    return (len(matched), matched)


# ---------------------------------------------------------------------------
# Filter 4: financing feasibility (DSCR on a 100%-financed purchase)
# ---------------------------------------------------------------------------

def amortized_annual_payment(principal: float, annual_rate: float = LOAN_INTEREST_RATE,
                              years: int = LOAN_TERM_YEARS) -> float:
    """Standard monthly-amortized loan payment, annualized."""
    n_payments = years * 12
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / years
    monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -n_payments)
    return monthly_payment * 12


def debt_service_feasibility(listing: Listing) -> dict:
    """Assumes a zero-cash-down purchase: the full asking price is financed.
    Feasible when DSCR (SDE / annual debt service) clears MIN_DSCR (1.25x),
    which is equivalent to debt service costing no more than 80% of SDE and
    leaving a 20% buffer for a hired manager's pay."""
    if not listing.asking_price or not listing.sde:
        return {
            "risk": "UNKNOWN",
            "reason": "Missing asking price or SDE - can't compute debt service",
            "annual_debt_service": None,
            "dscr": None,
        }

    annual_debt_service = amortized_annual_payment(listing.asking_price)
    dscr = listing.sde / annual_debt_service if annual_debt_service else None
    manager_buffer = listing.sde - annual_debt_service

    feasible = dscr is not None and dscr >= MIN_DSCR
    return {
        "risk": "PASS" if feasible else "HIGH_RISK",
        "reason": (
            f"DSCR {dscr:.2f}x >= {MIN_DSCR:.2f}x minimum"
            if feasible
            else f"DSCR {dscr:.2f}x < {MIN_DSCR:.2f}x minimum - debt service would eat too much of SDE"
        ),
        "annual_debt_service": round(annual_debt_service, 0),
        "dscr": round(dscr, 2) if dscr is not None else None,
        "manager_buffer": round(manager_buffer, 0),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def screen_listing(listing: Listing) -> dict:
    sift_ok, sift_reasons = financial_sift(listing)
    industry_status, industry_reason = industry_filter(listing)
    motivation_count, motivation_flags = seller_motivation_score(listing)
    financing = debt_service_feasibility(listing)

    if industry_status == "disqualified":
        verdict = "DISQUALIFIED"
    elif not sift_ok:
        verdict = "OUT_OF_RANGE"
    elif financing["risk"] == "HIGH_RISK":
        verdict = "HIGH_RISK"
    elif financing["risk"] == "UNKNOWN":
        verdict = "NEEDS_DATA"
    else:
        verdict = "PASS"

    return {
        "listing": listing,
        "verdict": verdict,
        "financial_sift": {"passed": sift_ok, "reasons": sift_reasons},
        "industry": {"status": industry_status, "reason": industry_reason},
        "seller_motivation": {"score": motivation_count, "flags": motivation_flags},
        "financing": financing,
    }


def screen_all(listings: List[Listing]) -> List[dict]:
    """Screen every listing, best financing (highest DSCR) first."""
    results = [screen_listing(l) for l in listings]
    return sorted(
        results,
        key=lambda r: (r["financing"]["dscr"] if r["financing"]["dscr"] is not None else -1),
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Self-test / example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    samples = [
        Listing(
            name="Regional Freight Logistics Co",
            source="sample",
            industry="Logistics / Trucking",
            description=(
                "B2B freight logistics company with long-term contracts and asset-heavy "
                "fleet. Owner retiring after 18 years, no partner to take over."
            ),
            revenue=3_200_000,
            sde=550_000,
            net_profit=520_000,
            asking_price=1_900_000,
        ),
        Listing(
            name="Downtown Family Restaurant",
            source="sample",
            industry="Restaurant",
            description="Popular family restaurant, owner relocating out of state.",
            revenue=1_400_000,
            sde=260_000,
            net_profit=180_000,
            asking_price=650_000,
        ),
        Listing(
            name="Premium HVAC Install & Service",
            source="sample",
            industry="HVAC",
            description="Residential and commercial HVAC install/service business. Health forces sale.",
            revenue=2_800_000,
            sde=480_000,
            net_profit=460_000,
            asking_price=3_600_000,  # priced high relative to SDE - should fail DSCR
        ),
        Listing(
            name="B2B Industrial Distribution",
            source="sample",
            industry="Wholesale Distribution",
            description="Asset-rich B2B distributor of industrial parts. Absentee owner, no partner.",
            revenue=4_100_000,
            sde=310_000,
            net_profit=250_000,
            asking_price=1_100_000,
        ),
        Listing(
            name="Pre-Revenue SaaS Startup",
            source="sample",
            industry="Technology",
            description="Pre-revenue tech startup with a promising product roadmap.",
            revenue=None,
            sde=None,
            net_profit=None,
            asking_price=500_000,
        ),
    ]

    results = screen_all(samples)

    print("=" * 78)
    print("LBO / ZERO-CASH-DOWN ACQUISITION SCREEN")
    print("=" * 78)
    for r in results:
        l = r["listing"]
        print(f"\n{l.name} — {r['verdict']}")
        print(f"  Industry: {r['industry']['status']} ({r['industry']['reason']})")
        print(f"  Financial sift: {'PASS' if r['financial_sift']['passed'] else 'FAIL'} "
              f"{'' if r['financial_sift']['passed'] else '- ' + '; '.join(r['financial_sift']['reasons'])}")
        f = r["financing"]
        if f["dscr"] is not None:
            print(f"  Financing: DSCR {f['dscr']}x, annual debt service ${f['annual_debt_service']:,.0f}, "
                  f"manager buffer ${f['manager_buffer']:,.0f} — {f['reason']}")
        else:
            print(f"  Financing: {f['reason']}")
        print(f"  Seller motivation score: {r['seller_motivation']['score']} {r['seller_motivation']['flags']}")
