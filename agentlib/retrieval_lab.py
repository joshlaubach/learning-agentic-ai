"""Shared fixtures for Chapter 3's lexical-retrieval lab.

Why a separate corpus: the chapter's SQuAD passages are close to a best case for lexical
retrieval, because a SQuAD question is written by a human who is looking at the passage and
therefore reuses its vocabulary. BM25 scores an MRR of 0.966 on them, which leaves no room to
show what lexical retrieval is actually for.

The catalog below is built to have the property SQuAD lacks: identifiers. A SKU, a filter
rating, a three-letter trade acronym -- strings that carry no meaning a semantic model could
have learned, and that a user types verbatim expecting an exact hit. That is the case the
"our vector search misses exact product codes" question is really about, and it needs a
corpus where such strings exist.

Two things are deliberate. The identifiers appear IN the indexed text, not only as record
keys: an identifier you cannot search for is a missing field, not a retrieval failure. And
the paraphrase queries share almost no content words with their target document, so a lexical
retriever has to genuinely fail on them rather than coast on overlap.
"""

from __future__ import annotations

import re

# A small parts catalog. Synthetic, and labelled as such -- but the SHAPE is what matters: a
# model number, a trade acronym, and a plain-language description, which is what almost every
# real product corpus looks like.
CATALOG = (
    ("SKU-4417", "ThermaFlow X2. Tankless electric unit that heats water on demand for a whole house. No storage vessel required."),
    ("SKU-9302", "ArcticCore 12K. Portable cooling appliance for a single room. Vents through a window and dehumidifies."),
    ("SKU-1188", "HelioPanel 400W. Monocrystalline photovoltaic module for rooftop mounting. Converts sunlight to electricity."),
    ("SKU-7734", "DuraSeal. Foil tape rated for HVAC ductwork. Withstands sustained high temperatures."),
    ("SKU-2251", "QuietVent ERV. Energy recovery ventilator exchanging stale indoor air for fresh outdoor air."),
    ("SKU-6690", "FrostGuard. Foam sleeves for plumbing exposed to sub-zero conditions. Prevents burst lines."),
    ("SKU-3345", "AquaPure RO. Reverse osmosis under-sink cartridge removing dissolved solids from drinking water."),
    ("SKU-8821", "StormShield. Solar-powered extractor that evacuates heat from a loft space."),
    ("SKU-5512", "TerraDrain FR. Perforated corrugated pipe for foundation drainage and groundwater diversion."),
    ("SKU-2907", "LumenArc LED Retrofit. Replaces fluorescent tubes in commercial ceiling fixtures. Low power draw."),
    ("SKU-6104", "CircuitSafe GFCI Outlet. Ground fault interrupter receptacle for wet locations such as bathrooms."),
    ("SKU-3378", "EchoStop Acoustic Batt. Mineral wool insulation for interior partitions. Reduces sound transmission."),
    ("SKU-8845", "VaporLock SMB. Polyethylene sheeting installed beneath slabs to block rising damp."),
    ("SKU-1273", "PulseGuard TVSS. Whole-panel surge protector clamping voltage spikes from the utility feed."),
    ("SKU-9960", "Cascade HRV Core. Heat recovery core cartridge, replacement part for balanced ventilation systems."),
    ("SKU-4088", "GeoStake Ground Anchor. Helical screw anchor for securing sheds and temporary structures."),
    ("SKU-7215", "ClearSpan Polycarbonate Glazing. Twin-wall sheet for greenhouse and canopy roofing."),
    ("SKU-3391", "SiltBar Sediment Fence. Woven geotextile barrier controlling runoff on construction sites."),
    ("SKU-6627", "ThermaBreak Sill Gasket. Closed-cell foam strip isolating framing from concrete."),
    ("SKU-1150", "AirSentry MERV 13. Pleated filter media capturing fine airborne particulates in forced-air systems."),
)

# The identifier is prepended to the indexed text on purpose. Storing it only as the record
# key would make it unsearchable, and a corpus whose identifiers cannot be matched is not a
# test of lexical retrieval -- it is a missing field.
CATALOG_DOCS = tuple({"doc_id": sku, "text": f"{sku} {text}"} for sku, text in CATALOG)

# Queries split by what kind of matching they require. Keeping the label on each one is the
# point: an aggregate MRR over a mixed workload hides exactly the thing worth seeing, which is
# that the two halves behave differently.
IDENTIFIER_QUERIES = (
    ("SKU-6690", "SKU-6690"),
    ("SKU-1273", "SKU-1273"),
    ("MERV 13", "SKU-1150"),
    ("GFCI", "SKU-6104"),
    ("ERV", "SKU-2251"),
    ("RO cartridge", "SKU-3345"),
)

PARAPHRASE_QUERIES = (
    ("stop my water lines bursting in a hard freeze", "SKU-6690"),
    ("make a bedroom less hot in summer", "SKU-9302"),
    ("produce my own power from the roof", "SKU-1188"),
    ("endless shower without a storage cylinder", "SKU-4417"),
    ("quieten a wall between two rooms", "SKU-3378"),
    ("keep moisture from wicking up through the floor", "SKU-8845"),
    ("protect appliances when lightning hits the grid", "SKU-1273"),
    ("hold a garden building down in high wind", "SKU-4088"),
)


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric runs.

    Deliberately crude, and the crudeness is load-bearing: `SKU-6690` becomes ['sku', '6690'],
    so the digits survive as their own searchable token. A tokenizer that dropped punctuation
    along with the digits -- or that stemmed aggressively -- would destroy the identifiers this
    corpus exists to test.
    """
    return re.findall(r"[a-z0-9]+", text.lower())


# --- a fact deliberately split across a chunk boundary -----------------------------------

# Chapter 3's Break-it #3 shows an answer split across two chunks and fixes it by retrieving
# more chunks. This is the same failure set up so the OTHER fix -- overlap -- can be measured
# against it. The two facts sit far enough apart that a 200-character chunk cannot hold both,
# and close enough that a modest overlap can.
SPLIT_FACT_TEXT = (
    "The Halden Reactor Project ran as an OECD joint undertaking for six decades. "
    "Its research reactor first reached criticality in 1959 at a site in south-eastern "
    "Norway, and operated continuously for decades afterwards under international "
    "supervision. The facility was permanently shut down in 2018, and the surrounding "
    "programme moved to decommissioning work and long-term fuel studies thereafter."
)
SPLIT_FACT_QUESTION = "When did the Halden reactor first reach criticality and when did it shut down?"
SPLIT_FACT_ANSWERS = ("1959", "2018")
