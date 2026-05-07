import requests as http

from config import QWEATHER_KEY


def fetch_weather(city_name: str, start_date: str = "", end_date: str = "") -> str:
    """查询目的地未来7天天气预报，返回格式化文本。"""
    if not QWEATHER_KEY:
        return "（未配置天气API密钥，暂无实时天气数据）"

    try:
        geo_resp = http.get(
            "https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city_name, "key": QWEATHER_KEY, "lang": "zh"},
            timeout=8,
        )
        geo_data = geo_resp.json()
        if geo_data.get("code") != "200" or not geo_data.get("location"):
            return f"（未找到{city_name}的天气数据）"

        loc = geo_data["location"][0]

        fc_resp = http.get(
            "https://devapi.qweather.com/v7/weather/7d",
            params={"location": loc["id"], "key": QWEATHER_KEY, "lang": "zh"},
            timeout=8,
        )
        fc_data = fc_resp.json()
        if fc_data.get("code") != "200" or not fc_data.get("daily"):
            return "（天气预报数据暂不可用）"

        daily_list = fc_data["daily"]
        if start_date and end_date:
            daily_list = [
                d for d in daily_list
                if start_date <= d["fxDate"] <= end_date
            ]

        if not daily_list:
            return "（出行日期超出7天预报范围，暂无精确天气数据）"

        lines = []
        for d in daily_list:
            rain_tags = ["小雨", "中雨", "大雨", "暴雨", "雷阵雨", "阵雨", "雨"]
            is_rain = any(
                t in (d.get("textDay", "") + d.get("textNight", "")) for t in rain_tags
            )
            high_temp = d.get("tempMax", "?")
            low_temp = d.get("tempMin", "?")
            wind = f"{d.get('windDirDay', '')}{d.get('windScaleDay', '')}级"
            hum = d.get("humidity", "?")

            line = (
                f"  {d['fxDate']}：{d['textDay']}转{d['textNight']}，"
                f"{high_temp}°C/{low_temp}°C，{wind}，湿度{hum}%"
            )
            if is_rain:
                line += " ⚠️有雨，建议安排室内景点"
            if int(high_temp or 0) >= 35:
                line += " ⚠️高温天气，注意防晒"
            lines.append(line)

        header = f"{loc['name']}未来天气（{daily_list[0]['fxDate']}至{daily_list[-1]['fxDate']}）：\n"
        return header + "\n".join(lines)

    except Exception as e:
        return f"（天气数据获取失败: {e}）"
