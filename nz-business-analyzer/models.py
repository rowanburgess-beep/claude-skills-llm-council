"""Core data model for a business-for-sale listing."""
from dataclasses import dataclass
from typing import Optional

EarningsBasis = str  # "EBITDA" | "SDE" | "net_profit" | "unknown"
OwnerInvolvement = str  # "absentee" | "part_time" | "full_time" | "unknown"


@dataclass
class Listing:
    name: str
    source: str = "manual"
    url: str = ""
    sector: str = ""
    region: str = ""

    asking_price: Optional[float] = None
    revenue: Optional[float] = None
    earnings_value: Optional[float] = None
    earnings_basis: EarningsBasis = "unknown"

    owner_involvement: OwnerInvolvement = "unknown"
    manager_in_place: bool = False
    staff_count: Optional[int] = None
    years_established: Optional[int] = None

    reason_for_sale: str = ""
    vendor_finance_offered: bool = False
    days_on_market: Optional[int] = None

    customer_concentration_pct: Optional[float] = None
    recurring_revenue: bool = False
    contracts_in_place: bool = False

    raw_text: str = ""
    notes: str = ""

    # Computed by scoring.score_listing() — left as None until scored.
    passive_ebitda: Optional[float] = None
    multiple: Optional[float] = None
