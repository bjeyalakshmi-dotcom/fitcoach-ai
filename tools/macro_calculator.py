"""
Deterministic TDEE and macro calculator — no LLM needed, pure maths.
"""


ACTIVITY_MULTIPLIERS = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}

GOAL_ADJUSTMENTS = {
    "lose_weight":  -400,   # kcal deficit
    "gain_muscle":  +300,   # kcal surplus
    "maintain":      0,
}


def calculate_tdee(weight_kg: float, height_cm: float, age: int,
                   activity: str = "moderate") -> float:
    """Mifflin-St Jeor BMR × activity multiplier."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5  # male baseline
    return round(bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.55), 1)


def calculate_macros(weight_kg: float, height_cm: float, age: int,
                     activity: str, goal: str) -> dict:
    tdee = calculate_tdee(weight_kg, height_cm, age, activity)
    target_kcal = max(1200, tdee + GOAL_ADJUSTMENTS.get(goal, 0))

    # Protein: 2g per kg bodyweight; fat: 25% of kcal; rest = carbs
    protein_g  = round(weight_kg * 2, 1)
    fat_g      = round(target_kcal * 0.25 / 9, 1)
    carbs_g    = round((target_kcal - protein_g * 4 - fat_g * 9) / 4, 1)

    return {
        "calories":  round(target_kcal, 1),
        "protein_g": protein_g,
        "fat_g":     fat_g,
        "carbs_g":   max(0, carbs_g),
    }


# Tool schema for OpenAI function calling
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate_macros",
        "description": "Calculate daily calorie target and macronutrient split (protein, fat, carbs) for a user.",
        "parameters": {
            "type": "object",
            "properties": {
                "weight_kg":  {"type": "number"},
                "height_cm":  {"type": "number"},
                "age":        {"type": "integer"},
                "activity":   {"type": "string", "enum": list(ACTIVITY_MULTIPLIERS)},
                "goal":       {"type": "string", "enum": list(GOAL_ADJUSTMENTS)},
            },
            "required": ["weight_kg", "height_cm", "age", "activity", "goal"],
        },
    },
}


def run(weight_kg, height_cm, age, activity, goal):
    return calculate_macros(weight_kg, height_cm, age, activity, goal)
