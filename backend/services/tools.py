"""Agent 工具定义 — 每个 @tool 封装一个外部 API 调用，供 LLM 自主选择调用。

工具的 docstring 至关重要：LLM 会阅读 docstring 来决定调用哪个工具、传什么参数。
"""

import json
from langchain_core.tools import tool

from services.weather import fetch_weather
from services.maps import (
    geocode,
    haversine,
    fetch_driving_route,
    fetch_transit_route,
    search_poi,
    search_hotels,
    search_hotels_by_keyword,
)


@tool
def query_weather(city: str, start_date: str = "", end_date: str = "") -> str:
    """查询指定城市未来7天的天气预报，包含温度、天气状况、风力、湿度。

    当需要了解目的地天气以便调整行程时调用此工具。
    例如发现雨天则需要安排室内景点，高温天则需提醒防晒。

    Args:
        city: 城市名称，如"杭州"、"北京"、"成都"
        start_date: 出行开始日期，格式YYYY-MM-DD，可选
        end_date: 出行结束日期，格式YYYY-MM-DD，可选

    Returns:
        格式化的天气预报文本，包含每日天气和注意事项
    """
    return fetch_weather(city, start_date, end_date)


@tool
def search_attractions(city: str, keyword: str = "", poi_type: str = "景点") -> str:
    """搜索城市中的景点、餐厅、博物馆等兴趣点。

    当需要了解某个城市有哪些值得去的地方时调用此工具。
    可以按关键词搜索（如"西湖"），也可以按类型浏览（如"美食"、"博物馆"）。

    Args:
        city: 城市名称
        keyword: 搜索关键词，如"火锅"、"博物馆"。留空则返回热门景点
        poi_type: 类型筛选，可选值：景点、餐饮、美食、小吃、博物馆、购物、娱乐

    Returns:
        兴趣点列表，包含名称、地址、类型、评分、人均消费
    """
    results = search_poi(city, keyword, poi_type)
    if not results:
        return f"未找到{city}的相关{poi_type}信息"

    lines = [f"在{city}搜索到以下{poi_type or '地点'}："]
    for i, poi in enumerate(results, 1):
        line = f"  {i}. {poi['name']}（{poi['address']}）"
        if poi["rating"] != "-":
            line += f" 评分{poi['rating']}"
        if poi["cost"] != "-":
            line += f" 人均¥{poi['cost']}"
        lines.append(line)
    return "\n".join(lines)


@tool
def plan_route(origin: str, destination: str, city: str) -> str:
    """规划两个地点之间的交通路线，提供驾车和公共交通两种方案。

    当需要了解景点之间的距离和交通方式时调用此工具，
    以便优化游览顺序、估算交通时间和费用。

    Args:
        origin: 出发地名称，如"西湖"
        destination: 目的地名称，如"灵隐寺"
        city: 所在城市名称

    Returns:
        交通路线信息，包含距离、驾车时间、公交时间和费用
    """
    orig_coord = geocode(origin, city)
    dest_coord = geocode(destination, city)

    if not orig_coord:
        return f"无法定位出发地：{origin}"
    if not dest_coord:
        return f"无法定位目的地：{destination}"

    straight = haversine(orig_coord[0], orig_coord[1], dest_coord[0], dest_coord[1])

    parts = [f"{origin} → {destination}（直线距离{straight:.1f}km）"]

    drive = fetch_driving_route(orig_coord, dest_coord)
    if drive:
        parts.append(f"  驾车约{drive['duration_min']}分钟（{drive['distance_km']}km）")

    transit = fetch_transit_route(orig_coord, dest_coord, city)
    if transit:
        parts.append(f"  公交约{transit['duration_min']}分钟，费用¥{transit['cost']}")

    if not drive and not transit:
        parts.append("  路线详情获取失败")

    return "\n".join(parts)


@tool
def search_hotels_nearby(location: str, city: str, radius: int = 3000) -> str:
    """搜索指定地点附近的酒店住宿。

    当需要为用户推荐住宿时调用此工具。
    会搜索指定地点周边范围内的酒店，返回名称、地址、评分和参考价格。

    Args:
        location: 中心位置名称，如"西湖"、"灵隐寺"，或"市中心"
        city: 所在城市名称
        radius: 搜索半径（米），默认3000米

    Returns:
        酒店列表，包含名称、地址、评分和参考价格
    """
    if location in ("市中心", "中心", "城区", ""):
        coord = geocode(city, city)
    else:
        coord = geocode(location, city)

    if not coord:
        # 回退到关键词搜索
        hotels = search_hotels_by_keyword(city, location)
    else:
        hotels = search_hotels(coord, city, radius)

    if not hotels:
        return f"未找到{city}的酒店信息"

    lines = [f"{location or city}附近推荐住宿："]
    for i, h in enumerate(hotels, 1):
        line = f"  {i}. {h['name']}（{h['address']}）"
        if h["rating"] != "-":
            line += f" 评分{h['rating']}"
        if h["cost"] != "-":
            line += f" 参考价¥{h['cost']}"
        lines.append(line)
    return "\n".join(lines)


@tool
def geocode_address(address: str, city: str = "") -> str:
    """将地址或景点名称转换为经纬度坐标和详细地址。

    当需要确定某个地点的具体位置时调用此工具。

    Args:
        address: 地址或景点名称，如"西湖"、"北京故宫"
        city: 所在城市（可选，提高定位精度）

    Returns:
        经纬度坐标和格式化地址
    """
    coord = geocode(address, city)
    if not coord:
        return f"无法定位：{address}"
    lng, lat = coord
    return f"{address}的位置：经度{lng}, 纬度{lat}"


# 导出所有工具的列表，供 Agent 注册使用
ALL_TOOLS = [
    query_weather,
    search_attractions,
    plan_route,
    search_hotels_nearby,
    geocode_address,
]
