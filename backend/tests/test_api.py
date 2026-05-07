"""API 端点集成测试。"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAuthEndpoints:
    """认证端点测试。"""

    def test_register_success(self, client):
        resp = client.post("/api/register", json={
            "username": "newuser",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["role"] == "user"

    def test_register_duplicate_username(self, client):
        client.post("/api/register", json={"username": "dup", "password": "123456"})
        resp = client.post("/api/register", json={"username": "dup", "password": "123456"})
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]

    def test_register_short_password(self, client):
        resp = client.post("/api/register", json={"username": "user1", "password": "123"})
        assert resp.status_code == 400

    def test_login_success(self, client):
        client.post("/api/register", json={"username": "loginuser", "password": "123456"})
        resp = client.post("/api/login", json={"username": "loginuser", "password": "123456"})
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/api/register", json={"username": "wrongpw", "password": "123456"})
        resp = client.post("/api/login", json={"username": "wrongpw", "password": "wrong"})
        assert resp.status_code == 401


class TestBookingEndpoints:
    """预订端点测试。"""

    def test_create_booking(self, client, auth_headers):
        resp = client.post("/api/booking", json={
            "dest": "杭州",
            "name": "张三",
            "phone": "13800138000",
            "date": "2025-05-10",
            "people": 2,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert "booking_id" in resp.json()

    def test_create_booking_invalid_phone(self, client, auth_headers):
        resp = client.post("/api/booking", json={
            "dest": "杭州",
            "name": "张三",
            "phone": "123",
            "date": "2025-05-10",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_list_bookings_requires_auth(self, client):
        resp = client.get("/api/bookings")
        assert resp.status_code == 401

    def test_list_bookings_returns_own_only(self, client, auth_headers):
        # 创建一个预订
        client.post("/api/booking", json={
            "dest": "杭州",
            "name": "张三",
            "phone": "13800138000",
            "date": "2025-05-10",
        }, headers=auth_headers)

        resp = client.get("/api/bookings", headers=auth_headers)
        assert resp.status_code == 200
        bookings = resp.json()["bookings"]
        assert len(bookings) >= 1


class TestPreferences:
    """用户偏好端点测试。"""

    def test_get_default_preferences(self, client, auth_headers):
        resp = client.get("/api/preferences", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["budget_level"] == "medium"

    def test_save_and_get_preferences(self, client, auth_headers):
        resp = client.post("/api/preferences", json={
            "travel_style": "adventure",
            "budget_level": "low",
            "dietary_restrictions": "不吃辣",
            "favorite_destinations": "杭州,成都",
            "notes": "喜欢户外活动",
        }, headers=auth_headers)
        assert resp.status_code == 200

        resp = client.get("/api/preferences", headers=auth_headers)
        data = resp.json()
        assert data["travel_style"] == "adventure"
        assert data["dietary_restrictions"] == "不吃辣"


class TestMeEndpoint:
    """用户信息端点测试。"""

    def test_me_with_auth(self, client, auth_headers):
        resp = client.get("/api/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_me_without_auth(self, client):
        resp = client.get("/api/me")
        assert resp.status_code == 401


class TestSubscribe:
    """订阅端点测试。"""

    def test_subscribe_success(self, client):
        resp = client.post("/api/newsletter/subscribe", json={"email": "test@example.com"})
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_subscribe_invalid_email(self, client):
        resp = client.post("/api/newsletter/subscribe", json={"email": "invalid"})
        assert resp.status_code == 400

    def test_subscribe_duplicate(self, client):
        client.post("/api/newsletter/subscribe", json={"email": "dup@example.com"})
        resp = client.post("/api/newsletter/subscribe", json={"email": "dup@example.com"})
        assert resp.status_code == 200
        assert "已订阅" in resp.json()["message"]
