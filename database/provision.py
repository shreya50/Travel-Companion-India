#!/usr/bin/env python3
import os
import sys
import sqlite3
import urllib.request
import urllib.parse
import json
import ssl
import argparse

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "travel_companion.db")

def init_db():
    """Initializes the database schema."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable Foreign Key enforcement in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create groups (cities) table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create points_of_interest table (associated with a group)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS points_of_interest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        pageid INTEGER UNIQUE NOT NULL,
        title TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        summary TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"[*] SQLite Database initialized at: {DB_PATH}")

def fetch_from_wikipedia(lat, lon, radius=5000, limit=10):
    """Fetches articles from Wikipedia near the coordinates using the generator search."""
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
        "User-Agent": "TravelCompanionIndiaDatabaseSeeder/1.0 (https://github.com/shreya/Travel-companion-India)"
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
        print(f"[!] Error fetching from Wikipedia for {lat},{lon}: {e}", file=sys.stderr)
        return []

def seed_group(name, lat, lon, radius=5000, limit=10):
    """Seeds a city group and automatically populates its POIs using the Wikipedia Geosearch API."""
    if not os.path.exists(DB_PATH):
        print("[*] Database doesn't exist. Initializing schema first...")
        init_db()
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Insert/update the group
    cursor.execute("""
    INSERT INTO groups (name, latitude, longitude) VALUES (?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET latitude=excluded.latitude, longitude=excluded.longitude
    """, (name, lat, lon))
    conn.commit()
    
    # Get group ID
    cursor.execute("SELECT id FROM groups WHERE name = ?", (name,))
    group_id = cursor.fetchone()[0]
    
    # 2. Fetch live POIs from Wikipedia
    print(f"[*] Fetching points of interest near {name} ({lat}, {lon}) with radius {radius}m...")
    pois = fetch_from_wikipedia(lat, lon, radius, limit)
    
    # 3. Save POIs to Database
    inserted_count = 0
    for poi in pois:
        try:
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
            """, (group_id, poi["pageid"], poi["title"], poi["lat"], poi["lon"], poi["summary"], poi["image_url"]))
            inserted_count += 1
        except Exception as e:
            print(f"[!] Failed to insert POI {poi['title']}: {e}", file=sys.stderr)
            
    conn.commit()
    conn.close()
    print(f"[+] Successfully saved/updated {inserted_count} points of interest for group '{name}' in the database.")

def list_db_contents():
    """Lists the stored groups and points of interest in the database."""
    if not os.path.exists(DB_PATH):
        print("[!] Database does not exist yet. Please run --init first.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, latitude, longitude FROM groups")
    groups = cursor.fetchall()
    
    if not groups:
        print("[-] No groups found in the database.")
        conn.close()
        return
        
    print("\n" + "="*60)
    print("STOCKED GROUPS & POINTS OF INTEREST")
    print("="*60)
    
    for g_id, g_name, g_lat, g_lon in groups:
        print(f"\n📍 Group: {g_name} ({g_lat}, {g_lon}) [ID: {g_id}]")
        cursor.execute("""
        SELECT pageid, title, latitude, longitude, summary 
        FROM points_of_interest 
        WHERE group_id = ?
        """, (g_id,))
        pois = cursor.fetchall()
        
        if not pois:
            print("  (No points of interest linked to this group)")
        else:
            for p_pageid, p_title, p_lat, p_lon, p_summary in pois:
                summary_snippet = (p_summary[:80] + "...") if p_summary else "No summary"
                print(f"  • {p_title} (ID: {p_pageid})")
                print(f"    Coords: {p_lat}, {p_lon}")
                print(f"    Summary: {summary_snippet}")
                
    print("="*60 + "\n")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Provision SQLite Database with Wikipedia Places of Interest.")
    parser.add_argument("--init", action="store_true", help="Initialize the database schema.")
    parser.add_argument("--seed", nargs=3, metavar=("NAME", "LAT", "LON"), help="Seed a city/group name and coordinates (e.g. Mumbai 18.9220 72.8347)")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters when seeding (default: 5000)")
    parser.add_argument("--limit", type=int, default=10, help="Max results when seeding (default: 10)")
    parser.add_argument("--list", action="store_true", help="List current database entries.")
    
    args = parser.parse_args()
    
    if args.init:
        init_db()
    elif args.seed:
        name = args.seed[0]
        try:
            lat = float(args.seed[1])
            lon = float(args.seed[2])
        except ValueError:
            print("[!] Latitude and Longitude must be floating point numbers.")
            sys.exit(1)
        seed_group(name, lat, lon, radius=args.radius, limit=args.limit)
    elif args.list:
        list_db_contents()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
