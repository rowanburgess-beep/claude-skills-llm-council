"""NZ sector valuation starter bands.

Granular NZ sale-multiple data is mostly behind broker paywalls (ABC Business
Sales' multiples database, Bizval SME reports). These bands are calibrated
estimates for triage only — every row is marked confidence="estimate".
Emailing ABC Business Sales or pulling a Bizval report for the sectors that
matter most (trade_services, civil_construction, water_infrastructure) would
make this authoritative. See README.md.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SectorBand:
    sector_key: str
    label: str
    basis: str  # "SDE" or "EBITDA" — the basis this sector is typically quoted on
    low: float
    typ: float
    high: float
    keywords: Tuple[str, ...]
    confidence: str = "estimate"


SECTOR_BANDS: Tuple[SectorBand, ...] = (
    SectorBand("hospitality_cafe", "Hospitality / Cafe", "SDE", 1.5, 2.25, 3.0,
               ("cafe", "restaurant", "takeaway", "bar", "eatery", "diner")),
    SectorBand("retail", "Retail", "SDE", 2.0, 2.75, 3.5,
               ("retail", "store", "shop", "liquor")),
    SectorBand("trade_services", "Trade Services", "SDE", 2.5, 3.25, 4.0,
               ("plumbing", "electrical", "hvac", "automotive", "mechanic", "workshop")),
    SectorBand("civil_construction", "Civil Construction", "EBITDA", 2.5, 3.25, 4.5,
               ("civil", "contracting", "earthworks", "drainage")),
    SectorBand("water_infrastructure", "Water Infrastructure", "EBITDA", 3.0, 4.0, 5.5,
               ("water", "pipeline", "trenchless", "wastewater")),
    SectorBand("manufacturing", "Manufacturing", "EBITDA", 3.0, 4.0, 5.5,
               ("manufacturing", "fabrication", "engineering")),
    SectorBand("wholesale_distribution", "Wholesale / Distribution", "EBITDA", 3.0, 3.75, 4.75,
               ("wholesale", "distribution", "import")),
    SectorBand("transport_logistics", "Transport / Logistics", "EBITDA", 3.0, 3.75, 5.0,
               ("transport", "freight", "logistics", "courier")),
    SectorBand("professional_services", "Professional Services", "SDE", 2.5, 3.5, 4.5,
               ("consulting", "agency", "accounting")),
    SectorBand("healthcare_medical", "Healthcare / Medical", "EBITDA", 4.0, 5.5, 7.0,
               ("medical", "dental", "clinic", "pharmacy")),
    SectorBand("childcare_education", "Childcare / Education", "EBITDA", 4.0, 5.5, 7.0,
               ("childcare", "early learning", "education")),
    SectorBand("waste_industrial", "Waste / Industrial", "EBITDA", 3.5, 4.5, 6.0,
               ("waste", "recycling", "environmental")),
    SectorBand("technology_software", "Technology / Software", "EBITDA", 4.0, 6.0, 9.0,
               ("software", "saas", "technology")),
    SectorBand("franchise", "Franchise", "SDE", 2.0, 2.75, 3.5,
               ("franchise",)),
    SectorBand("ecommerce_online", "Ecommerce / Online", "SDE", 2.0, 3.0, 4.0,
               ("ecommerce", "online store", "dropship")),
)

GENERAL_SME = SectorBand(
    "general_sme", "General SME (fallback)", "SDE", 2.0, 2.75, 3.5, tuple(), confidence="estimate"
)


def match_sector(sector_label: str, raw_text: str = "") -> SectorBand:
    """Score a listing's sector label + raw text against each band's keywords.

    Falls back to GENERAL_SME if nothing matches. Ties go to whichever band is
    listed first in SECTOR_BANDS, so word choice in a listing's sector/raw text
    matters when a term (e.g. "water") could plausibly belong to more than one
    band — prefer the most specific phrasing available.
    """
    haystack = f"{sector_label} {raw_text}".lower()
    best = None
    best_hits = 0
    for band in SECTOR_BANDS:
        hits = sum(1 for kw in band.keywords if kw in haystack)
        if hits > best_hits:
            best_hits = hits
            best = band
    return best if best else GENERAL_SME


def get_benchmark(sector_key: str) -> SectorBand:
    for band in SECTOR_BANDS:
        if band.sector_key == sector_key:
            return band
    return GENERAL_SME
