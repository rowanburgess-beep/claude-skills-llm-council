"""Score and rank the sample listings, printing a readable shortlist."""

from sample_listings import SAMPLE_LISTINGS
from scoring import rank


def _fmt_money(value):
    return f"${value:,.0f}" if value is not None else "n/a"


def main():
    results = rank(SAMPLE_LISTINGS)

    print("=" * 78)
    print("NZ BUSINESS ACQUISITION SHORTLIST")
    print("=" * 78)

    for i, result in enumerate(results, start=1):
        listing = result["listing"]
        low, typ, high = result["sector_band"]
        fallback_note = " (fallback estimate)" if result["sector_band_is_fallback"] else ""

        print(f"\n#{i}  {listing.name}  —  {result['verdict']}  (composite {result['composite']}/100)")
        print(f"    Asking: {_fmt_money(listing.asking_price)}  |  "
              f"Reported {listing.earnings_basis}: {_fmt_money(listing.earnings_value)}  |  "
              f"Passive EBITDA: {_fmt_money(result['passive_ebitda'])}")
        if listing.multiple:
            print(f"    Multiple: {listing.multiple:.2f}x  vs  {result['sector']} band "
                  f"{low:.2f}/{typ:.2f}/{high:.2f} ({result['sector_basis']}){fallback_note}")

        financing = result["financing"]
        if financing["dscr"] is not None:
            print(f"    Financing: DSCR {financing['dscr']:.2f}x, annual debt service "
                  f"{_fmt_money(financing['annual_debt_service'])} — {financing['risk']}")
        else:
            print(f"    Financing: {financing['reason']}")

        pillars = result["pillars"]
        pillar_str = "  ".join(f"{name}={score:.0f}" for name, score in pillars.items())
        print(f"    Pillars: {pillar_str}")

        if result["red_flags"]:
            print("    Red flags:")
            for flag in result["red_flags"]:
                print(f"      - {flag}")
        else:
            print("    Red flags: none")

    print("\n" + "=" * 78)
    print(f"Scored {len(results)} listings. Verdicts must be independently verified "
          f"before any LOI — all financials are seller-provided.")
    print("=" * 78)


if __name__ == "__main__":
    main()
