"""NZ sector valuation bands.

These are calibrated ESTIMATES based on general NZ business-sale convention
(main-street SDE multiples, managed-business EBITDA multiples), NOT verified
transaction data. Replace with real ABC Business Sales / Bizval figures per
sector as soon as you have them — until then, treat every valuation score as
an estimate/fallback.

sector_key: (basis, low, typ, high)
"""

SECTOR_BANDS = {
    "hospitality_cafe":       ("SDE",    1.5, 2.25, 3.0),
    "retail":                 ("SDE",    2.0, 2.75, 3.5),
    "trade_services":         ("SDE",    2.5, 3.25, 4.0),
    "civil_construction":     ("EBITDA", 2.5, 3.25, 4.5),
    "water_infrastructure":   ("EBITDA", 3.0, 4.0,  5.5),
    "manufacturing":          ("EBITDA", 3.0, 4.0,  5.5),
    "wholesale_distribution": ("EBITDA", 3.0, 3.75, 4.75),
    "transport_logistics":    ("EBITDA", 3.0, 3.75, 5.0),
    "professional_services":  ("SDE",    2.5, 3.5,  4.5),
    "healthcare_medical":     ("EBITDA", 4.0, 5.5,  7.0),
    "childcare_education":    ("EBITDA", 4.0, 5.5,  7.0),
    "waste_industrial":       ("EBITDA", 3.5, 4.5,  6.0),
    "technology_software":    ("EBITDA", 4.0, 6.0,  9.0),
    "franchise":              ("SDE",    2.0, 2.75, 3.5),
    "ecommerce_online":       ("SDE",    2.0, 3.0,  4.0),
    "general_sme":            ("SDE",    2.0, 2.75, 3.5),  # fallback
}

FALLBACK_SECTOR = "general_sme"

SECTOR_KEYWORDS = {
    "hospitality_cafe": ["cafe", "coffee shop", "restaurant", "bar", "hospitality", "takeaway", "catering", "eatery"],
    "retail": ["retail", "shop", "store", "boutique"],
    "trade_services": ["trade", "electrician", "builder", "plumber", "handyman", "landscaping", "painter", "roofing"],
    "civil_construction": ["civil", "construction", "earthworks", "roading", "contracting"],
    "water_infrastructure": ["three waters", "wastewater", "stormwater", "pipeline", "trenchless", "drainage", "water infrastructure"],
    "manufacturing": ["manufactur", "fabrication", "factory", "engineering workshop"],
    "wholesale_distribution": ["wholesale", "distribution", "distributor", "importer"],
    "transport_logistics": ["transport", "logistics", "freight", "courier", "haulage"],
    "professional_services": ["accounting firm", "law firm", "consultancy", "professional services", "advisory"],
    "healthcare_medical": ["medical", "healthcare", "clinic", "dental", "physio", "pharmacy"],
    "childcare_education": ["childcare", "early learning", "education", "school", "tutoring", "kindergarten"],
    "waste_industrial": ["waste management", "recycling", "industrial services"],
    "technology_software": ["software", "saas", "technology company", "app development", "it services"],
    "franchise": ["franchise"],
    "ecommerce_online": ["ecommerce", "e-commerce", "online store", "online retailer", "dropship"],
}


def match_sector(text: str) -> str:
    """Match free text (sector field, raw listing text) to a benchmark sector."""
    lowered = (text or "").lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return sector
    return FALLBACK_SECTOR


def get_benchmark(sector: str):
    """Return (basis, low, typ, high, is_fallback) for a sector key."""
    is_fallback = sector not in SECTOR_BANDS
    basis, low, typ, high = SECTOR_BANDS.get(sector, SECTOR_BANDS[FALLBACK_SECTOR])
    return basis, low, typ, high, is_fallback
