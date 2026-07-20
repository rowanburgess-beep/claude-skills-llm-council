# NZ Business Acquisition Analyzer

Screens NZ businesses-for-sale against a Ken Mack–style acquisition lens:
a **truly passive** business (manager in place, buyer doesn't work in it)
throwing off **NZD 200k–300k of manager-adjusted EBITDA**, bought at a
sensible multiple for its sector. See `BLUEPRINT.md` for how each pillar of
the scoring model maps back to that philosophy.

## The one calculation that matters

NZ main-street listings quote profit as **SDE / EBPITD** (the owner's wage
added back in). That overstates profit for a buyer who won't work in the
business. `scoring.manager_adjusted_ebitda()` strips a replacement manager's
cost back out:

- If a manager is already in place: no deduction.
- If earnings are reported as SDE: deduct the full replacement-manager cost
  (`config.REPLACEMENT_MANAGER_COST`, default NZD 110,000).
- Otherwise (EBITDA / net profit / unknown basis, no manager): deduct a
  fraction of that cost, scaled by how involved the current owner already is.

Everything downstream — the profit-quality pillar, the valuation multiple,
the hard caps — is scored off this **passive EBITDA**, not the raw number in
the listing.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Optional environment variables (copy `.env.example` to `.env`):

| Variable | Enables |
|---|---|
| `ANTHROPIC_API_KEY` | LLM-assisted listing parsing (falls back to offline regex parsing without it) |
| `DATABASE_URL` | Postgres persistence of scored listings |
| `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL` / `TELEGRAM_BOT_TOKEN`+`TELEGRAM_CHAT_ID` | Alerts when a listing scores ≥ `ALERT_COMPOSITE_MIN` |

None of these are required — every integration is a safe no-op when unconfigured.

## Running it

```bash
python demo.py          # scores & ranks the 5 sample listings, prints a shortlist
streamlit run app.py     # interactive dashboard
```

## Daily use

1. Forward broker emails / paste saved-search alerts / paste listing copy
   into the "Paste a new listing" box in the dashboard.
2. Each pasted listing is parsed (LLM if `ANTHROPIC_API_KEY` is set,
   otherwise offline regex), scored across five pillars, and added to the
   ranked shortlist for the session.
3. Anything scoring ≥ 70 (`config.VERDICT_SWING`) fires an alert if you've
   configured a webhook.
4. Drill into a listing to see its pillar breakdown, its NZ sector valuation
   band, and any red flags before deciding whether it's worth a call to the
   broker.
5. If `DATABASE_URL` is set, every scored listing is persisted so you can
   track opportunities over time (`opportunities_tracked` table).

## Ingestion — no scraping, ever

This tool **never scrapes a NZ business-for-sale listing site.** That's a
hard compliance rule, not a preference — nowhere in this codebase is there,
or should there ever be, code that fetches listing pages from TradeMe
Business, ABC Business Sales, LINK, Bayleys, or similar. Ingestion is
strictly: paste listing text into the dashboard, forward a broker email, or
paste a saved-search email alert. `parser.py` only ever operates on text you
provide it.

## Honesty caveats

- **All financials are seller-provided and unverified.** The scoring model
  triages candidates for further investigation — it is not due diligence
  and not investment advice. Verify every figure (with the vendor's
  accountant, IRD statements, bank records) before signing any LOI.
- **The NZ sector valuation bands in `nz_benchmarks.py` are calibrated
  estimates**, not sourced from a paid multiples database — every row is
  marked `confidence="estimate"`. Granular NZ sale-multiple data is mostly
  behind broker paywalls. Emailing ABC Business Sales for their multiples
  database, or pulling a Bizval SME report, for the sectors that matter most
  to you (trade services, civil construction, water infrastructure) would
  make these bands authoritative rather than estimated.
- **Scoring caps, weights, and thresholds are all editable** in `config.py`
  and, for the replacement manager cost, live-adjustable from the dashboard
  sidebar. They encode one particular set of judgment calls about what
  "truly passive" and "sensible multiple" mean — recalibrate them to your
  own risk tolerance.
- **Alerts and Postgres persistence are both optional** and fail silently if
  unconfigured; they will never crash the scoring pipeline.

## Files

| File | Purpose |
|---|---|
| `config.py` | All calibration constants (editable) |
| `models.py` | `Listing` dataclass |
| `nz_benchmarks.py` | Sector valuation bands, `match_sector()`, `get_benchmark()` |
| `scoring.py` | The five-pillar scoring engine, hard caps, `score_listing()`, `rank()` |
| `parser.py` | LLM + offline-fallback listing parsing |
| `alerts.py` | Slack / Discord / Telegram webhook alerts |
| `sample_listings.py` | 5 invented calibration listings |
| `demo.py` | CLI: score & rank the samples |
| `app.py` | Streamlit dashboard |
| `db.py` / `schema.sql` | Optional Postgres persistence |
| `BLUEPRINT.md` | How each Ken Mack principle maps to the code |
