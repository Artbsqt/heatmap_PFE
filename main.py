import requests
import os
from geopy.geocoder import Nominatim
import folium
from folium.plugins import HeatMap

# Config
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

# 1. Récupération des données
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

response = requests.post(
    f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
    headers=headers
)
data = response.json()["results"]

# 2. Extraction des données clés
geolocator = Nominatim(user_agent="angers_churches")
coordinates = []

for entry in data:
    props = entry["properties"]
    
    # Récupération du nom
    name = "".join([t["plain_text"] for t in props["Name"]["title"]])
    
    # Récupération de l'église (premier élément du multi-select)
    eglise = props["Eglise"]["multi_select"]
    if not eglise:  # Si pas d'église, on saute
        continue
    
    nom_eglise = eglise[0]["name"] + ", Angers, France"
    
    # Géocodage
    try:
        location = geolocator.geocode(nom_eglise)
        if location:
            coordinates.append((location.latitude, location.longitude))
            print(f"✅ {name} : {nom_eglise} → {location.latitude},{location.longitude}")
        else:
            print(f"⚠️  Église non trouvée : {nom_eglise}")
    except Exception as e:
        print(f"❌ Erreur de géocodage pour {nom_eglise} : {str(e)}")

# 3. Génération de la carte
if coordinates:
    m = folium.Map(location=[47.4784, -0.5632], zoom_start=13)
    HeatMap(coordinates, radius=15, blur=20).add_to(m)
    m.save("docs/index.html")
    print(f"\n🎉 Carte générée avec {len(coordinates)} points !")
else:
    print("\n😢 Aucune coordonnée valide trouvée.")
