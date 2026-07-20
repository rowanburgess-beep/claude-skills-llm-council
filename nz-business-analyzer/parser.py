"""Turn raw listing text into a structured Listing.

Ingestion is deliberately manual: paste listing text into the dashboard,
forward a broker email, or paste a saved-search alert. This module never
fetches anything from a listing site — see README.md for why scraping is a
hard "no" here, not a style preference.

Primary path: the Anthropic API, prompted to return ONLY JSON for the
Listing fields. Falls back to regex/keyword extraction so the whole pipeline
still runs with no ANTHROPIC_API_KEY at all.
"""
import json
import os
import re
from typing import Optional

from models import Listing

_LLM_FIELDS = [
    "name", "sector", "region", "asking_price", "revenue", "earnings_value",
    "earnings_basis", "owner_involvement", "manager_in_place", "staff_count",
    "years_established", "reason_for_sale", "vendor_finance_offered",
    "days_on_market", "customer_concentration_pct", "recurring_revenue",
    "contracts_in_place", "notes",
]

_FIELDS_DOC = """
name (string), sector (string), region (string),
asking_price (number|null), revenue (number|null), earnings_value (number|null),
earnings_basis (string), owner_involvement (string), manager_in_place (boolean),
staff_count (number|null), years_established (number|null), reason_for_sale (string),
vendor_finance_offered (boolean), days_on_market (number|null),
customer_concentration_pct (number|null), recurring_revenue (boolean),
contracts_in_place (boolean), notes (string)
""".strip()

_PROMPT_TEMPLATE = """You extract structured data from NZ business-for-sale listings.
Read the listing text below and return ONLY a single JSON object (no prose, no markdown
fences) with exactly these keys:

{fields_doc}

Rules:
- earnings_basis must be one of: "EBITDA", "SDE", "net_profit", "unknown"
- owner_involvement must be one of: "absentee", "part_time", "full_time", "unknown"
- Use null for any value that isn't stated in the text. Do not guess numbers.
- asking_price, revenue, earnings_value are plain numbers in NZD (no currency symbols, no commas).
- manager_in_place, vendor_finance_offered, recurring_revenue, contracts_in_place are booleans.

Listing text:
---
{raw_text}
---
"""


def parse_listing(raw_text: str, source: str = "manual", url: str = "") -> Listing:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            return _parse_with_llm(raw_text, api_key, source, url)
        except Exception:
            pass  # any API/parse failure falls through to offline extraction
    return _parse_with_fallback(raw_text, source, url)


def _parse_with_llm(raw_text: str, api_key: str, source: str, url: str) -> Listing:
    import anthropic  # imported lazily so the package is only required if a key is set

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _PROMPT_TEMPLATE.format(fields_doc=_FIELDS_DOC, raw_text=raw_text)
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    data = json.loads(text)

    kwargs = {k: data.get(k) for k in _LLM_FIELDS if data.get(k) is not None}
    kwargs.setdefault("earnings_basis", "unknown")
    kwargs.setdefault("owner_involvement", "unknown")
    kwargs.setdefault("manager_in_place", False)
    kwargs.setdefault("vendor_finance_offered", False)
    kwargs.setdefault("recurring_revenue", False)
    kwargs.setdefault("contracts_in_place", False)
    kwargs.setdefault("name", "Unnamed listing")

    return Listing(source=source, url=url, raw_text=raw_text, **kwargs)


_MONEY_RE = re.compile(r"\$?\s?([\d][\d,]*(?:\.\d+)?)\s?(k|m)?", re.IGNORECASE)


def _extract_money_near(text: str, keywords) -> Optional[float]:
    lowered = text.lower()
    for kw in keywords:
        idx = lowered.find(kw)
        if idx == -1:
            continue
        window = text[idx + len(kw): idx + len(kw) + 100]
        match = _MONEY_RE.search(window)
        if match:
            value = float(match.group(1).replace(",", ""))
            suffix = (match.group(2) or "").lower()
            if suffix == "k":
                value *= 1_000
            elif suffix == "m":
                value *= 1_000_000
            return value
    return None


def _parse_with_fallback(raw_text: str, source: str, url: str) -> Listing:
    lowered = raw_text.lower()

    asking_price = _extract_money_near(raw_text, ["asking price", "asking:", "price:", "asking"])
    revenue = _extract_money_near(raw_text, ["revenue", "turnover", "sales"])
    earnings_value = _extract_money_near(raw_text, ["ebitda", "sde", "net profit", "earnings"])

    if "ebitda" in lowered:
        earnings_basis = "EBITDA"
    elif "sde" in lowered or "owner's benefit" in lowered or "seller's discretionary" in lowered:
        earnings_basis = "SDE"
    elif "net profit" in lowered:
        earnings_basis = "net_profit"
    else:
        earnings_basis = "unknown"

    if "absentee" in lowered:
        owner_involvement = "absentee"
    elif any(p in lowered for p in ("semi-passive", "semi passive", "part-time", "part time")):
        owner_involvement = "part_time"
    elif any(p in lowered for p in ("owner-operator", "owner operator", "hands-on", "hands on",
                                     "full-time owner", "full time owner")):
        owner_involvement = "full_time"
    else:
        owner_involvement = "unknown"

    manager_in_place = any(p in lowered for p in
                            ("manager in place", "fully staffed", "experienced manager",
                             "management team in place"))
    vendor_finance_offered = "vendor finance" in lowered or "vendor terms" in lowered
    recurring_revenue = any(p in lowered for p in ("recurring revenue", "contracted revenue", "subscription"))
    contracts_in_place = any(p in lowered for p in ("contract in place", "contracts in place", "long-term contract"))

    years_match = re.search(r"(?:established|trading)(?:\s+for)?\s+(\d{1,3})\s+years", lowered)
    years_established = int(years_match.group(1)) if years_match else None

    days_match = re.search(r"(\d{1,4})\s+days\s+on\s+market", lowered)
    days_on_market = int(days_match.group(1)) if days_match else None

    concentration_match = re.search(r"(\d{1,3})\s?%\s+(?:of\s+)?revenue\s+from", lowered)
    customer_concentration_pct = float(concentration_match.group(1)) if concentration_match else None

    reason_match = re.search(r"reason for sale[:\-]?\s*([^\n.]+)", raw_text, re.IGNORECASE)
    reason_for_sale = reason_match.group(1).strip() if reason_match else ""

    name_match = re.match(r"^([^\n]{3,80})", raw_text.strip())
    name = name_match.group(1).strip() if name_match else "Unnamed listing"

    return Listing(
        name=name,
        source=source,
        url=url,
        asking_price=asking_price,
        revenue=revenue,
        earnings_value=earnings_value,
        earnings_basis=earnings_basis,
        owner_involvement=owner_involvement,
        manager_in_place=manager_in_place,
        reason_for_sale=reason_for_sale,
        vendor_finance_offered=vendor_finance_offered,
        days_on_market=days_on_market,
        customer_concentration_pct=customer_concentration_pct,
        recurring_revenue=recurring_revenue,
        contracts_in_place=contracts_in_place,
        years_established=years_established,
        raw_text=raw_text,
        notes="Parsed offline via regex fallback (no ANTHROPIC_API_KEY set) — verify all figures.",
    )
