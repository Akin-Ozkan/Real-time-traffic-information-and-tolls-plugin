import requests
import json
from datetime import datetime

def fetch_tomtom_traffic(api_key):
    # Bounding box for Eskisehir (minLon, minLat, maxLon, maxLat)
    bbox = "30.4000,39.7000,30.6500,39.8500"
    
    # TomTom Incident Details API Endpoint
    url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    
    # Requesting specific fields for a cleaner JSON response
    fields = "{incidents{type,geometry{type,coordinates},properties{iconCategory}}}"
    
    params = {
        "key": api_key,
        "bbox": bbox,
        "fields": fields,
        "language": "en-US" # Ensures incident descriptions (if added later) are in English
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"API Response: {response.text}")
        return None

def build_geojson(tomtom_data):
    if not tomtom_data:
        return None

    features = []
    
    if "incidents" in tomtom_data:
        for incident in tomtom_data["incidents"]:
            coords = incident.get("geometry", {}).get("coordinates", [])
            
            # Handle both Point and LineString coordinate structures
            if coords and isinstance(coords[0], list):
                lon, lat = coords[0][0], coords[0][1]
            elif coords:
                lon, lat = coords[0], coords[1]
            else:
                continue
            
            props = incident.get("properties", {})
            icon_category = props.get("iconCategory", "Unknown")
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "category_code": icon_category,
                    "updated_at": datetime.now().isoformat()
                }
            }
            features.append(feature)
            
    return {
        "type": "FeatureCollection",
        "features": features
    }

if __name__ == "__main__":
    # IMPORTANT: Replace the string below with your actual TomTom API key!
    API_KEY = os.environ.get("TOMTOM_API_KEY")
    
    print("Connecting to TomTom servers...")
    raw_data = fetch_tomtom_traffic(API_KEY)
    
    if raw_data:
        print("Data fetched successfully. Converting to GeoJSON format...")
        geojson_data = build_geojson(raw_data)
        
        filename = "eskisehir_traffic.geojson"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=4)
            
        print(f"Success! '{filename}' has been generated.")
    else:
        print("Failed to fetch data. GeoJSON file was not created.")