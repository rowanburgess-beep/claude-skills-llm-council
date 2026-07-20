"""Score and rank the sample NZ listings — a quick sanity check of the scoring engine.

Run: python demo.py
"""
from sample_listings import get_sample_listings
from scoring import rank


def _fmt_money(value):
    return f"${value:,.0f}" if value is not None else "—"


def main():
    results = rank(get_sample_listings())

    print("=" * 100)
    print("NZ BUSINESS ACQUISITION ANALYZER — SHORTLIST")
    print("=" * 100)

    for i, r in enumerate(results, start=1):
        l = r.listing
        print(f"\n#{i}  [{r.verdict}]  {l.name}  —  composite {r.composite}/100")
        print(
            f"    Sector band:     {r.band.label} ({r.band.basis}, "
            f"{r.band.low}x/{r.band.typ}x/{r.band.high}x, confidence={r.band.confidence})"
        )
        print(f"    Asking:          {_fmt_money(l.asking_price)}")
        print(f"    Reported ({l.earnings_basis}): {_fmt_money(l.earnings_value)}")
        print(f"    Passive EBITDA:  {_fmt_money(l.passive_ebitda)}")
        print(f"    Multiple:        {l.multiple:.2f}x" if l.multiple else "    Multiple:        —")
        print("    Pillars:         " + ", ".join(f"{k}={v}" for k, v in r.pillars.items()))
        if r.red_flags:
            print("    Red flags:")
            for flag in r.red_flags:
                print(f"      - {flag}")
        else:
            print("    Red flags:       none")

    print("\n" + "=" * 100)
    print("Reminder: all financials are seller-provided and unverified. Verify before any LOI.")


if __name__ == "__main__":
    main()
