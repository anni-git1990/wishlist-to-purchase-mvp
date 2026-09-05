"""
Myntra Wishlist Confidence Engine - Catalog Dataset (50+ Products)
Provides realistic apparel items across Men's, Women's, Activewear, and Kids categories
with personalized fit confidence scores, review digests, and customer media.
"""

from typing import List, Dict, Any


def get_50_product_catalog() -> List[Dict[str, Any]]:
    brands_mens = ["ROADSTER", "HRX BY HRITHIK ROSHAN", "HIGHLANDER", "WRANGLER", "LEVIS", "TOMMY HILFIGER", "JACK & JONES", "U.S. POLO ASSN."]
    brands_womens = ["ANOUK", "SANGRIA", "BBAE", "DRESSBERRY", "ONLY", "VERO MODA", "GLOBAL DESI", "MANGO"]
    
    categories = ["Men", "Women", "Activewear", "Ethnic"]
    
    items: List[Dict[str, Any]] = []

    # High Confidence Products (1 to 30)
    for i in range(1, 31):
        if i % 2 != 0:
            brand = brands_mens[(i - 1) % len(brands_mens)]
            category = "Men"
            title = f"{brand} Men Slim Fit Cotton Casual Shirt #{i}"
            img = f"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400"
            rec_size = "M" if i % 3 == 0 else ("L" if i % 3 == 1 else "S")
            match_pct = 85 + (i % 12)
            snippet = "100% combed cotton, soft feel, highly breathable for summer wear."
        else:
            brand = brands_womens[(i - 1) % len(brands_womens)]
            category = "Women"
            title = f"{brand} Women Printed Cotton A-Line Dress #{i}"
            img = f"https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400"
            rec_size = "S" if i % 3 == 0 else ("M" if i % 3 == 1 else "L")
            match_pct = 86 + (i % 11)
            snippet = "Lightweight rayon blend, graceful drape, color retention 4.8/5."

        items.append({
            "id": f"style_100{i:02d}",
            "brand": brand,
            "title": title,
            "category": category,
            "price": 999 + (i * 50),
            "originalPrice": 1999 + (i * 50),
            "discount": "50% OFF",
            "img": img,
            "recSize": rec_size,
            "matchPct": match_pct,
            "confidence": "HIGH",
            "trueToSizePct": 90 + (i % 8),
            "shrinkage": "Low (2%)",
            "reason": f"Based on 4 past purchases in size {rec_size} from {brand} & {12 + i} peer reviews.",
            "snippet": snippet,
            "aspects": [
                {"aspect": "Fabric & Feel", "pct": 96},
                {"aspect": "Stitching Quality", "pct": 92},
                {"aspect": "Color Permanence", "pct": 94}
            ],
            "reviews": [
                {"meta": f"Height: 5'9\" • Weight: 72kg • Size: {rec_size}", "text": "Fits perfectly across shoulders and length is spot on."},
                {"meta": f"Height: 5'10\" • Weight: 74kg • Size: {rec_size}", "text": "Great quality fabric. No tightness around chest."}
            ],
            "photos": [img]
        })

    # Medium Confidence Products (31 to 42)
    for i in range(31, 43):
        brand = "HRX BY HRITHIK ROSHAN" if i % 2 == 0 else "PUMA"
        category = "Activewear"
        title = f"{brand} Active Performance Training Jacket #{i}"
        img = "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400"
        rec_size = "L"
        match_pct = 72 + (i % 8)

        items.append({
            "id": f"style_100{i:02d}",
            "brand": brand,
            "title": title,
            "category": category,
            "price": 1499 + (i * 40),
            "originalPrice": 2999 + (i * 40),
            "discount": "50% OFF",
            "img": img,
            "recSize": rec_size,
            "matchPct": match_pct,
            "confidence": "MEDIUM",
            "trueToSizePct": 78,
            "shrinkage": "None (Polyester Blend)",
            "reason": f"Based on brand size chart and 6 customer reviews.",
            "snippet": "Moisture-wicking polyester blend, athletic stretch.",
            "aspects": [
                {"aspect": "Stretchability", "pct": 88},
                {"aspect": "Breathability", "pct": 82}
            ],
            "reviews": [
                {"meta": "Height: 6'0\" • Weight: 80kg • Size: L", "text": "Sleeves are long enough. Good stretch for running."}
            ],
            "photos": [img]
        })

    # Fallback 0-Review Products (43 to 52)
    for i in range(43, 53):
        brand = "ANOUK" if i % 2 == 0 else "ALLEN SOLLY"
        category = "Ethnic" if i % 2 == 0 else "Men"
        title = f"{brand} New Collection Tailored Fit Apparel #{i}"
        img = "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400" if i % 2 == 0 else "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400"

        items.append({
            "id": f"style_100{i:02d}",
            "brand": brand,
            "title": title,
            "category": category,
            "price": 1299 + (i * 30),
            "originalPrice": 2599 + (i * 30),
            "discount": "50% OFF",
            "img": img,
            "recSize": "Standard Chart",
            "matchPct": 0,
            "confidence": "FALLBACK",
            "trueToSizePct": 0,
            "shrinkage": "Unknown",
            "reason": "Limited evidence available. Standard brand size chart rendered.",
            "snippet": "Limited evidence available. Refer to brand size chart.",
            "aspects": [],
            "reviews": [],
            "photos": []
        })

    return items
