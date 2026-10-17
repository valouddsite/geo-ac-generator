from __future__ import annotations
import math, os
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = os.path.dirname(os.path.dirname(__file__))
MAX_AREA_KM2 = float(os.getenv("MAX_AREA_KM2", "50"))
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
app = FastAPI(title="Geo → Assetto Corsa Generator", version="0.1.0")
app.mount("/static", StaticFiles(directory=os.path.join(ROOT, "frontend")), name="static")

class Bounds(BaseModel):
    south: float = Field(ge=-90, le=90)
    west: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)

def area_km2(b: Bounds) -> float:
    h = (b.north-b.south)*111.32
    mid = (b.north+b.south)/2
    w = (b.east-b.west)*111.32*max(0.01, math.cos(math.radians(mid)))
    return abs(h*w)

def estimate_height(tags: dict[str, Any]) -> float:
    try:
        levels = float(str(tags.get("building:levels", "")).replace(",", "."))
        if 0 < levels < 100:
            return round(levels*3.0, 1)
    except (TypeError, ValueError):
        pass
    kind = str(tags.get("building", "")).lower()
    if kind in {"industrial", "warehouse", "retail", "commercial"}: return 7.0
    if kind in {"apartments", "office", "hotel"}: return 12.0
    if kind in {"church", "cathedral"}: return 16.0
    return 6.5

def building_quality(tags: dict[str, Any]) -> dict[str, Any]:
    has_height = bool(tags.get("height"))
    has_levels = bool(tags.get("building:levels"))
    has_roof = bool(tags.get("roof:shape"))
    if has_height and has_roof:
        level, confidence = "A/B — attributs détaillés", "élevée pour les attributs présents"
        basis = "attributs explicites; vérification terrain non garantie"
    elif has_height or has_levels:
        level, confidence = "B — attributs partiels", "moyenne"
        basis = "empreinte OSM réelle et quelques attributs"
    else:
        level, confidence = "C — estimation requise", "faible à moyenne"
        basis = "empreinte réelle, hauteur/toiture non confirmées"
    return {
        "reconstruction_level": level, "confidence": confidence,
        "confidence_basis": basis, "geometry_source": "OpenStreetMap footprint",
        "estimated_height_m": None if has_height else estimate_height(tags),
        "height_is_estimated": not has_height,
        "texture_status": "not_assigned",
        "estimated_fields": [name for name, present in [
            ("height", has_height or has_levels), ("roof:shape", has_roof)
        ] if not present]
    }

def osm_to_geojson(osm: dict[str, Any]) -> dict[str, Any]:
    features = []
    for e in osm.get("elements", []):
        typ, tags = e.get("type"), e.get("tags", {}) or {}
        props = {"osm_id": e.get("id"), "osm_type": typ, **tags}
        if typ == "node":
            if "lat" not in e or "lon" not in e: continue
            if any(k in tags for k in ("amenity", "shop", "tourism", "leisure", "historic", "natural")):
                features.append({"type":"Feature","geometry":{"type":"Point","coordinates":[e["lon"],e["lat"]]},"properties":props})
            continue
        if typ != "way": continue
        coords = [[p["lon"],p["lat"]] for p in e.get("geometry", []) if "lon" in p and "lat" in p]
        if len(coords) < 2: continue
        closed = len(coords) >= 4 and coords[0] == coords[-1]
        if "building" in tags and closed:
            props.update(building_quality(tags))
            geom = {"type":"Polygon","coordinates":[coords]}
        elif "highway" in tags:
            geom = {"type":"LineString","coordinates":coords}
        elif closed and any(k in tags for k in ("amenity","shop","tourism","leisure","landuse")):
            geom = {"type":"Polygon","coordinates":[coords]}
        else:
            continue
        features.append({"type":"Feature","geometry":geom,"properties":props})
    return {"type":"FeatureCollection","name":"geo-ac-export","features":features}

async def fetch_osm(b: Bounds) -> dict[str, Any]:
    query = f"""[out:json][timeout:45];
(
 way["highway"]({b.south},{b.west},{b.north},{b.east});
 way["building"]({b.south},{b.west},{b.north},{b.east});
 node["amenity"]({b.south},{b.west},{b.north},{b.east});
 node["shop"]({b.south},{b.west},{b.north},{b.east});
 node["tourism"]({b.south},{b.west},{b.north},{b.east});
 node["leisure"]({b.south},{b.west},{b.north},{b.east});
);
out body geom;"""
    async with httpx.AsyncClient(timeout=60, headers={"User-Agent":"GeoACGenerator/0.1"}) as client:
        r = await client.post(OVERPASS_URL, data={"data":query})
        r.raise_for_status()
        return r.json()

@app.get("/")
async def home():
    return FileResponse(os.path.join(ROOT, "frontend", "index.html"))

@app.get("/api/health")
async def health():
    return {"ok": True, "version": app.version, "max_area_km2": MAX_AREA_KM2}

@app.post("/api/extract")
async def extract(bounds: Bounds):
    if bounds.north <= bounds.south or bounds.east <= bounds.west:
        raise HTTPException(400, "Rectangle invalide.")
    area = area_km2(bounds)
    if area > MAX_AREA_KM2:
        raise HTTPException(413, f"Zone trop grande ({area:.2f} km²); maximum {MAX_AREA_KM2:.2f} km².")
    try:
        raw = await fetch_osm(bounds)
    except Exception as exc:
        raise HTTPException(502, f"Source OSM indisponible ou limitée ({type(exc).__name__}). Réessaie plus tard.")
    geo = osm_to_geojson(raw)
    features = geo["features"]
    buildings = [f for f in features if "building" in f["properties"]]
    counts = {
        "routes": sum("highway" in f["properties"] for f in features),
        "batiments": len(buildings),
        "points": sum(f["geometry"]["type"] == "Point" for f in features)
    }
    manifest = {
        "project": "Geo → Assetto Corsa Generator",
        "bounds": bounds.model_dump(), "area_km2": round(area, 4), "counts": counts,
        "building_quality_counts": {
            "detailed": sum(str(f["properties"].get("reconstruction_level","")).startswith("A/") for f in buildings),
            "partial": sum(str(f["properties"].get("reconstruction_level","")).startswith("B ") for f in buildings),
            "estimated": sum(str(f["properties"].get("reconstruction_level","")).startswith("C ") for f in buildings)
        },
        "sources": [{"name":"OpenStreetMap contributors","url":"https://www.openstreetmap.org/copyright","license":"ODbL 1.0","attribution":"© OpenStreetMap contributors"}],
        "texture_policy": "Aucune imagerie satellite n'est téléchargée. Ajouter uniquement des images et modèles dont la licence permet l'usage et la redistribution dans un mod.",
        "limitations": ["Les hauteurs heuristiques sont estimées, pas mesurées.", "Le MNT/DEM n'est pas encore intégré.", "Pas d'export KN5 direct."]
    }
    return {"geojson": geo, "manifest": manifest}
