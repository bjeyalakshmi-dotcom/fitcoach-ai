"""
Orchestrator — routes events to the right agents and coordinates responses.
This is the single entry point called by all API routes.
"""
import json
import asyncio
from datetime import date

import database as db
from agents.planner        import PlannerAgent
from agents.nutrition      import NutritionAgent
from agents.progress_tracker import ProgressTrackerAgent
from agents.coach          import CoachAgent

planner  = PlannerAgent()
nutrition = NutritionAgent()
tracker  = ProgressTrackerAgent()
coach    = CoachAgent()


def onboard_user(user: dict) -> dict:
    """
    Called once when a new user is created.
    Generates initial workout + meal plan.
    """
    db.save_user({
        "id":           user["id"],
        "name":         user["name"],
        "age":          user["age"],
        "weight_kg":    user["weight_kg"],
        "height_cm":    user["height_cm"],
        "goal":         user["goal"],
        "activity":     user["activity"],
        "restrictions": json.dumps(user.get("restrictions", [])),
    })

    # Generate plans in parallel (independent tasks)
    workout_plan = planner.generate(user)
    meal_plan    = nutrition.generate(user)

    combined = {
        "week_start": str(date.today()),
        "workout":    workout_plan,
        "meals":      meal_plan.get("meals", {}),
        "calories":   meal_plan.get("calories", 2000),
        "protein_g":  meal_plan.get("protein_g", 120),
        "carbs_g":    meal_plan.get("carbs_g", 200),
        "fat_g":      meal_plan.get("fat_g", 60),
    }
    db.save_plan(user["id"], combined)

    coach.send_plan_update(
        user["id"],
        f"Welcome {user['name']}! Your personalised plan is ready."
    )

    return combined


def process_health_sync(user_id: str, signal: dict) -> dict:
    """
    Called hourly when phone SDK syncs health data.
    Runs Progress Tracker → may trigger Planner/Nutrition/Coach updates.
    """
    db.save_health_signal(user_id, signal)

    user = db.get_user(user_id)
    if not user:
        return {"error": "user not found"}

    logs         = db.get_recent_logs(user_id, days=7)
    current_plan = db.get_latest_plan(user_id) or {}
    actions      = []

    analysis = tracker.analyse(user, logs, current_plan)

    # Planner update
    if analysis.get("needs_plan_update"):
        reason = analysis.get("plan_update_reason", "progress detected")
        injury_notes = analysis.get("health_flag")
        new_workout  = planner.adapt(user, current_plan.get("workout", {}), reason)

        updated = {**current_plan,
                   "week_start": str(date.today()),
                   "workout":    new_workout}
        if isinstance(current_plan.get("meals"), str):
            updated["meals"] = json.loads(current_plan["meals"])
        db.save_plan(user_id, updated)
        coach.send_plan_update(user_id, reason)
        actions.append("plan_updated")

    # Nutrition update
    if analysis.get("needs_nutrition_update"):
        reason = analysis.get("nutrition_update_reason", "dietary adjustment needed")
        meal_plan = nutrition.adjust_for_recovery(current_plan, reason)
        updated = {**current_plan,
                   "week_start": str(date.today()),
                   "meals":      meal_plan.get("meals", {}),
                   "calories":   meal_plan.get("calories", current_plan.get("calories")),
                   "protein_g":  meal_plan.get("protein_g", current_plan.get("protein_g")),
                   "carbs_g":    meal_plan.get("carbs_g",   current_plan.get("carbs_g")),
                   "fat_g":      meal_plan.get("fat_g",     current_plan.get("fat_g"))}
        db.save_plan(user_id, updated)
        actions.append("nutrition_adjusted")

    # Health flag — LOW autonomy: send alert but do NOT change plan
    if analysis.get("health_flag"):
        coach.send_health_alert(user_id, analysis["health_flag"])
        actions.append("health_alert_sent")

    # Coaching nudge
    elif analysis.get("nudge_message"):
        coach.send_nudge(user_id, analysis["nudge_message"])
        actions.append("nudge_sent")

    return {
        "analysis_summary": analysis.get("summary"),
        "actions_taken":    actions,
        "health_flag":      analysis.get("health_flag"),
        "plan_updated":     "plan_updated" in actions,
    }


def process_workout_log(user_id: str, log: dict) -> dict:
    """
    Called when a user logs a completed (or skipped) workout.
    """
    db.save_workout_log(user_id, log)
    actions = []

    if log.get("skipped") and log.get("skip_reason"):
        reason = log["skip_reason"].lower()
        user   = db.get_user(user_id)
        plan   = db.get_latest_plan(user_id) or {}

        # Detect injury keywords → health alert (LOW autonomy)
        injury_keywords = ["pain", "hurt", "injury", "injured", "strain", "sprain", "knee", "back", "shoulder"]
        if any(kw in reason for kw in injury_keywords):
            coach.send_health_alert(user_id, f"User skipped workout due to: {log['skip_reason']}")
            actions.append("health_alert_sent")

            # Auto-adapt plan to low-impact for safety (HIGH autonomy)
            new_workout = planner.adapt(user, plan.get("workout", {}),
                                        f"Injury reported: {log['skip_reason']}. Switch to low-impact.")
            updated = {**plan, "week_start": str(date.today()), "workout": new_workout}
            db.save_plan(user_id, updated)
            actions.append("plan_adapted_for_injury")
        else:
            coach.send_nudge(user_id, f"Workout skipped: {log['skip_reason']}. Let's get back on track!")
            actions.append("nudge_sent")

    return {"logged": True, "actions_taken": actions}


def process_meal_log(user_id: str, log: dict) -> dict:
    """Called when a user logs a meal."""
    db.save_meal_log(user_id, log)
    plan = db.get_latest_plan(user_id) or {}
    target_kcal = plan.get("calories", 2000)
    logged_kcal = log.get("total_kcal", 0)

    actions = []
    # If under by >500 kcal, send a nudge
    if target_kcal - logged_kcal > 500:
        coach.send_nudge(
            user_id,
            f"You're {int(target_kcal - logged_kcal)} kcal below target. Add a protein-rich snack!"
        )
        actions.append("low_calorie_nudge_sent")

    return {"logged": True, "actions_taken": actions}


def chat_with_coach(user_id: str, message: str) -> str:
    """Direct conversational interface with Coach Agent."""
    user = db.get_user(user_id) or {}
    plan = db.get_latest_plan(user_id) or {}
    logs = db.get_recent_logs(user_id, days=3)
    context = {"user": user, "current_plan_summary": {
        "calories": plan.get("calories"),
        "protein_g": plan.get("protein_g"),
    }, "recent_workout_count": len(logs.get("workouts", []))}
    return coach.chat(user_id, message, context)
