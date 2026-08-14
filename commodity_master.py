# 🛢️ ஒட்டுமொத்த இந்திய (MCX ₹) மற்றும் சர்வதேச ($) கமாடிட்டி பங்குகளின் மாஸ்டர் பட்டியல்

COMMODITY_LIST = {
    # 1. தங்கம் மற்றும் வெள்ளி பிரிவுகள் (Bullion)
    "24KGOLDM.NS": "MCX இந்திய தங்கம் (Gold 10g - ₹)",
    "SILVERM.NS": "MCX இந்திய வெள்ளி (Silver 1kg - ₹)",
    "GC=F": "சர்வதேச தங்கம் (Gold - $ / Ounce)",
    "SI=F": "சர்வதேச வெள்ளி (Silver - $ / Ounce)",
    
    # 2. எரிசக்தி பிரிவுகள் (Energy)
    "CRUDEOIL.NS": "MCX இந்திய கச்சா எண்ணெய் (Crude - ₹ / Barrel)",
    "NATURALGAS.NS": "MCX இந்திய இயற்கை எரிவாயு (Gas - ₹)",
    "CL=F": "சர்வதேச கச்சா எண்ணெய் (Crude Oil - $)",
    "NG=F": "சர்வதேச இயற்கை எரிவாயு (Natural Gas - $)",
    
    # 3. உலோகப் பிரிவுகள் (Base Metals)
    "COPPER.NS": "MCX இந்திய செம்பு (Copper - ₹ / kg)",
    "ALUMINIUM.NS": "MCX இந்திய அலுமினியம் (Aluminium - ₹ / kg)",
    "ZINC.NS": "MCX இந்திய துத்தநாகம் (Zinc - ₹ / kg)",
    "LEAD.NS": "MCX இந்திய ஈயம் (Lead - ₹ / kg)",
    "HG=F": "சர்வதேச செம்பு (Copper - $)",
    "ALI=F": "சர்வதேச அலுமினியம் (Aluminium - $)",
    
    # 4. விவசாயப் பொருட்கள் (Agri Commodities)
    "MENTHAEXPO.NS": "MCX இந்திய மெந்தா எண்ணெய் (Mentha Oil - ₹)",
    "COTTON.NS": "MCX இந்திய பருத்தி (Cotton - ₹ / Bale)",
    "CC=F": "சர்வதேச கொக்கோ (Cocoa - $)",
    "KC=F": "சர்வதேச காபி (Coffee - $)",
    "SB=F": "சர்வதேச சர்க்கரை (Sugar - $)"
}

def get_all_commodities():
    return COMMODITY_LIST

