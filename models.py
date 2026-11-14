from pydantic import BaseModel, Field
from typing import Optional, List


class UserProfile(BaseModel):
    id: str
    name: str
    age: int
    weight_kg: float
    height_cm: float
    goal: str = "lose_weight"          # lose_weight | gain_muscle | maintain
    activity: str = "moderate"          # sedentary | light | moderate | active | very_active
    restrictions: List[str] = Field(default_factory=list)


class HealthSyncData(BaseModel):
    steps: Optional[int] = None
    heart_rate_bpm: Optional[float] = None
    sleep_hours: Optional[float] = None
    calories_burned: Optional[float] = None


class WorkoutLog(BaseModel):
    exercises: List[str] = Field(default_factory=list)
    duration_min: int = 0
    skipped: bool = False
    skip_reason: Optional[str] = None


class MealLog(BaseModel):
    meals: List[str] = Field(default_factory=list)
    total_kcal: float
    protein_g: float = 0.0


class ChatMessage(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str
    actions_taken: List[str] = Field(default_factory=list)
    plan_updated: bool = False
    health_flag: Optional[str] = None
