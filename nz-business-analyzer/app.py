"""Streamlit dashboard for the NZ Business Acquisition Analyzer.

Run: streamlit run app.py

Listings live in st.session_state for the life of the browser session —
deliberately not in browser localStorage. Nothing here scrapes a listing
site: ingestion is paste-a-listing only. See README.md.
"""
import pandas as pd
import streamlit as st

import config
import db
from alerts import maybe_alert
from parser import parse_listing
from sample_listings import get_sample_listings
from scoring import rank

st.set_page_config(page_title="NZ Business Acquisition Analyzer", layout="wide")

if "listings" not in st.session_state:
    st.session_state.listings = get_sample_listings()

st.sidebar.header("Calibration")
config.REPLACEMENT_MANAGER_COST = st.sidebar.number_input(
    "Replacement manager cost (NZD/yr)",
    min_value=0,
    value=config.REPLACEMENT_MANAGER_COST,
    step=5_000,
    help="Annual cost of installing a manager, stripped out of owner-inclusive earnings.",
)
bargain_factor = st.sidebar.slider(
    "Flag as a 'bargain' when multiple ≤ sector low × this factor",
    min_value=0.5,
    max_value=1.5,
    value=1.0,
    step=0.05,
)
st.sidebar.divider()
st.sidebar.caption(
    "⚠️ Financials are seller-provided and unverified. This tool triages candidates; "
    "it does not replace due diligence — verify every figure before any LOI."
)
if db.is_configured():
    st.sidebar.success("Postgres persistence: connected")
else:
    st.sidebar.info("Postgres persistence: not configured (optional)")

st.title("NZ Business Acquisition Analyzer")
st.caption("Screening businesses-for-sale against a passive-ownership acquisition lens.")

with st.expander("Paste a new listing", expanded=False):
    raw_text = st.text_area(
        "Paste the full listing text (broker email, saved-search alert copy, etc.)", height=200
    )
    col1, col2 = st.columns(2)
    source = col1.text_input("Source", value="manual")
    url = col2.text_input("URL (optional)", value="")
    if st.button("Parse & score", type="primary"):
        if raw_text.strip():
            listing = parse_listing(raw_text, source=source, url=url)
            st.session_state.listings.append(listing)
            st.success(f"Added: {listing.name}")
        else:
            st.warning("Paste some listing text first.")

results = rank(st.session_state.listings)

for result in results:
    maybe_alert(result)
    if db.is_configured():
        db.save_result(result)

rows = []
for i, r in enumerate(results, start=1):
    l = r.listing
    is_bargain = bool(l.multiple and l.multiple <= r.band.low * bargain_factor)
    rows.append({
        "Rank": i,
        "Verdict": r.verdict,
        "Score": r.composite,
        "Name": l.name,
        "Sector": r.band.label,
        "Asking": l.asking_price,
        "Reported": l.earnings_value,
        "Basis": l.earnings_basis,
        "Passive EBITDA": l.passive_ebitda,
        "Multiple": round(l.multiple, 2) if l.multiple else None,
        "NZ Band (low/typ/high)": f"{r.band.low}x / {r.band.typ}x / {r.band.high}x ({r.band.basis})",
        "Bargain?": "★" if is_bargain else "",
        "# Flags": len(r.red_flags),
    })

df = pd.DataFrame(rows)

st.subheader("Ranked shortlist")
if df.empty:
    st.info("No listings yet — paste one above.")
else:
    styled = df.style.background_gradient(subset=["Score"], cmap="RdYlGn", vmin=0, vmax=100)
    st.dataframe(styled, use_container_width=True, hide_index=True)

st.subheader("Drill down")
if results:
    names = [f"{i + 1}. {r.listing.name}" for i, r in enumerate(results)]
    choice = st.selectbox("Choose a listing", names)
    idx = names.index(choice)
    r = results[idx]
    l = r.listing

    col1, col2 = st.columns([2, 1])
    with col1:
        pillar_df = pd.DataFrame({
            "Pillar": list(r.pillars.keys()),
            "Score": list(r.pillars.values()),
        }).set_index("Pillar")
        st.bar_chart(pillar_df)
    with col2:
        st.metric("Composite", r.composite)
        st.metric("Verdict", r.verdict)
        st.metric(
            "Passive EBITDA",
            f"${l.passive_ebitda:,.0f}" if l.passive_ebitda is not None else "—",
        )

    st.markdown(
        f"**Sector band:** {r.band.label} — {r.band.low}x / {r.band.typ}x / {r.band.high}x "
        f"({r.band.basis}, confidence: {r.band.confidence})"
    )

    if r.red_flags:
        st.markdown("**Red flags:**")
        for flag in r.red_flags:
            st.warning(flag)
    else:
        st.success("No red flags raised.")

    with st.expander("Raw listing text"):
        st.text(l.raw_text or "(no raw text captured)")

st.divider()
st.caption(
    "⚠️ All financials are seller-provided and unverified. This is a triage tool, not investment "
    "advice — confirm every figure with the vendor's accountant before signing any LOI."
)
