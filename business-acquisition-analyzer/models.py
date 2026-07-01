"""Data model for a business-for-sale listing."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    name: str
    source: str = ""
    url: str = ""
    sector: str = ""
    region: str = ""

    asking_price: Optional[float] = None
    revenue: Optional[float] = None
    earnings_value: Optional[float] = None
    earnings_basis: str = "unknown"  # EBITDA | SDE | net_profit | unknown

    owner_involvement: str = "unknown"  # absentee | part_time | full_time | unknown
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

    # Populated by scoring.py, not set at ingestion time.
    passive_ebitda: Optional[float] = None
    multiple: Optional[float] = None
