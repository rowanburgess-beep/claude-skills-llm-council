"""Streamlit dashboard for the NZ Business Acquisition Analyzer.

Run with: streamlit run app.py

State lives in st.session_state for the life of the server process only -
this app intentionally does not use browser localStorage, so listings are
lost on a full page reload. Use the optional Postgres persistence (db.py)
if you need listings to survive restarts.
"""

import pandas as pd
import streamlit as st

import config
from alerts import maybe_alert
from parser import parse_listing
from sample_listings import SAMPLE_LISTINGS
from scoring import rank

st.set_page_config(page_title="NZ Business Acquisition Analyzer", layout="wide")

if "listings" not in st.session_state:
    st.session_state.listings = list(SAMPLE_LISTINGS)
if "manager_cost" not in st.session_state:
    st.session_state.manager_cost = config.REPLACEMENT_MANAGER_COST

st.title("NZ Business Acquisition Analyzer")
st.caption("Screening business-for-sale listings against a passive-buyer, Ken Mack-style lens.")

# --- Sidebar: calibration dials ---------------------------------------------
with st.sidebar:
    st.header("Calibration")
    st.session_state.manager_cost = st.number_input(
        "Replacement manager cost (NZD/yr)",
        min_value=0,
        max_value=500_000,
        value=int(st.session_state.manager_cost),
        step=5_000,
        help="Annual cost of hiring a manager to replace the owner. Used to strip "
             "owner's-wage-inflated SDE/EBPITD down to a true passive EBITDA.",
    )
    config.REPLACEMENT_MANAGER_COST = st.session_state.manager_cost

    st.divider()
    st.caption(f"Target EBITDA band: ${config.TARGET_EBITDA_MIN:,} - ${config.TARGET_EBITDA_MAX:,}")
    st.caption(f"EBITDA floor: ${config.EBITDA_FLOOR:,}")
    st.caption(f"Verdict thresholds: SWING >= {config.VERDICT_SWING}, WATCHLIST >= {config.VERDICT_WATCH}")

    st.divider()
    if st.button("Reset to sample listings"):
        st.session_state.listings = list(SAMPLE_LISTINGS)
        st.rerun()

# --- Paste-a-listing box -----------------------------------------------------
st.subheader("Add a listing")
with st.form("paste_listing_form", clear_on_submit=True):
    raw_text = st.text_area(
        "Paste raw listing text (from a broker site, forwarded email, or saved-search alert)",
        height=150,
    )
    submitted = st.form_submit_button("Parse & score")

if submitted and raw_text.strip():
    with st.spinner("Parsing listing..."):
        listing = parse_listing(raw_text, source="pasted")
    st.session_state.listings.append(listing)
    st.success(f"Added: {listing.name}")

# --- Ranked table -------------------------------------------------------------
st.subheader("Ranked shortlist")

results = rank(st.session_state.listings)

for result in results:
    maybe_alert(result)

table_rows = []
for i, result in enumerate(results, start=1):
    listing = result["listing"]
    low, typ, high = result["sector_band"]
    table_rows.append({
        "Rank": i,
        "Verdict": result["verdict"],
        "Score": result["composite"],
        "Name": listing.name,
        "Sector": result["sector"],
        "Asking": listing.asking_price,
        "Reported": listing.earnings_value,
        "Basis": listing.earnings_basis,
        "Passive EBITDA": result["passive_ebitda"],
        "Multiple": listing.multiple,
        "NZ Band (low/typ/high)": f"{low:.2f}/{typ:.2f}/{high:.2f} ({result['sector_basis']})",
        "# Flags": len(result["red_flags"]),
    })

df = pd.DataFrame(table_rows)

styled = df.style.background_gradient(subset=["Score"], cmap="RdYlGn", vmin=0, vmax=100)
st.dataframe(styled, use_container_width=True, hide_index=True)

# --- Drill-down ---------------------------------------------------------------
st.subheader("Drill-down")

names = [r["listing"].name for r in results]
selected_name = st.selectbox("Select a listing", names) if names else None

if selected_name:
    result = next(r for r in results if r["listing"].name == selected_name)
    listing = result["listing"]
    low, typ, high = result["sector_band"]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### {listing.name} — **{result['verdict']}** ({result['composite']}/100)")
        pillar_df = pd.DataFrame(
            {"Pillar": list(result["pillars"].keys()), "Score": list(result["pillars"].values())}
        ).set_index("Pillar")
        st.bar_chart(pillar_df)

    with col2:
        st.metric("Passive EBITDA", f"${result['passive_ebitda']:,.0f}")
        st.metric("Asking price", f"${listing.asking_price:,.0f}" if listing.asking_price else "n/a")
        if listing.multiple:
            st.metric("Multiple", f"{listing.multiple:.2f}x")
        fallback_note = " (fallback estimate — replace with real comps)" if result["sector_band_is_fallback"] else ""
        st.caption(f"Sector band ({result['sector_basis']}): {low:.2f} / {typ:.2f} / {high:.2f}{fallback_note}")

    st.markdown("**Red flags**")
    if result["red_flags"]:
        for flag in result["red_flags"]:
            st.warning(flag)
    else:
        st.success("No red flags detected.")

    with st.expander("Raw listing text"):
        st.text(listing.raw_text or "(no raw text captured)")

st.divider()
st.caption(
    "All financials are seller-provided and unverified. This tool is a screening aid, "
    "not due diligence — verify every figure independently before signing an LOI."
)
