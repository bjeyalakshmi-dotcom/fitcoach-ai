"""
Planner Agent — generates and adapts weekly workout plans.
Autonomy: HIGH — can restructure exercises autonomously within safe limits.
"""
import json
from datetime import date
from agents.base import BaseAgent
from tools import exercise_db


class PlannerAgent(BaseAgent):
    name = "planner"

    system_prompt = """You are the Planner Agent for FitAgent, a personalized fitness coaching system.

Your job is to generate and update weekly workout plans based on the user's profile, goals, and progress.

Rules:
- Use the lookup_exercises tool to get exercises for each muscle group
- Create a 5-day plan (Mon-Fri) with rest on weekends
- For users with reported injuries, ALWAYS use low_impact or bodyweight exercises for affected areas
- Never increase training load by more than 20% from the previous week
- Return the plan as a valid JSON object with this structure:
  {
    "week_start": "YYYY-MM-DD",
    "days": {
      "Monday": [{"muscle_group": "...", "exercises": [...]}],
      ...
    },
    "notes": "any special instructions"
  }
- Output ONLY the JSON, no extra text."""

    tools = [exercise_db.TOOL_SCHEMA]
    tool_handlers = {"lookup_exercises": exercise_db.run}

    def generate(self, user: dict, injury_notes: str = None) -> dict:
        prompt = f"""Generate a weekly workout plan for this user:
- Goal: {user.get('goal')}
- Activity level: {user.get('activity')}
- Weight: {user.get('weight_kg')} kg
- Injury/restriction notes: {injury_notes or 'None'}

Use lookup_exercises for each muscle group needed.
Monday = Chest, Tuesday = Back, Wednesday = Cardio,
Thursday = Legs, Friday = Shoulders+Arms."""

        result = self.run(prompt)
        try:
            # Strip markdown code fences if present
            clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return {"week_start": str(date.today()), "raw": result, "days": {}}

    def adapt(self, user: dict, current_plan: dict, reason: str) -> dict:
        prompt = f"""Adapt this workout plan due to: {reason}

Current plan: {json.dumps(current_plan)}
User goal: {user.get('goal')}
User weight: {user.get('weight_kg')} kg

Make the minimum necessary changes. Use lookup_exercises only for changed muscle groups.
Return the full updated plan as JSON."""

        result = self.run(prompt)
        try:
            clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return current_plan
