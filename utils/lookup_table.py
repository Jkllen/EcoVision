# lookup_table.py
# Stores estimated CO₂-equivalent emissions in kg CO₂ per kg of material
# Sources: EPA, ADEME, various LCA studies

carbon_lookup = {
    "plastic": 3.5,
    "paper": 0.8,
    "metal": 6.0,
    "glass": 0.9,
    "cardboard": 1.35,
    "trash": 2.0
}

def get_carbon_value(material):
    return carbon_lookup.get(material.lower(), 0)
