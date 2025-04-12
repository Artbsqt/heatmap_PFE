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

# Géocodage des adresses (si nécessaire)
geolocator = Nominatim(user_agent="angers_churches")
coordinates = []

for entry in data:
    props = entry["properties"]
    
    # Si vous avez déjà les coordonnées :
    if "Coordonnées" in props:
        lat, lon = map(float, props["Coordonnées"]["rich_text"][0]["plain_text"].split(","))
        coordinates.append((lat, lon))
    
    # Si vous avez une adresse :
    elif "Adresse" in props:
        adresse = props["Adresse"]["rich_text"][0]["plain_text"] + ", Angers, France"
        location = geolocator.geocode(adresse)
        if location:
            coordinates.append((location.latitude, location.longitude))

# Génération de la carte
m = folium.Map(location=[47.4784, -0.5632], zoom_start=13)
HeatMap(coordinates, radius=15).add_to(m)
m.save("docs/index.html")  # Dossier pour GitHub Pages

m.save("docs/index.html") 
