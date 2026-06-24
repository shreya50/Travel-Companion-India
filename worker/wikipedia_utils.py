#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.parse
import argparse

def fetch_nearby_places(lat: float, lon: float, radius: int = 5000, limit: int = 10):
    """
    Fetches articles from Wikipedia near the given latitude and longitude.
    
    Args:
        lat (float): Latitude of center point.
        lon (float): Longitude of center point.
        radius (int): Search radius in meters (max 10000).
        limit (int): Max search results (max 500).
    
    Returns:
        list: List of dictionaries containing page info (pageid, title, lat, lon, summary, image_url).
    """
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
    
    # Wikipedia API requests a descriptive User-Agent
    headers = {
        "User-Agent": "TravelCompanionIndia/1.0 (https://github.com/shreya/Travel-companion-India)"
    }
    
    import ssl
    context = ssl._create_unverified_context()
    
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")
            data = json.loads(response.read().decode('utf-8'))
            
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                coords = page.get("coordinates", [{}])[0]
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
        print(f"Error fetching data from Wikipedia: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="Fetch nearby points of interest from Wikipedia.")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters (default: 5000)")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    
    args = parser.parse_args()
    
    results = fetch_nearby_places(args.lat, args.lon, radius=args.radius, limit=args.limit)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
