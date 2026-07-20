# BLUEPRINT: Ken Mack principles → code

This document maps the acquisition philosophy behind this tool to the
specific code that implements it, so the scoring logic doesn't read as an
arbitrary pile of weights.

## 1. "Don't buy a job"

The single biggest failure mode in main-street acquisition is buying a
business that's actually just a self-employment arrangement wearing a P&L.
Two mechanisms enforce this:

- **`scoring.score_owner_independence()`** — the owner_independence pillar
  (30% weight, the largest of the five) rewards absentee/managed businesses
  and punishes full-time owner-operator language directly in the listing
  text ("owner-operator", "hands-on", "key person").
- **Hard cap in `scoring.score_listing()`** — if the owner is full-time and
  no manager is in place, the composite score is capped at 45 *regardless*
  of how good the other four pillars look. A cheap multiple or a motivated
  seller cannot rescue a business that is fundamentally a job. See the
  "Long-Established Mechanical Workshop" sample: a cheap 2.4x multiple, a
  highly motivated seller, and vendor finance still can't clear PASS because
  the underlying economics — once a manager's cost is priced in — don't
  support genuine passive ownership.

## 2. Profit has to be measured the way a passive owner will actually receive it

NZ main-street brokers quote **SDE** — profit with the owner's wage added
back in, because most buyers are buying themselves a job and the owner's
wage is *their* wage. A passive buyer never receives that wage; it goes to
a manager instead. `scoring.manager_adjusted_ebitda()` is the load-bearing
calculation in this codebase: every other pillar and the final verdict are
computed off **passive EBITDA**, never off the raw reported number.

- `owner_independence`: rewards the *structure* that makes passive ownership
  possible (manager already in place).
- `profit_quality`: rewards passive EBITDA landing in the NZD 200k–300k
  target band, and margin quality — because thin margins evaporate the
  moment costs move against you, even before subtracting a manager's wage.
  See the "High-Growth Online Homeware Retailer" sample: NZD 3m revenue
  looks impressive, but a 6% margin means the passive-adjusted EBITDA is
  a rounding error, and the pillar score reflects that even though the
  multiple looks cheap.

## 3. Price the deal on the sector's own terms

A 3x multiple is cheap for a cafe and expensive for a software business.
`nz_benchmarks.py` encodes per-sector bands (low/typical/high) on each
sector's own typical quoting basis (SDE for main-street trades and
hospitality, EBITDA for civil, water, manufacturing, tech). `score_valuation()`
explicitly flags — rather than silently blends — a mismatch between the
listing's reported basis and the sector's typical basis, because an EBITDA
multiple and an SDE multiple for the same business are not the same number
and mixing them makes a business look artificially cheap or expensive.

## 4. Structure the deal, don't just price it

Ken Mack's approach leans on structure — vendor finance, motivated sellers,
earn-outs — to make deals work with limited money down. `score_deal_structure()`
rewards exactly the signals that make that possible: a motivated seller
(retirement, ill health, relocation, succession, estate, divorce), vendor
finance already on the table, a listing that's sat on the market long enough
that the vendor is more flexible, and an established trading history that
de-risks the earn-out period.

## 5. Fit the target's resilience and PipeTech's own operating lens

`score_resilience_fit()` rewards recurring/contracted revenue and low
customer concentration — generic resilience signals — and then adds a
deliberate PipeTech-specific bonus for businesses in drainage, civil,
water/wastewater/stormwater, trenchless, contracting, plumbing, and
adjacent infrastructure work, since those are sectors where operating
experience compounds an acquisition's odds of success beyond what the
financial pillars alone can see.

## Composite score and verdict

```
composite = Σ (pillar_score × weight)   for the five pillars in config.WEIGHTS
```

Hard caps are applied *after* the weighted composite, so no combination of
good scores elsewhere can outrun the two deal-killers for a passive buyer:
a full-time owner with no manager, or a manager-adjusted EBITDA that's
already zero or negative once a manager is costed in.

- `composite ≥ config.VERDICT_SWING` (70) → **SWING**
- `composite ≥ config.VERDICT_WATCH` (50) → **WATCHLIST**
- otherwise → **PASS**
