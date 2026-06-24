#!/usr/bin/env python3
import sys
import asyncio
import sqlite3
import os
import urllib.request
import urllib.parse
import json
import ssl
import time
from google.antigravity import Agent, LocalAgentConfig

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/travel_companion.db"))

def get_place_coordinates(place_name: str) -> dict:
    """Finds the latitude and longitude coordinates of a city or place using Wikipedia search.
    
    Args:
        place_name: Name of the place to search (e.g., "Mumbai", "Delhi").
        
    Returns:
        dict: A dictionary containing "lat", "lon", and "title" if found, else empty dict.
    """
    time.sleep(13)
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": place_name,
        "srlimit": 1
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    headers = {
        "User-Agent": "TravelCompanionAgent/1.0 (https://github.com/shreya/Travel-companion-India)"
    }
    
    context = ssl._create_unverified_context()
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return {}
            
            title = search_results[0]["title"]
            
            # Fetch coordinates for this article
            params_coords = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "coordinates"
            }
            query_string_coords = urllib.parse.urlencode(params_coords)
            full_url_coords = f"{url}?{query_string_coords}"
            
            req_coords = urllib.request.Request(full_url_coords, headers=headers)
            with urllib.request.urlopen(req_coords, context=context) as response_coords:
                data_coords = json.loads(response_coords.read().decode('utf-8'))
                pages = data_coords.get("query", {}).get("pages", {})
                for page_id, page in pages.items():
                    coords = page.get("coordinates", [{}])[0]
                    if coords.get("lat") and coords.get("lon"):
                        return {
                            "title": title,
                            "lat": coords["lat"],
                            "lon": coords["lon"]
                        }
            return {}
    except Exception as e:
        print(f"[!] Error fetching coordinates for {place_name}: {e}", file=sys.stderr)
        return {}

def fetch_wikipedia_geosearch(lat: float, lon: float, radius: int = 5000, limit: int = 4) -> list:
    """Queries Wikipedia for points of interest near the specified coordinates.
    
    Args:
        lat: Latitude coordinate.
        lon: Longitude coordinate.
        radius: Search radius in meters (max 10000).
        limit: Maximum results to return (max 10).
        
    Returns:
        list: List of dictionaries containing POI details.
    """
    time.sleep(13)
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggsradius": str(radius),
        "ggslimit": str(limit),
        "prop": "coordinates|pageimages|extracts",
        "exintro": "1",
        "explaintext": "1",
        "exchars": "200",
        "piprop": "thumbnail",
        "pithumbsize": "200"
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    headers = {
        "User-Agent": "TravelCompanionAgent/1.0 (https://github.com/shreya/Travel-companion-India)"
    }
    
    context = ssl._create_unverified_context()
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            if response.status != 200:
                raise Exception(f"HTTP Error: {response.status}")
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            
            results = []
            for page_id, page in pages.items():
                coords = page.get("coordinates", [{}])[0]
                if not coords.get("lat") or not coords.get("lon"):
                    continue
                results.append({
                    "pageid": page.get("pageid"),
                    "title": page.get("title"),
                    "lat": coords.get("lat"),
                    "lon": coords.get("lon"),
                    "summary": page.get("extract"),
                    "image_url": page.get("thumbnail", {}).get("source")
                })
            return results
    except Exception as e:
        print(f"[!] Error fetching POIs from Wikipedia for {lat},{lon}: {e}", file=sys.stderr)
        return []

def save_poi_to_db(city_name: str, city_lat: float, city_lon: float, pageid: int, title: str, poi_lat: float, poi_lon: float, summary: str, image_url: str = None) -> str:
    """Inserts or updates a point of interest (article) in the SQLite database under a city group.
    
    Args:
        city_name: Name of the city group (e.g., "Mumbai").
        city_lat: Latitude of the city.
        city_lon: Longitude of the city.
        pageid: Wikipedia page ID of the POI.
        title: Title of the POI.
        poi_lat: Latitude of the POI.
        poi_lon: Longitude of the POI.
        summary: Brief summary of the POI.
        image_url: Optional URL of the POI's thumbnail image.
        
    Returns:
        str: Status message indicating success or failure.
    """
    time.sleep(13)
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Insert/get group
        cursor.execute("""
        INSERT INTO groups (name, latitude, longitude) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET latitude=excluded.latitude, longitude=excluded.longitude
        """, (city_name, city_lat, city_lon))
        conn.commit()
        
        cursor.execute("SELECT id FROM groups WHERE name = ?", (city_name,))
        group_id = cursor.fetchone()[0]
        
        # Insert POI
        cursor.execute("""
        INSERT INTO points_of_interest 
        (group_id, pageid, title, latitude, longitude, summary, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(pageid) DO UPDATE SET
            group_id=excluded.group_id,
            title=excluded.title,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            summary=excluded.summary,
            image_url=excluded.image_url
        """, (group_id, pageid, title, poi_lat, poi_lon, summary, image_url))
        conn.commit()
        conn.close()
        return f"Successfully saved '{title}' to SQLite database under city '{city_name}'."
    except Exception as e:
        return f"Error saving '{title}' to database: {e}"

async def run_agent(city_name: str):
    """Runs the Google Antigravity SDK agent to populate POIs for a city."""
    system_instructions = (
        f"You are a travel helper agent. Your goal is to populate the SQLite database with interesting "
        f"Wikipedia articles (points of interest) for the city '{city_name}'.\n\n"
        f"Steps you must perform:\n"
        f"1. Use `get_place_coordinates` to retrieve the latitude and longitude of '{city_name}'.\n"
        f"2. Use those coordinates to query for nearby points of interest using `fetch_wikipedia_geosearch`.\n"
        f"3. For each interesting point of interest returned (limit to at most 4), call `save_poi_to_db` to write it to the database "
        f"associated with '{city_name}'. Make sure you pass the correct coordinates of the city and the POI.\n\n"
        f"Database File Path: {DB_PATH}\n"
        f"Execute your task fully. Report back a summary of the seeded articles when complete."
    )
    
    config = LocalAgentConfig(
        model="gemini-3.1-flash-lite",
        tools=[get_place_coordinates, fetch_wikipedia_geosearch, save_poi_to_db],
        system_instructions=system_instructions
    )
    
    print(f"[*] Initializing Antigravity agent for {city_name}...")
    async with Agent(config) as agent:
        prompt = f"Find and store points of interest for {city_name}."
        print(f"[*] Prompting Agent: '{prompt}'")
        response = await agent.chat(prompt)
        
        print("\n=== Agent Output ===")
        async for chunk in response:
            print(chunk, end="", flush=True)
        print("\n====================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 populate_city_pois.py <city_name>")
        sys.exit(1)
        
    city = sys.argv[1]
    asyncio.run(run_agent(city))
