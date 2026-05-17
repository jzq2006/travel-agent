from config import AMAP_KEY
from services.api_client import safe_get


def fetch_weather(city_name: str, start_date: str = "", end_date: str = "") -> str:
    """查询目的地天气预报，返回格式化文本。"""
    if not AMAP_KEY:
        return "（未配置高德地图API密钥，暂无实时天气数据）"

    try:
        key = AMAP_KEY.strip()

        # 1. 通过地理编码获取城市 adcode
        geo_resp = safe_get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={"address": city_name, "key": key},
        )
        if geo_resp is None:
            return "（地理编码服务暂时不可用，请稍后重试）"
        if not geo_resp.text:
            return "（地理编码接口返回为空，请检查API Key是否正确）"
        geo_data = geo_resp.json()
        if geo_data.get("status") != "1" or not geo_data.get("geocodes"):
            return f"（未找到{city_name}的天气数据，接口返回: {geo_data}）"

        adcode = geo_data["geocodes"][0].get("adcode", "")

        # 2. 查询天气预报（extensions=all 返回预报）
        fc_resp = safe_get(
            "https://restapi.amap.com/v3/weather/weatherInfo",
            params={"city": adcode, "key": key, "extensions": "all"},
        )
        if fc_resp is None:
            return "（天气服务暂时不可用，请稍后重试）"
        if not fc_resp.text:
            return "（天气接口返回为空，请检查API Key是否有天气查询权限）"
        fc_data = fc_resp.json()
        if fc_data.get("status") != "1" or not fc_data.get("forecasts"):
            return f"（天气预报数据暂不可用，接口返回: {fc_data}）"

        casts = fc_data["forecasts"][0].get("casts", [])
        city_display = fc_data["forecasts"][0].get("city", city_name)

        if start_date and end_date:
            casts = [
                c for c in casts
                if start_date <= c["date"] <= end_date
            ]

        if not casts:
            return "（出行日期超出预报范围，暂无精确天气数据）"

        lines = []
        for c in casts:
            day_w = c.get("dayweather", "")
            night_w = c.get("nightweather", "")
            rain_tags = ["小雨", "中雨", "大雨", "暴雨", "雷阵雨", "阵雨", "雨"]
            is_rain = any(t in (day_w + night_w) for t in rain_tags)

            high_temp = c.get("daytemp", "?")
            low_temp = c.get("nighttemp", "?")
            wind = f"{c.get('daywind', '')}风{c.get('daypower', '')}级"

            line = (
                f"  {c['date']}：{day_w}转{night_w}，"
                f"{high_temp}°C/{low_temp}°C，{wind}"
            )
            if is_rain:
                line += " ⚠️有雨，建议安排室内景点"
            if int(high_temp or 0) >= 35:
                line += " ⚠️高温天气，注意防晒"
            lines.append(line)

        header = f"{city_display}未来天气（{casts[0]['date']}至{casts[-1]['date']}）：\n"
        return header + "\n".join(lines)

    except Exception as e:
        return f"（天气数据获取失败: {e}）"
