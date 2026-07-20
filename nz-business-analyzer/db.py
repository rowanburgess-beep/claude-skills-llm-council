"""Optional PostgreSQL persistence.

Everything in this module is a no-op if DATABASE_URL isn't set or psycopg2
isn't installed — the rest of the app must never crash because Postgres
isn't configured.
"""
import json
import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

DATABASE_URL = os.environ.get("DATABASE_URL")


def is_configured() -> bool:
    return bool(DATABASE_URL and psycopg2)


def get_connection():
    if not is_configured():
        return None
    return psycopg2.connect(DATABASE_URL)


def init_schema() -> bool:
    conn = get_connection()
    if conn is None:
        return False
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        sql = f.read()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        return True
    finally:
        conn.close()


def save_result(result) -> bool:
    """Persist a scoring.ScoreResult to Postgres. Silently returns False if not configured."""
    conn = get_connection()
    if conn is None:
        return False
    listing = result.listing
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO businesses_for_sale (name, source, url, sector, region, raw_text, notes)
                       VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (listing.name, listing.source, listing.url, listing.sector,
                     listing.region, listing.raw_text, listing.notes),
                )
                listing_id = cur.fetchone()[0]

                cur.execute(
                    """INSERT INTO listing_financials
                       (listing_id, asking_price, revenue, earnings_value, earnings_basis, passive_ebitda, multiple)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (listing_id, listing.asking_price, listing.revenue, listing.earnings_value,
                     listing.earnings_basis, listing.passive_ebitda, listing.multiple),
                )

                cur.execute(
                    """INSERT INTO owner_dependency
                       (listing_id, owner_involvement, manager_in_place, staff_count, years_established)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (listing_id, listing.owner_involvement, listing.manager_in_place,
                     listing.staff_count, listing.years_established),
                )

                cur.execute(
                    """INSERT INTO deal_signals
                       (listing_id, reason_for_sale, vendor_finance_offered, days_on_market,
                        customer_concentration_pct, recurring_revenue, contracts_in_place)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (listing_id, listing.reason_for_sale, listing.vendor_finance_offered,
                     listing.days_on_market, listing.customer_concentration_pct,
                     listing.recurring_revenue, listing.contracts_in_place),
                )

                cur.execute(
                    """INSERT INTO opportunities_tracked
                       (listing_id, composite_score, verdict, pillar_scores, red_flags)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (listing_id, result.composite, result.verdict,
                     json.dumps(result.pillars), json.dumps(result.red_flags)),
                )
        return True
    finally:
        conn.close()
