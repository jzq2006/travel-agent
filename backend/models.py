from pydantic import BaseModel
from typing import Optional


class TravelPlanRequest(BaseModel):
    destination: str
    travelType: str
    budget: int
    duration: int
    peopleCount: int
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    dietaryRequirements: Optional[str] = ""
    desiredAttractions: Optional[str] = ""
    selectedPreferences: Optional[list[str]] = []
    remarks: Optional[str] = ""


class ChatRequest(BaseModel):
    destination: str
    message: str
    history: list[dict] = []
    sessionId: Optional[str] = ""


class PlanChatRequest(BaseModel):
        destination: str
        message: str
        plan_text: str  # 前端传来的行程方案全文
        history: list[dict] = []


class BookingRequest(BaseModel):
    dest: str
    name: str
    phone: str
    date: str
    people: int = 2
    package: Optional[str] = ""
    remark: Optional[str] = ""


class SubscribeRequest(BaseModel):
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class UserPreferencesRequest(BaseModel):
    travel_style: Optional[str] = ""
    budget_level: Optional[str] = "medium"
    dietary_restrictions: Optional[str] = ""
    favorite_destinations: Optional[str] = ""
    notes: Optional[str] = ""
