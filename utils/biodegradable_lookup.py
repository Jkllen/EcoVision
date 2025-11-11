# utils/biodegradable_lookup.py

# Lookup table for biodegradable vs non-biodegradable classification
BIODEGRADABLE_LOOKUP = {
    "plastic": False,
    "paper": True,
    "metal": False,
    "glass": False,
    "cardboard": True,
    "trash": False
}

def is_biodegradable(material: str) -> bool:
    """
    Returns True if the material is biodegradable, False otherwise.
    Defaults to False if unknown.
    """
    return BIODEGRADABLE_LOOKUP.get(material.lower(), False)
