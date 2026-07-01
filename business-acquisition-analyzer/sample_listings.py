"""Five realistic (invented) NZ listings for demoing and sanity-checking the
scoring model. None of these are real businesses.
"""

from models import Listing

SAMPLE_LISTINGS = [
    Listing(
        name="Established Drainage & Pipe Services Co",
        source="sample",
        sector="water_infrastructure",
        region="Waikato",
        asking_price=896_000,
        revenue=1_400_000,
        earnings_value=280_000,
        earnings_basis="EBITDA",
        owner_involvement="absentee",
        manager_in_place=True,
        staff_count=9,
        years_established=15,
        reason_for_sale="Owner retirement after 15 years",
        vendor_finance_offered=True,
        days_on_market=150,
        customer_concentration_pct=10,
        recurring_revenue=True,
        contracts_in_place=True,
        raw_text=(
            "Long-established drainage and pipeline contracting business serving "
            "residential and council clients across the Waikato region. Full-time "
            "manager in place running daily operations - owner is fully absentee "
            "and involved only in high-level review. Multiple council maintenance "
            "contracts in place providing recurring revenue. Owner retiring after "
            "15 years and open to vendor finance for the right buyer."
        ),
    ),
    Listing(
        name="Popular Inner-City Cafe",
        source="sample",
        sector="hospitality_cafe",
        region="Wellington",
        asking_price=375_000,
        revenue=600_000,
        earnings_value=150_000,
        earnings_basis="SDE",
        owner_involvement="full_time",
        manager_in_place=False,
        staff_count=6,
        years_established=5,
        reason_for_sale="",
        vendor_finance_offered=False,
        days_on_market=60,
        customer_concentration_pct=None,
        recurring_revenue=False,
        contracts_in_place=False,
        raw_text=(
            "Busy owner-operator cafe in a high-foot-traffic location. Current "
            "owner is very hands-on, opening most mornings and doing the books "
            "personally. SDE of $150k reflects the owner's own labour - a buyer "
            "would need to either work in the business or hire a manager."
        ),
    ),
    Listing(
        name="Pump & Pipe Maintenance Ltd",
        source="sample",
        sector="trade_services",
        region="Bay of Plenty",
        asking_price=715_000,
        revenue=900_000,
        earnings_value=220_000,
        earnings_basis="SDE",
        owner_involvement="part_time",
        manager_in_place=False,
        staff_count=5,
        years_established=12,
        reason_for_sale="Owner relocating overseas",
        vendor_finance_offered=False,
        days_on_market=90,
        customer_concentration_pct=20,
        recurring_revenue=True,
        contracts_in_place=True,
        raw_text=(
            "Pump installation and pipe maintenance business with several council "
            "maintenance contracts providing steady recurring work. Owner works "
            "part-time, mostly on quoting and supplier relationships, with a small "
            "crew handling day-to-day jobs. Owner is relocating overseas and needs "
            "a sale within the next year."
        ),
    ),
    Listing(
        name="Thin-Margin Online Retailer",
        source="sample",
        sector="ecommerce_online",
        region="Auckland",
        asking_price=525_000,
        revenue=3_000_000,
        earnings_value=150_000,
        earnings_basis="EBITDA",
        owner_involvement="absentee",
        manager_in_place=False,
        staff_count=2,
        years_established=4,
        reason_for_sale="",
        vendor_finance_offered=False,
        days_on_market=45,
        customer_concentration_pct=5,
        recurring_revenue=False,
        contracts_in_place=False,
        raw_text=(
            "High-revenue online retail store selling homewares, fulfilled via a "
            "third-party logistics provider with no staff required for day-to-day "
            "operations. Sales are down on last year due to rising ad costs "
            "compressing already thin margins. Reported EBITDA basis, not SDE, "
            "though buyer should independently verify the figure."
        ),
    ),
    Listing(
        name="Regional Mechanical Workshop",
        source="sample",
        sector="trade_services",
        region="Canterbury",
        asking_price=495_000,
        revenue=750_000,
        earnings_value=180_000,
        earnings_basis="SDE",
        owner_involvement="full_time",
        manager_in_place=False,
        staff_count=4,
        years_established=20,
        reason_for_sale="Owner ill health, needs to sell quickly",
        vendor_finance_offered=True,
        days_on_market=200,
        customer_concentration_pct=None,
        recurring_revenue=False,
        contracts_in_place=False,
        raw_text=(
            "20-year-old mechanical workshop with a loyal local customer base. "
            "Owner-operator is hands-on in the workshop every day and is the key "
            "person for the business's biggest repair jobs. Selling due to ill "
            "health and open to vendor finance to get a deal done quickly."
        ),
    ),
]
