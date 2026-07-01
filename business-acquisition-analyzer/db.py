"""Optional Postgres persistence for scored listings.

Entirely opt-in: every function no-ops (returns None / False) if DATABASE_URL
isn't configured, so the app and demo work fine without Postgres installed.
"""

import json

import config

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def is_configured() -> bool:
    return bool(config.DATABASE_URL) and psycopg2 is not None


def get_connection():
    if not is_configured():
        return None
    return psycopg2.connect(config.DATABASE_URL)


def init_schema() -> None:
    """Apply schema.sql. No-op if Postgres isn't configured."""
    conn = get_connection()
    if conn is None:
        return
    try:
        with open("schema.sql") as f:
            ddl = f.read()
        with conn, conn.cursor() as cur:
            cur.execute(ddl)
    finally:
        conn.close()


def save_result(result: dict) -> None:
    """Persist a scored listing and its opportunity-tracking row.

    No-op if Postgres isn't configured - the app must work without a DB.
    """
    conn = get_connection()
    if conn is None:
        return

    listing = result["listing"]
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO businesses_for_sale (name, source, url, sector, region, raw_text, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (listing.name, listing.source, listing.url, result["sector"], listing.region,
                 listing.raw_text, listing.notes),
            )
            business_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO listing_financials
                    (business_id, asking_price, revenue, earnings_value, earnings_basis, passive_ebitda, multiple)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (business_id, listing.asking_price, listing.revenue, listing.earnings_value,
                 listing.earnings_basis, result["passive_ebitda"], listing.multiple),
            )

            cur.execute(
                """
                INSERT INTO owner_dependency
                    (business_id, owner_involvement, manager_in_place, staff_count, years_established)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (business_id, listing.owner_involvement, listing.manager_in_place,
                 listing.staff_count, listing.years_established),
            )

            cur.execute(
                """
                INSERT INTO deal_signals
                    (business_id, reason_for_sale, vendor_finance_offered, days_on_market,
                     customer_concentration_pct, recurring_revenue, contracts_in_place)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (business_id, listing.reason_for_sale, listing.vendor_finance_offered,
                 listing.days_on_market, listing.customer_concentration_pct,
                 listing.recurring_revenue, listing.contracts_in_place),
            )

            cur.execute(
                """
                INSERT INTO opportunities_tracked
                    (business_id, composite_score, verdict, pillar_scores, red_flags)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (business_id, result["composite"], result["verdict"],
                 json.dumps(result["pillars"]), json.dumps(result["red_flags"])),
            )
    finally:
        conn.close()
