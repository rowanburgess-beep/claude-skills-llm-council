# BLUEPRINT

How the Ken Mack passive-acquisition methodology maps to this codebase.

## 1. "Don't buy a job" → `owner_independence` pillar

Ken Mack's central filter: if the business can't run without the owner, you
haven't bought an asset, you've bought yourself a job. `scoring.py:
score_owner_independence()` scores this directly from `owner_involvement`
and `manager_in_place`, with language detection (`owner-operator`,
`hands-on`, `key person` vs. `manager in place`, `fully staffed`) as a
secondary signal from the listing text. A full-time owner with no manager is
also a **hard cap**: composite is capped at 45 regardless of how well the
other four pillars score (`scoring.py: score_listing()`).

## 2. Manager-adjusted (passive) EBITDA → the core calculation

Everything downstream depends on `scoring.py: manager_adjusted_ebitda()`.
NZ main-street listings quote SDE (owner's wage added back), which is not
what a passive buyer actually gets to keep. The function strips a
replacement manager's cost (`config.REPLACEMENT_MANAGER_COST`, editable, and
tunable live from the Streamlit sidebar) out of reported earnings, scaled by
how involved the current owner is — unless a manager is already in place, in
which case no deduction is needed.

## 3. Profit quality, not just profit size → `profit_quality` pillar

A business barely above the EBITDA floor scores worse than one comfortably
inside the target band, and thin margins get penalized even on high revenue
(see the Thin-Margin Online Retailer sample: $3M revenue but a 32/100
profit-quality score). `score_profit_quality()` blends a band score (where
passive EBITDA sits relative to `EBITDA_FLOOR`/`TARGET_EBITDA_MIN`) with a
margin score.

## 4. Pay a sensible multiple → `valuation` pillar

Ken Mack's guidance is sector-relative: a multiple that's cheap for a cafe
is expensive for trade services. `nz_benchmarks.py` holds per-sector
(basis, low, typ, high) bands; `score_valuation()` scores the listing's
actual asking/earnings multiple against its sector's band on a piecewise
linear scale (100 at/below `low`, down to 10 at `high * 1.3`).

## 5. Motivated sellers make better deals → `deal_structure` pillar

Retirement, ill health, relocation, and similar language signal a seller
who wants a fast, clean exit — often on better terms (vendor finance, lower
price, more flexibility). `score_deal_structure()` rewards these signals
plus vendor finance and listings that have sat unsold for a while (both
correlate with more room to negotiate).

## 6. Resilience over hustle → `resilience_fit` pillar

Recurring revenue and contracts in place mean the business doesn't depend on
constant new-customer hunting; customer concentration is a risk multiplier
in the other direction. `score_resilience_fit()` also adds a bonus for
PipeTech-adjacent sectors (drainage, civil, water infrastructure, etc.) —
this is the one deliberately personal weighting, reflecting familiarity with
that space as a buyer.

## 7. Composite, verdict, and red flags

`score_listing()` combines the five pillars via `config.WEIGHTS` (owner
independence weighted highest — Ken Mack's "don't buy a job" is the
non-negotiable filter), applies the hard caps, and buckets the result into
SWING / WATCHLIST / PASS (`config.VERDICT_SWING` / `VERDICT_WATCH`).
`detect_red_flags()` runs independently of scoring — flags exist to surface
things a composite score can hide (e.g. a decent score with unverifiable
earnings basis still gets flagged).

## 8. Compliance boundary

No scraper exists or should be built against nzbizbuysell,
businessesforsale.com, ABC Business, Tabak, or Barker Business — their T&Cs
prohibit it. `parser.py` only ever processes text you provide (pasted,
forwarded email, or a saved-search alert you already receive) — it has no
network-fetch path to a listing site.
