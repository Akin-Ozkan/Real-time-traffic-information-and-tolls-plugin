import json
import requests
import re
from datetime import datetime
import os



def clean_query_for_tomtom(text):
    """
    KGM metinlerini TomTom'un anlayabileceği daha temiz bir formata sokar.
    """
    # Öncelik 1: Belirgin yapıları (Kavşak, Tünel, Gişe) yakala ve eklerinden arındır
    pattern = r'([A-ZÇĞİÖŞÜ][a-zçğıöşüA-ZÇĞİÖŞÜ\s]+(Kavşağı|Gişeleri|Tüneli|Köprüsü|Otoyolu))'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    # Öncelik 2: "Ankara-Bala-Karakeçili yolunun 30-35.km.leri" gibi karmaşık metinlerde
    # tireden önceki ana şehri/ilçeyi alıp sonuna "Yolu" ekleyelim (Örn: "Ankara Yolu")
    if "-" in text:
        first_part = text.split("-")[0].strip()
        # Çok kısa veya anlamsız değilse kullan
        if len(first_part) > 3:
            return f"{first_part} Yolu"
            
    # Hiçbirine uymuyorsa ilk 3 kelimeyi alıp şansımızı deneyelim
    return " ".join(text.split()[:3])

def geocode_with_tomtom(query, api_key):
    """TomTom Fuzzy Search API ile akıllı koordinat bulma"""
    # TomTom arama URL'si (TR ile sınırlandırılmış)
    url = f"https://api.tomtom.com/search/2/geocode/{query}.json"
    
    params = {
        "key": api_key,
        "countrySet": "TR", # Sadece Türkiye'de ara
        "limit": 1 # Sadece en iyi eşleşmeyi getir
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            position = data["results"][0]["position"]
            return position["lon"], position["lat"]
    except Exception as e:
        # 400 veya 403 hatalarını gizleyip sadece sonucu dönebiliriz
        pass
        
    return None, None

def process_kgm_to_geojson():
    # TODO: Buraya kendi TomTom API anahtarını yapıştır!
    TOMTOM_API_KEY = os.environ.get("TOMTOM_API_KEY")
    
    try:
        with open("kgm_road_conditions.json", "r", encoding="utf-8") as f:
            kgm_data = json.load(f)
    except FileNotFoundError:
        print("Hata: 'kgm_road_conditions.json' bulunamadı.")
        return

    features = []
    notices = kgm_data.get("notices", [])
    
    print(f"Toplam {len(notices)} KGM duyurusu TomTom Zekası ile aranıyor...\n")

    for idx, notice in enumerate(notices):
        # Metni temizle
        location_query = clean_query_for_tomtom(notice)
        
        # TomTom'a sor
        lon, lat = geocode_with_tomtom(location_query, TOMTOM_API_KEY)
        
        if lon and lat:
            print(f"[{idx+1}/{len(notices)}] BAŞARILI: '{location_query}' -> {lat}, {lon}")
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "source": "KGM",
                    "description": notice,
                    "extracted_keyword": location_query,
                    "category": "road_work",
                    "updated_at": datetime.now().isoformat()
                }
            }
            features.append(feature)
        else:
            print(f"[{idx+1}/{len(notices)}] BULUNAMADI: '{location_query}'")

    geojson_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    filename = "kgm_mapped.geojson"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(geojson_collection, f, ensure_ascii=False, indent=4)
        
    print(f"\nİşlem Tamamlandı! {len(features)} adet KGM uyarısı haritalandı.")

if __name__ == "__main__":
    process_kgm_to_geojson()