"""
FitAgent — Personalized Exercise & Diet Planning System
FastAPI backend  |  run: uvicorn main:app --reload
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

import database as db
from models import UserProfile, HealthSyncData, WorkoutLog, MealLog, ChatMessage
from agents import orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    print("✓ Database initialised")
    yield


app = FastAPI(
    title="FitAgent API",
    description="Agentic AI for personalized exercise and diet planning",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── users ─────────────────────────────────────────────────────────────────────
@app.post("/users", summary="Create user and generate initial plan")
def create_user(profile: UserProfile):
    if db.get_user(profile.id):
        raise HTTPException(400, "User already exists. Use PATCH /users/{id} to update.")

    plan = orchestrator.onboard_user(profile.model_dump())
    return {
        "user_id": profile.id,
        "message": f"Welcome {profile.name}! Your plan is ready.",
        "plan":    plan,
    }


@app.get("/users/{user_id}", summary="Get user profile")
def get_user(user_id: str):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


# ── plan ──────────────────────────────────────────────────────────────────────
@app.get("/users/{user_id}/plan", summary="Get current workout + meal plan")
def get_plan(user_id: str):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    plan = db.get_latest_plan(user_id)
    if not plan:
        raise HTTPException(404, "No plan found — create user first")

    plan = dict(plan)
    for field in ("workout", "meals"):
        if isinstance(plan.get(field), str):
            try:
                plan[field] = json.loads(plan[field])
            except Exception:
                pass
    return plan


# ── health sync ───────────────────────────────────────────────────────────────
@app.post("/users/{user_id}/health-sync",
          summary="Sync health data from phone (HealthKit / Health Connect)")
def health_sync(user_id: str, data: HealthSyncData):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    result = orchestrator.process_health_sync(user_id, data.model_dump())
    return result


# ── logging ───────────────────────────────────────────────────────────────────
@app.post("/users/{user_id}/log-workout", summary="Log a completed or skipped workout")
def log_workout(user_id: str, log: WorkoutLog):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    result = orchestrator.process_workout_log(user_id, log.model_dump())
    return result


@app.post("/users/{user_id}/log-meal", summary="Log a meal")
def log_meal(user_id: str, log: MealLog):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    result = orchestrator.process_meal_log(user_id, log.model_dump())
    return result


# ── progress ──────────────────────────────────────────────────────────────────
@app.get("/users/{user_id}/progress", summary="Get recent logs and health signals")
def get_progress(user_id: str, days: int = 7):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    logs = db.get_recent_logs(user_id, days=days)
    return logs


@app.get("/users/{user_id}/notifications", summary="Get sent notifications")
def get_notifications(user_id: str):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id=? ORDER BY sent_at DESC LIMIT 20",
            (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── chat ──────────────────────────────────────────────────────────────────────
@app.post("/users/{user_id}/chat", summary="Chat with your AI fitness coach")
def chat(user_id: str, msg: ChatMessage):
    if not db.get_user(user_id):
        raise HTTPException(404, "User not found")

    reply = orchestrator.chat_with_coach(user_id, msg.message)
    return {"reply": reply}


# ── health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "FitAgent API"}
