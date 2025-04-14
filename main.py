import requests
import os
from geopy.geocoder import Nominatim
import folium
from folium.plugins import HeatMap
from pathlib import Path



# Config
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")


# Créer le dossier "docs" si inexistant
Path("docs").mkdir(exist_ok=True)


# Récupération des données depuis Notion
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

response = requests.post(
    f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
    headers=headers
)
data = response.json()["results"]

# Géocodage depuis la colonne "Eglise"
geolocator = Nominatim(user_agent="angers_churches")
coordinates = []

for entry in data:
    props = entry["properties"]
    
    # 1. Récupérer le nom de l'église (colonne Titre "Eglise")
    eglise_name = props["Eglise"]["title"][0]["plain_text"]  # Accès au titre
    
    # 2. Géocodage avec le nom + "Angers" pour améliorer la précision
    try:
        location = geolocator.geocode(f"{eglise_name}, Angers, France")
        if location:
            coordinates.append((location.latitude, location.longitude))
            print(f"✅ {eglise_name} → {location.latitude}, {location.longitude}")
        else:
            print(f"⚠️ Non trouvé : {eglise_name}")
    except Exception as e:
        print(f"❌ Erreur avec {eglise_name} : {str(e)}")


# Génération de la carte
m = folium.Map(location=[47.4784, -0.5632], zoom_start=13)
HeatMap(coordinates, radius=15).add_to(m)
m.save("docs/index.html")  # Dossier pour GitHub Pages

m.save("docs/index.html") 
