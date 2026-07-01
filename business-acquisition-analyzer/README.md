# NZ Business Acquisition Analyzer

Screens NZ businesses-for-sale against a Ken Mack-style acquisition lens for a
**truly passive buyer**: manager already in place, owner not working in the
business, throwing off NZD 200k-300k of manager-adjusted EBITDA at a sensible
multiple for its sector.

## The core idea

NZ main-street listings quote profit as SDE / EBPITD — the owner's own wage is
added back in. That overstates profit for a buyer who won't work in the
business. This tool strips a replacement manager's salary back out before
scoring anything, so a business that only looks profitable because the current
owner works for free gets scored honestly.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Everything beyond pandas/Streamlit is optional:

- `ANTHROPIC_API_KEY` — enables LLM-assisted parsing of pasted listings
  (`ANTHROPIC_MODEL` env var to override the model). Without it, `parser.py`
  falls back to regex/keyword extraction, which is far rougher — treat it as
  a first pass, not a substitute for reading the listing.
- `DATABASE_URL` — enables Postgres persistence via `db.py` / `schema.sql`.
  Without it, listings only live for the Streamlit session.
- `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL` / `TELEGRAM_BOT_TOKEN` +
  `TELEGRAM_CHAT_ID` — enables alerts when a listing's composite score clears
  `ALERT_COMPOSITE_MIN` (config.py). None configured = no alerts, no crash.

## Running it

```bash
python demo.py           # score + rank the 5 sample listings, print a shortlist
streamlit run app.py      # interactive dashboard
```

## How to use it day to day

1. Save a search on the broker sites you follow and forward listing emails
   (or paste listing text directly) into the dashboard's "Add a listing" box.
2. The analyzer computes manager-adjusted EBITDA, scores the five pillars,
   and slots the listing into SWING / WATCHLIST / PASS.
3. Drill into any listing to see its pillar breakdown, red flags, and how its
   asking multiple compares to the NZ sector band.
4. SWING-tier listings above `ALERT_COMPOSITE_MIN` fire your configured
   webhook so you don't have to keep the dashboard open.

## Honesty caveats — read before you rely on this

- **All financials are seller-provided and unverified.** The tool has no way
  to confirm asking price, revenue, or earnings are accurate. Verify
  everything independently before an LOI.
- **NZ sector valuation bands (`nz_benchmarks.py`) are calibrated estimates**,
  not real transaction data. Replace them with real ABC Business Sales /
  Bizval comps per sector as you get access to them — every valuation score
  is only as good as that table.
- **The offline parser fallback is rough.** It's regex/keyword matching, not
  comprehension. Always double-check a parsed listing's fields against the
  original text, especially dollar figures.
- **No scraper was built, and none should be.** nzbizbuysell,
  businessesforsale.com, ABC Business, Tabak, and Barker Business all
  prohibit scraping in their T&Cs. Listings only enter this tool via paste,
  forwarded email, or saved-search alerts you already receive.
- **This is a screening filter, not due diligence.** A SWING verdict means
  "worth a serious look," not "worth an offer."

See `BLUEPRINT.md` for how each part of the Ken Mack methodology maps to the
code.
