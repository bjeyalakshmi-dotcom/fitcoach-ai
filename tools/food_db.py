"""
Food / nutrition database tool.
Uses mock data; swap for Nutritionix or USDA FoodData Central API in production.
"""

FOODS = {
    "chicken breast (100g)":   {"kcal": 165, "protein_g": 31, "carbs_g": 0,  "fat_g": 3.6},
    "brown rice (100g)":       {"kcal": 216, "protein_g": 5,  "carbs_g": 45, "fat_g": 1.8},
    "oats (100g)":             {"kcal": 389, "protein_g": 17, "carbs_g": 66, "fat_g": 7},
    "eggs (1 whole)":          {"kcal": 72,  "protein_g": 6,  "carbs_g": 0.4,"fat_g": 5},
    "greek yogurt (200g)":     {"kcal": 118, "protein_g": 20, "carbs_g": 9,  "fat_g": 0.7},
    "salmon (100g)":           {"kcal": 208, "protein_g": 20, "carbs_g": 0,  "fat_g": 13},
    "sweet potato (100g)":     {"kcal": 86,  "protein_g": 1.6,"carbs_g": 20, "fat_g": 0.1},
    "broccoli (100g)":         {"kcal": 34,  "protein_g": 2.8,"carbs_g": 7,  "fat_g": 0.4},
    "almonds (30g)":           {"kcal": 174, "protein_g": 6,  "carbs_g": 6,  "fat_g": 15},
    "banana (1 medium)":       {"kcal": 105, "protein_g": 1.3,"carbs_g": 27, "fat_g": 0.4},
    "whey protein shake (1)":  {"kcal": 120, "protein_g": 25, "carbs_g": 3,  "fat_g": 1},
    "whole milk (250ml)":      {"kcal": 150, "protein_g": 8,  "carbs_g": 12, "fat_g": 8},
    "lentils cooked (100g)":   {"kcal": 116, "protein_g": 9,  "carbs_g": 20, "fat_g": 0.4},
    "avocado (half)":          {"kcal": 120, "protein_g": 1.5,"carbs_g": 6,  "fat_g": 11},
    "cottage cheese (100g)":   {"kcal": 98,  "protein_g": 11, "carbs_g": 3.4,"fat_g": 4.3},
}

# Meal templates by goal
MEAL_TEMPLATES = {
    "lose_weight": {
        "breakfast": ["oats (100g)", "greek yogurt (200g)", "banana (1 medium)"],
        "lunch":     ["chicken breast (100g)", "broccoli (100g)", "sweet potato (100g)"],
        "dinner":    ["salmon (100g)", "broccoli (100g)", "brown rice (100g)"],
        "snack":     ["almonds (30g)", "cottage cheese (100g)"],
    },
    "gain_muscle": {
        "breakfast": ["oats (100g)", "eggs (1 whole)", "whole milk (250ml)", "banana (1 medium)"],
        "lunch":     ["chicken breast (100g)", "brown rice (100g)", "avocado (half)"],
        "dinner":    ["salmon (100g)", "sweet potato (100g)", "broccoli (100g)"],
        "snack":     ["whey protein shake (1)", "almonds (30g)"],
    },
    "maintain": {
        "breakfast": ["oats (100g)", "greek yogurt (200g)", "eggs (1 whole)"],
        "lunch":     ["chicken breast (100g)", "brown rice (100g)", "broccoli (100g)"],
        "dinner":    ["lentils cooked (100g)", "sweet potato (100g)", "broccoli (100g)"],
        "snack":     ["almonds (30g)", "banana (1 medium)"],
    },
}

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "lookup_food_nutrition",
        "description": "Look up nutritional info for a food item or get a full meal template for a goal.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Food name (e.g. 'chicken breast (100g)') OR 'template:<goal>' for a full day meal plan.",
                },
            },
            "required": ["query"],
        },
    },
}


def run(query: str):
    if query.startswith("template:"):
        goal = query.split(":", 1)[1].strip()
        template = MEAL_TEMPLATES.get(goal, MEAL_TEMPLATES["maintain"])
        result = {}
        for meal, items in template.items():
            totals = {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
            for item in items:
                n = FOODS.get(item, {})
                for k in totals:
                    totals[k] += n.get(k, 0)
            result[meal] = {"items": items, "totals": totals}
        return result

    return FOODS.get(query.lower(), {"error": f"Food '{query}' not found in database."})
