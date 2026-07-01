"""Turn raw listing text (pasted, forwarded, or from an email alert) into a
structured Listing.

Primary path: the Anthropic API, prompted to return only JSON matching the
Listing fields. Falls back to regex/keyword extraction so the tool still
works offline or without an API key - the fallback will be far less
accurate and should be treated as a rough first pass, not a substitute for
reading the listing yourself.
"""

import json
import os
import re
from dataclasses import fields

import config
from models import Listing

_FIELD_NAMES = {f.name for f in fields(Listing)}

_PARSE_PROMPT = """You are extracting structured data from a business-for-sale listing.
Return ONLY a JSON object (no prose, no markdown fences) with these fields:

name (string), sector (string), region (string), asking_price (number or null),
revenue (number or null), earnings_value (number or null),
earnings_basis (one of "EBITDA", "SDE", "net_profit", "unknown"),
owner_involvement (one of "absentee", "part_time", "full_time", "unknown"),
manager_in_place (boolean), staff_count (integer or null),
years_established (integer or null), reason_for_sale (string),
vendor_finance_offered (boolean), days_on_market (integer or null),
customer_concentration_pct (number or null), recurring_revenue (boolean),
contracts_in_place (boolean), notes (string, anything noteworthy that
doesn't fit elsewhere).

If a field isn't mentioned in the text, use null/false/"unknown" as
appropriate - do not guess numbers that aren't stated.

Listing text:
---
{raw_text}
---
"""


def parse_listing(raw_text: str, source: str = "pasted") -> Listing:
    """Parse raw listing text into a Listing, preferring the Anthropic API."""
    data = _parse_with_llm(raw_text)
    if data is None:
        data = _parse_with_fallback(raw_text)

    data = {k: v for k, v in data.items() if k in _FIELD_NAMES}
    listing = Listing(name=data.pop("name", "Unnamed listing"), source=source, raw_text=raw_text, **data)
    return listing


def _parse_with_llm(raw_text: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": _PARSE_PROMPT.format(raw_text=raw_text)}],
        )
        text = response.content[0].text.strip()
        text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(text)
    except Exception:
        # Any API/network/parsing failure falls back to the offline parser
        # rather than blocking ingestion.
        return None


_MONEY_RE = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*(k|m)?", re.IGNORECASE)


def _to_number(match) -> float:
    value = float(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").lower()
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return value


def _find_money(text: str, labels) -> float:
    for label in labels:
        pattern = re.compile(label + r"[^$\n]{0,20}(\$\s?[\d,]+(?:\.\d+)?\s*[km]?)", re.IGNORECASE)
        m = pattern.search(text)
        if m:
            money_match = _MONEY_RE.search(m.group(1))
            if money_match:
                return _to_number(money_match)
    return None


def _parse_with_fallback(raw_text: str) -> dict:
    """Best-effort regex/keyword extraction - no network required."""
    text = raw_text or ""
    lowered = text.lower()

    data = {
        "name": text.strip().splitlines()[0][:80] if text.strip() else "Unnamed listing",
        "asking_price": _find_money(text, [r"asking", r"price"]),
        "revenue": _find_money(text, [r"revenue", r"turnover", r"sales"]),
        "earnings_value": _find_money(text, [r"ebitda", r"sde", r"net profit", r"owner'?s? benefit"]),
        "earnings_basis": "unknown",
        "owner_involvement": "unknown",
        "manager_in_place": "manager in place" in lowered or "fully staffed" in lowered,
        "vendor_finance_offered": "vendor finance" in lowered,
        "recurring_revenue": "recurring revenue" in lowered or "subscription" in lowered,
        "contracts_in_place": "contract in place" in lowered or "contracts in place" in lowered or "long-term contract" in lowered,
        "reason_for_sale": "",
        "notes": "Parsed with offline fallback - verify all fields against the original listing.",
    }

    if "ebitda" in lowered:
        data["earnings_basis"] = "EBITDA"
    elif "sde" in lowered or "owner's benefit" in lowered or "owners benefit" in lowered:
        data["earnings_basis"] = "SDE"

    if "absentee" in lowered:
        data["owner_involvement"] = "absentee"
    elif "part-time owner" in lowered or "part time owner" in lowered:
        data["owner_involvement"] = "part_time"
    elif "owner-operator" in lowered or "owner operator" in lowered or "hands-on" in lowered:
        data["owner_involvement"] = "full_time"

    for term in ["retire", "ill health", "relocate", "must sell", "succession", "estate", "divorce"]:
        if term in lowered:
            data["reason_for_sale"] = term
            break

    return data
