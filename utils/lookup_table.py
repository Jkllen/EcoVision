# lookup_table.py
# stores CO₂ emission mapping
# Estimated CO₂ equivalent emissions in kg per kg of material

carbon_lookup = {
    "plastic": 1.75,
    "paper": 0.95,
    "metal": 2.50,
    "glass": 0.90,
    "cardboard": 1.10,
    "biodegradable": 0.50,
    "clothes": 3.00,
    "others": 2.00
}

def get_carbon_value(material):
    return carbon_lookup.get(material.lower(), 0)
