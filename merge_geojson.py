import json

def merge_geojsons(file1, file2, output_file):
    features1 = []
    features2 = []
    
    # 1. Dosyayı Oku (TomTom Anlık Trafik)
    try:
        with open(file1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
            features1 = data1.get("features", [])
            print(f"{file1} okundu: {len(features1)} anlık olay bulundu.")
    except FileNotFoundError:
        print(f"Uyarı: '{file1}' bulunamadı, atlanıyor.")

    # 2. Dosyayı Oku (KGM Yol Çalışmaları)
    try:
        with open(file2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
            features2 = data2.get("features", [])
            print(f"{file2} okundu: {len(features2)} yol çalışması bulundu.")
    except FileNotFoundError:
        print(f"Uyarı: '{file2}' bulunamadı, atlanıyor.")

    # 3. Verileri Birleştir
    merged_features = features1 + features2

    # 4. Yeni GeoJSON Dosyasını Oluştur
    merged_geojson = {
        "type": "FeatureCollection",
        "features": merged_features
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_geojson, f, ensure_ascii=False, indent=4)
        
    print("-" * 40)
    print(f"Mükemmel! Toplam {len(merged_features)} harita noktası '{output_file}' dosyasında birleştirildi.")

if __name__ == "__main__":
    # Dosya isimlerini kendi projendeki isimlendirmelere göre ayarlayabilirsin
    tomtom_file = "eskisehir_traffic.geojson" 
    kgm_file = "kgm_mapped.geojson"
    master_file = "master_traffic.geojson"
    
    merge_geojsons(tomtom_file, kgm_file, master_file)