"""Agent 工具单元测试。"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from services.tools import query_weather, search_attractions, plan_route, search_hotels_nearby, geocode_address


class TestQueryWeather:
    """天气查询工具测试。"""

    @patch("services.tools.fetch_weather")
    def test_returns_weather_text(self, mock_fetch):
        mock_fetch.return_value = "杭州未来天气：\n  2025-05-10：晴转多云，25°C/18°C"
        result = query_weather.invoke({"city": "杭州", "start_date": "2025-05-10", "end_date": "2025-05-10"})
        assert "杭州" in result
        mock_fetch.assert_called_once_with("杭州", "2025-05-10", "2025-05-10")

    @patch("services.tools.fetch_weather")
    def test_handles_empty_dates(self, mock_fetch):
        mock_fetch.return_value = "北京未来天气：..."
        result = query_weather.invoke({"city": "北京"})
        mock_fetch.assert_called_once_with("北京", "", "")


class TestSearchAttractions:
    """景点搜索工具测试。"""

    @patch("services.tools.search_poi")
    def test_returns_attractions_list(self, mock_search):
        mock_search.return_value = [
            {"name": "西湖", "address": "杭州市西湖区", "type": "风景名胜", "rating": "4.8", "cost": "0"},
        ]
        result = search_attractions.invoke({"city": "杭州", "keyword": "西湖", "poi_type": "景点"})
        assert "西湖" in result
        assert "评分4.8" in result

    @patch("services.tools.search_poi")
    def test_handles_empty_results(self, mock_search):
        mock_search.return_value = []
        result = search_attractions.invoke({"city": "未知城市", "keyword": "景点"})
        assert "未找到" in result


class TestPlanRoute:
    """路线规划工具测试。"""

    @patch("services.tools.fetch_transit_route")
    @patch("services.tools.fetch_driving_route")
    @patch("services.tools.geocode")
    def test_returns_route_info(self, mock_geocode, mock_drive, mock_transit):
        mock_geocode.side_effect = [(120.1, 30.2), (120.0, 30.3)]
        mock_drive.return_value = {"distance_km": 5.2, "duration_min": 15}
        mock_transit.return_value = {"duration_min": 25, "cost": "3"}

        result = plan_route.invoke({"origin": "西湖", "destination": "灵隐寺", "city": "杭州"})
        assert "西湖 → 灵隐寺" in result
        assert "驾车约15分钟" in result
        assert "公交约25分钟" in result

    @patch("services.tools.geocode")
    def test_handles_unknown_location(self, mock_geocode):
        mock_geocode.return_value = None
        result = plan_route.invoke({"origin": "不存在的地点", "destination": "灵隐寺", "city": "杭州"})
        assert "无法定位" in result


class TestGeocodeAddress:
    """地理编码工具测试。"""

    @patch("services.tools.geocode")
    def test_returns_coordinates(self, mock_geocode):
        mock_geocode.return_value = (120.1551, 30.2741)
        result = geocode_address.invoke({"address": "西湖", "city": "杭州"})
        assert "120.1551" in result
        assert "30.2741" in result

    @patch("services.tools.geocode")
    def test_handles_not_found(self, mock_geocode):
        mock_geocode.return_value = None
        result = geocode_address.invoke({"address": "不存在的地方"})
        assert "无法定位" in result
