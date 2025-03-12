import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PRACTO_API_KEY = os.getenv("PRACTO_API_KEY")

def fetch_google_maps_data(location: str):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={location}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}

def fetch_perplexity_data(query: str):
    url = f"https://api.perplexity.ai/query"
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
    payload = {"query": query}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}

def fetch_practo_data(query: str):
    url = f"https://api.practo.com/v1/search?q={query}&key={PRACTO_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}

