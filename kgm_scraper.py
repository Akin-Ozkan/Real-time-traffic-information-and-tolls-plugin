import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_kgm_bulletin():
    url = "https://www.kgm.gov.tr/Sayfalar/KGM/SiteTr/YolDanisma/GunlukYolDurumuBulteni.aspx"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        bulletins = []
        
        # KGM's site uses various tags. We will scan all common text containers.
        elements = soup.find_all(['p', 'span', 'li', 'td'])
        
        # Keywords that are typically found in ACTUAL road bulletins
        keywords = [" km", "çalışma", "yönü", "şerit", "kapatılmış", "trafiğe", "ayrımı", "kavşağı", "viyadüğü", "otoyolu"]
        
        for element in elements:
            text = element.get_text(strip=True)
            text_lower = text.lower()
            
            # SMART FILTER:
            # 1. Must be longer than 40 characters (removes UI buttons/dates)
            # 2. Must contain at least one road-related keyword
            # 3. Check for duplicates
            if len(text) > 40 and any(kw in text_lower for kw in keywords):
                if text not in bulletins:
                    bulletins.append(text)
                    
        return bulletins

    except requests.exceptions.RequestException as e:
        print(f"Network error while connecting to KGM: {e}")
        return []
    except Exception as e:
        print(f"Parsing error: {e}")
        return []

if __name__ == "__main__":
    print("Fetching daily road bulletin from KGM...")
    kgm_data = scrape_kgm_bulletin()
    
    if kgm_data:
        print(f"Success! Fetched {len(kgm_data)} actual road notices.")
        
        output_data = {
            "source": "KGM",
            "updated_at": datetime.now().isoformat(),
            "total_notices": len(kgm_data),
            "notices": kgm_data
        }
        
        filename = "kgm_road_conditions.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        print(f"Data saved to '{filename}'.")
    else:
        print("Could not find appropriate notices. The KGM website structure might be fully JavaScript-rendered now.")