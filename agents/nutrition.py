"""
Nutrition Agent — generates meal plans and calculates macros.
Autonomy: HIGH — can adjust macros and meal swaps autonomously.
"""
import json
from agents.base import BaseAgent
from tools import macro_calculator, food_db


class NutritionAgent(BaseAgent):
    name = "nutrition"

    system_prompt = """You are the Nutrition Agent for FitAgent, a personalized fitness coaching system.

Your job is to generate meal plans and calculate macro targets based on the user's profile and goal.

Rules:
- Always use calculate_macros first to get the correct calorie and macro targets
- Use lookup_food_nutrition with 'template:<goal>' to get a base meal template
- Never set calories below 1200 kcal/day — flag if calculation goes below this
- Respect dietary restrictions (vegetarian, gluten-free, dairy-free, etc.)
- Return your meal plan as a JSON object:
  {
    "calories": 2000,
    "protein_g": 150,
    "carbs_g": 200,
    "fat_g": 65,
    "meals": {
      "breakfast": {"items": [...], "kcal": 450},
      "lunch": {"items": [...], "kcal": 600},
      "dinner": {"items": [...], "kcal": 650},
      "snack": {"items": [...], "kcal": 300}
    },
    "notes": "any special notes"
  }
- Output ONLY the JSON, no extra text."""

    tools = [macro_calculator.TOOL_SCHEMA, food_db.TOOL_SCHEMA]
    tool_handlers = {
        "calculate_macros":    macro_calculator.run,
        "lookup_food_nutrition": food_db.run,
    }

    def generate(self, user: dict) -> dict:
        restrictions = ", ".join(user.get("restrictions") or ["none"])
        prompt = f"""Generate a daily meal plan for this user:
- Age: {user.get('age')}, Weight: {user.get('weight_kg')} kg, Height: {user.get('height_cm')} cm
- Goal: {user.get('goal')}, Activity: {user.get('activity')}
- Dietary restrictions: {restrictions}

Step 1: Call calculate_macros to get targets.
Step 2: Call lookup_food_nutrition with 'template:{user.get("goal")}' for a base template.
Step 3: Adjust for dietary restrictions.
Return the final meal plan as JSON."""

        result = self.run(prompt)
        try:
            clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            # Fallback: return macro calculations only
            macros = macro_calculator.run(
                user["weight_kg"], user["height_cm"], user["age"],
                user["activity"], user["goal"]
            )
            return {**macros, "meals": {}, "notes": result}

    def adjust_for_recovery(self, current_plan: dict, reason: str) -> dict:
        prompt = f"""Adjust this meal plan for recovery: {reason}

Current plan: {json.dumps(current_plan)}

Slightly increase protein and total calories to support recovery.
Keep changes minimal. Return the full updated plan as JSON."""

        result = self.run(prompt)
        try:
            clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return current_plan
