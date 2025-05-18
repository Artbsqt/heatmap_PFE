import requests
import os
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import time

# --------------------------
# 1. Configuration améliorée
# --------------------------
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

geolocator = Nominatim(
    user_agent="my_heatmap_app_contact@example.com",
    timeout=10
)

# --------------------------
# 2. Récupération des données
# --------------------------
response = requests.post(
    f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
    headers={
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
)

if response.status_code != 200:
    print(f"❌ ERREUR API Notion : {response.text}")
    exit(1)

data = response.json()["results"]

# --------------------------
# 3. Géocodage avec gestion d'erreur
# --------------------------
coordinates = []
errors = []

for idx, entry in enumerate(data):
    try:
        props = entry["properties"]
        
        # Extraction du nom
        name = "".join([t["plain_text"] for t in props["Name"]["title"]])
        
        # Récupération de l'église
        eglise = props["Eglise"]["multi_select"]
        if not eglise:
            continue
            
        nom_eglise = eglise[0]["name"] + ", Angers, France"

        # Mécanisme de retry
        for attempt in range(3):
            try:
                location = geolocator.geocode(nom_eglise)
                if location:
                    coordinates.append((location.latitude, location.longitude))
                    print(f"✅ {name} : {nom_eglise} → {location.latitude},{location.longitude}")
                    break
                else:
                    if attempt == 2:
                        print(f"⚠️  Église non trouvée : {nom_eglise}")
                        errors.append(nom_eglise)
                    time.sleep(1)
            except Exception as e:
                if attempt == 2:
                    print(f"❌ Erreur de géocodage pour {nom_eglise} : {str(e)}")
                    errors.append(nom_eglise)
                time.sleep(1)

    except Exception as e:
        print(f"❌ Erreur générale sur l'entrée {idx} : {str(e)}")
        errors.append(f"Entrée {idx}")

# --------------------------
# 4. Création du dossier
# --------------------------
os.makedirs("docs", exist_ok=True)

# --------------------------
# 5. Génération de la carte
# --------------------------
m = folium.Map(location=[47.4784, -0.5632], zoom_start=13)

if coordinates:
    HeatMap(coordinates, radius=15, blur=20).add_to(m)
else:
    folium.Marker(
        [47.4784, -0.5632], 
        popup="Aucune donnée disponible",
        icon=folium.Icon(color="red")
    ).add_to(m)

# Sauvegarde des erreurs
with open("docs/errors.log", "w") as f:
    f.write("\n".join(errors))

m.save("docs/index.html")

# Rapport final
print("\n--- Résultat final ---")
print(f"Points valides : {len(coordinates)}")
print(f"Erreurs : {len(errors)}")
print(f"Fichier généré : docs/index.html")
print(f"Log des erreurs : docs/errors.log")
