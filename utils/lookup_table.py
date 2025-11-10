# lookup_table.py
# Stores estimated CO₂-equivalent emissions in kg CO₂ per kg of material
# Sources: EPA, ADEME, various LCA studies

carbon_lookup = {
    "plastic": 2.5,         # average plastic packaging, kg CO2/kg
    "paper": 0.8,           # uncoated paper, kg CO2/kg
    "metal": 6.0,           # aluminum can, average kg CO2/kg
    "glass": 0.9,           # bottle glass, kg CO2/kg
    "cardboard": 1.2,       # corrugated cardboard, kg CO2/kg
    "biodegradable": 0.3,   # organic waste decomposition (composted), kg CO2/kg
    "clothes": 9.0,         # cotton T-shirt avg lifecycle, kg CO2/kg
    "battery": 12.0,        # lithium-ion battery, kg CO2/kg
    "shoes": 7.5,           # average leather/shoe lifecycle, kg CO2/kg
    "trash": 2.0,           # general non-recyclable waste, kg CO2/kg
    "others": 2.0           # fallback
}

def get_carbon_value(material):
    """
    Returns the estimated CO₂-equivalent emissions (kg CO2 per kg) 
    for a given material. Defaults to 0 if material is unknown.
    """
    return carbon_lookup.get(material.lower(), 0)
