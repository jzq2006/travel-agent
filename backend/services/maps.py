import math
import re
import requests as http

from config import AMAP_KEY


# ── 基础 API 调用 ──

def geocode(address: str, city: str = "") -> tuple | None:
    """地址 → (经度, 纬度)"""
    if not AMAP_KEY:
        return None
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={"address": address, "city": city, "key": AMAP_KEY},
            timeout=8,
        )
        data = resp.json()
        if data.get("geocodes"):
            loc = data["geocodes"][0]["location"]
            lng, lat = loc.split(",")
            return (float(lng), float(lat))
    except Exception:
        pass
    return None


def reverse_geocode(lng: float, lat: float) -> str:
    """经纬度 → 地址描述"""
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/geocode/regeo",
            params={"location": f"{lng},{lat}", "key": AMAP_KEY},
            timeout=8,
        )
        data = resp.json()
        return data.get("regeocode", {}).get("formatted_address", "")
    except Exception:
        return ""


def haversine(lng1, lat1, lng2, lat2) -> float:
    """两点间直线距离（公里）"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def fetch_driving_route(origin: tuple, dest: tuple) -> dict | None:
    """驾车路线：返回 {distance_km, duration_min}"""
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/direction/driving",
            params={
                "origin": f"{origin[0]},{origin[1]}",
                "destination": f"{dest[0]},{dest[1]}",
                "key": AMAP_KEY,
            },
            timeout=8,
        )
        data = resp.json()
        path = data.get("route", {}).get("paths", [{}])[0]
        dist_m = int(path.get("distance", 0))
        dur_s = int(path.get("duration", 0))
        return {"distance_km": round(dist_m / 1000, 1), "duration_min": round(dur_s / 60)}
    except Exception:
        return None


def fetch_transit_route(origin: tuple, dest: tuple, city: str) -> dict | None:
    """公交路线：返回 {duration_min, cost}"""
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/direction/transit/integrated",
            params={
                "origin": f"{origin[0]},{origin[1]}",
                "destination": f"{dest[0]},{dest[1]}",
                "city": city,
                "key": AMAP_KEY,
            },
            timeout=8,
        )
        data = resp.json()
        transit = data.get("route", {}).get("transits", [{}])[0]
        dur_s = int(transit.get("duration", 0))
        cost = transit.get("cost", "?")
        return {"duration_min": round(dur_s / 60), "cost": cost}
    except Exception:
        return None


# ── POI 搜索 ──

POI_TYPE_MAP = {
    "景点": "110200|110100",
    "风景名胜": "110200",
    "公园": "110100",
    "博物馆": "140100",
    "餐饮": "050000",
    "美食": "050000",
    "小吃": "050300",
    "酒店": "100100",
    "住宿": "100000",
    "购物": "060000",
    "娱乐": "080000",
}


def search_poi(city: str, keyword: str = "", poi_type: str = "") -> list[dict]:
    """搜索城市中的兴趣点（景点、餐厅等）。

    Args:
        city: 城市名
        keyword: 搜索关键词，如"西湖"、"火锅"
        poi_type: 类型，如"景点"、"餐饮"、"酒店"
    """
    if not AMAP_KEY:
        return []

    types = POI_TYPE_MAP.get(poi_type, "")

    try:
        resp = http.get(
            "https://restapi.amap.com/v3/place/text",
            params={
                "keywords": keyword,
                "city": city,
                "citylimit": "true",
                "types": types,
                "offset": 10,
                "key": AMAP_KEY,
            },
            timeout=8,
        )
        data = resp.json()
        results = []
        for poi in data.get("pois", [])[:10]:
            biz = poi.get("biz_ext", {})
            results.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", "") or poi.get("pname", ""),
                "type": poi.get("type", "").split(";")[0] if poi.get("type") else "",
                "rating": biz.get("rating", "-"),
                "cost": biz.get("cost", "-"),
                "location": poi.get("location", ""),
            })
        return results
    except Exception:
        return []


def search_hotels(coord: tuple, city: str, radius: int = 5000) -> list[dict]:
    """搜索坐标附近酒店。"""
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/place/around",
            params={
                "location": f"{coord[0]},{coord[1]}",
                "types": "住宿服务",
                "city": city,
                "radius": radius,
                "sortrule": "distance",
                "offset": 8,
                "key": AMAP_KEY,
            },
            timeout=8,
        )
        data = resp.json()
        hotels = []
        for poi in data.get("pois", [])[:8]:
            biz = poi.get("biz_ext", {})
            hotels.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", "") or poi.get("pname", ""),
                "rating": biz.get("rating", "-"),
                "cost": biz.get("cost", "-"),
            })
        return hotels
    except Exception:
        return []


def search_hotels_by_keyword(city: str, keyword: str = "") -> list[dict]:
    """按关键词搜索酒店。"""
    if not AMAP_KEY:
        return []
    try:
        resp = http.get(
            "https://restapi.amap.com/v3/place/text",
            params={
                "keywords": keyword or "酒店",
                "city": city,
                "citylimit": "true",
                "types": "100000",
                "offset": 8,
                "key": AMAP_KEY,
            },
            timeout=8,
        )
        data = resp.json()
        hotels = []
        for poi in data.get("pois", [])[:8]:
            biz = poi.get("biz_ext", {})
            hotels.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", "") or poi.get("pname", ""),
                "rating": biz.get("rating", "-"),
                "cost": biz.get("cost", "-"),
            })
        return hotels
    except Exception:
        return []
