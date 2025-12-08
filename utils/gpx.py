import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Tuple

import pandas as pd

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two lat/lon points."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def parse_gpx_to_df(gpx_content: str) -> pd.DataFrame:
    """Parse GPX XML content into a DataFrame with lat, lon, ele, dist and cum_dist.

    Accepts a string (already-decoded file contents). Use `read_gpx_file` for path-based.
    """
    ns = {
        "default": "http://www.topografix.com/GPX/1/1",
    }
    root = ET.fromstring(gpx_content)

    pts: List[Tuple[float, float, Optional[float]]] = []

    # Collect track points (trk > trkseg > trkpt)
    for trk in root.findall(".//default:trk", ns):
        for seg in trk.findall("default:trkseg", ns):
            for tp in seg.findall("default:trkpt", ns):
                lat = float(tp.attrib.get("lat"))
                lon = float(tp.attrib.get("lon"))
                ele_el = tp.find("default:ele", ns)
                ele = float(ele_el.text) if ele_el is not None and ele_el.text else None
                pts.append((lat, lon, ele))

    # If no trk, fallback to route points (rte > rtept)
    if not pts:
        for rte in root.findall(".//default:rte", ns):
            for rp in rte.findall("default:rtept", ns):
                lat = float(rp.attrib.get("lat"))
                lon = float(rp.attrib.get("lon"))
                ele_el = rp.find("default:ele", ns)
                ele = float(ele_el.text) if ele_el is not None and ele_el.text else None
                pts.append((lat, lon, ele))

    if not pts:
        return pd.DataFrame(columns=[
            'position_lat',
            'position_lon',
            'altitude',
            'distance',
            'distance_change'
        ])

    rows = []
    cum = 0.0
    prev = None
    for lat, lon, ele in pts:
        if prev is None:
            d = 0.0
        else:
            d = _haversine(prev[0], prev[1], lat, lon)
        cum += d
        rows.append({
            'position_lat': lat,
            'position_lon': lon,
            'altitude': ele,
            'distance': cum,
            'distance_change': d
        })
        prev = (lat, lon)

    df = pd.DataFrame(rows)
    return df


def read_gpx(gpx_path: Path) -> pd.DataFrame:
    with open(gpx_path, 'rb') as f:
        gpx_bytes = f.read()

    gpx_content = gpx_bytes.decode('utf-8', errors='ignore')

    return parse_gpx_to_df(gpx_content)


def route_summary(df: pd.DataFrame) -> tuple[float, float]:
    if df.empty:
        raise RuntimeError(f"GPX contained no route points")

    distance = float(df['distance'].iloc[-1])
    elevation_gain = float(df['altitude'].diff().clip(lower=0).sum())
    return distance, elevation_gain
