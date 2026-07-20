"""Five realistic (invented) NZ listings used to sanity-check the scoring engine.

None of these are real businesses or real listings — they're calibration
fixtures chosen to exercise the scoring logic across the spectrum: a truly
passive asset, a disguised job, a partially-passive trade business, a
vanity-revenue retailer, and a motivated-seller business that still can't
clear the "don't buy a job" bar.
"""
from typing import List

from models import Listing


def get_sample_listings() -> List[Listing]:
    return [
        Listing(
            name="Established Drainage & Civil Contracting Business",
            source="manual",
            sector="Civil / Drainage Contracting",
            region="Waikato",
            asking_price=850_000,
            revenue=1_400_000,
            earnings_value=280_000,
            earnings_basis="EBITDA",
            owner_involvement="absentee",
            manager_in_place=True,
            staff_count=14,
            years_established=18,
            reason_for_sale="Owner retiring after 20 years in the industry and relocating overseas",
            vendor_finance_offered=True,
            days_on_market=150,
            customer_concentration_pct=12,
            recurring_revenue=True,
            contracts_in_place=True,
            raw_text=(
                "Established residential and commercial drainage and civil earthworks contracting "
                "business, fully staffed with an experienced manager in place who runs day-to-day "
                "operations. Long-standing council contracts provide recurring, contracted revenue. "
                "The current owner is absentee and has not worked in the field for several years. "
                "Reason for sale: owner retiring after 20 years and relocating overseas."
            ),
            notes="Sample listing for calibration — invented, not a real business.",
        ),
        Listing(
            name="Popular Suburban Cafe",
            source="manual",
            sector="Cafe",
            region="Auckland",
            asking_price=320_000,
            revenue=650_000,
            earnings_value=150_000,
            earnings_basis="SDE",
            owner_involvement="full_time",
            manager_in_place=False,
            staff_count=6,
            years_established=6,
            reason_for_sale="Owner wants a lifestyle change and more time with family",
            vendor_finance_offered=False,
            days_on_market=60,
            customer_concentration_pct=5,
            recurring_revenue=False,
            contracts_in_place=False,
            raw_text=(
                "Well-known suburban cafe with a loyal following. This is very much an "
                "owner-operator business — the current owner is hands-on every day, opening up, "
                "managing the till and running the floor, with no manager currently employed. "
                "Reason for sale: owner wants a lifestyle change and more time with family."
            ),
            notes="Sample listing for calibration — invented, not a real business.",
        ),
        Listing(
            name="Rural Plumbing & Pump Installation Company",
            source="manual",
            sector="Plumbing & Pump Services",
            region="Bay of Plenty",
            asking_price=700_000,
            revenue=1_000_000,
            earnings_value=240_000,
            earnings_basis="SDE",
            owner_involvement="part_time",
            manager_in_place=False,
            staff_count=8,
            years_established=15,
            reason_for_sale="Owner wants to focus on other business interests",
            vendor_finance_offered=False,
            days_on_market=90,
            customer_concentration_pct=18,
            recurring_revenue=True,
            contracts_in_place=True,
            raw_text=(
                "Specialising in plumbing and pump installation contracting for residential and "
                "rural clients across the lower North Island. The current owner works roughly "
                "15-20 hours a week on quoting and supplier relationships, while a full-time "
                "supervisor runs the day-to-day jobs. No general manager is employed yet. "
                "Reason for sale: owner wants to focus on other business interests."
            ),
            notes="Sample listing for calibration — invented, not a real business.",
        ),
        Listing(
            name="High-Growth Online Homeware Retailer",
            source="manual",
            sector="Online Retail / Ecommerce",
            region="Nationwide (online)",
            asking_price=450_000,
            revenue=3_000_000,
            earnings_value=180_000,
            earnings_basis="SDE",
            owner_involvement="part_time",
            manager_in_place=False,
            staff_count=3,
            years_established=4,
            reason_for_sale="Founder pursuing a new venture",
            vendor_finance_offered=False,
            days_on_market=45,
            customer_concentration_pct=8,
            recurring_revenue=False,
            contracts_in_place=False,
            raw_text=(
                "This ecommerce business runs a single online store selling homeware products "
                "via dropship fulfilment, with strong topline growth. The founder spends roughly "
                "15 hours a week on supplier negotiations and marketing; no manager is in place. "
                "Reason for sale: founder pursuing a new venture."
            ),
            notes="Sample listing for calibration — invented, not a real business.",
        ),
        Listing(
            name="Long-Established Mechanical Workshop",
            source="manual",
            sector="Mechanical Workshop",
            region="Canterbury",
            asking_price=480_000,
            revenue=900_000,
            earnings_value=200_000,
            earnings_basis="SDE",
            owner_involvement="full_time",
            manager_in_place=False,
            staff_count=5,
            years_established=22,
            reason_for_sale="Owner diagnosed with a serious illness and needs to stop working immediately",
            vendor_finance_offered=True,
            days_on_market=200,
            customer_concentration_pct=10,
            recurring_revenue=False,
            contracts_in_place=False,
            raw_text=(
                "Long-established automotive mechanical workshop with a loyal customer base. The "
                "owner is a hands-on, owner-operator tradesman who works in the workshop full-time; "
                "there is no manager in place. Vendor finance available to the right buyer. "
                "Reason for sale: owner diagnosed with a serious illness and needs to stop working "
                "immediately."
            ),
            notes="Sample listing for calibration — invented, not a real business.",
        ),
    ]
