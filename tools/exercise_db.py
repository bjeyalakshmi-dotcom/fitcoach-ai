"""
Exercise database tool — returns exercises by muscle group and equipment.
Uses mock data; swap for a real API (ExerciseDB, Wger) in production.
"""

EXERCISES = {
    "legs": {
        "high_impact": [
            {"name": "Barbell Squat",    "sets": 4, "reps": "8-10", "rest_sec": 90},
            {"name": "Romanian Deadlift","sets": 3, "reps": "10-12","rest_sec": 75},
            {"name": "Box Jump",         "sets": 3, "reps": "8",    "rest_sec": 60},
            {"name": "Leg Press",        "sets": 3, "reps": "12-15","rest_sec": 60},
        ],
        "low_impact": [
            {"name": "Leg Press (light)","sets": 3, "reps": "15",   "rest_sec": 60},
            {"name": "Seated Leg Curl",  "sets": 3, "reps": "12-15","rest_sec": 60},
            {"name": "Wall Sit",         "sets": 3, "reps": "45s",  "rest_sec": 45},
            {"name": "Calf Raise",       "sets": 4, "reps": "20",   "rest_sec": 30},
        ],
        "bodyweight": [
            {"name": "Bodyweight Squat", "sets": 3, "reps": "20",   "rest_sec": 45},
            {"name": "Reverse Lunge",    "sets": 3, "reps": "12ea", "rest_sec": 45},
            {"name": "Glute Bridge",     "sets": 3, "reps": "20",   "rest_sec": 30},
        ],
    },
    "chest": {
        "high_impact": [
            {"name": "Bench Press",      "sets": 4, "reps": "8-10", "rest_sec": 90},
            {"name": "Incline DB Press", "sets": 3, "reps": "10-12","rest_sec": 75},
            {"name": "Cable Fly",        "sets": 3, "reps": "12-15","rest_sec": 60},
        ],
        "low_impact": [
            {"name": "Push-Up",          "sets": 3, "reps": "15-20","rest_sec": 45},
            {"name": "DB Floor Press",   "sets": 3, "reps": "12",   "rest_sec": 60},
        ],
        "bodyweight": [
            {"name": "Push-Up",          "sets": 4, "reps": "15",   "rest_sec": 45},
            {"name": "Wide Push-Up",     "sets": 3, "reps": "12",   "rest_sec": 45},
        ],
    },
    "back": {
        "high_impact": [
            {"name": "Deadlift",         "sets": 4, "reps": "5",    "rest_sec": 120},
            {"name": "Barbell Row",      "sets": 4, "reps": "8-10", "rest_sec": 90},
            {"name": "Pull-Up",          "sets": 3, "reps": "6-10", "rest_sec": 90},
            {"name": "Lat Pulldown",     "sets": 3, "reps": "10-12","rest_sec": 75},
        ],
        "bodyweight": [
            {"name": "Inverted Row",     "sets": 3, "reps": "12",   "rest_sec": 60},
            {"name": "Superman Hold",    "sets": 3, "reps": "12",   "rest_sec": 45},
        ],
    },
    "cardio": {
        "high_impact": [
            {"name": "Running 5km",      "sets": 1, "reps": "5km",  "rest_sec": 0},
            {"name": "HIIT Intervals",   "sets": 8, "reps": "30s",  "rest_sec": 30},
        ],
        "low_impact": [
            {"name": "Brisk Walk 30min", "sets": 1, "reps": "30min","rest_sec": 0},
            {"name": "Cycling 20min",    "sets": 1, "reps": "20min","rest_sec": 0},
            {"name": "Swimming 20min",   "sets": 1, "reps": "20min","rest_sec": 0},
        ],
    },
}

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "lookup_exercises",
        "description": "Look up exercises for a given muscle group and intensity level.",
        "parameters": {
            "type": "object",
            "properties": {
                "muscle_group": {
                    "type": "string",
                    "enum": list(EXERCISES.keys()),
                    "description": "Target muscle group",
                },
                "intensity": {
                    "type": "string",
                    "enum": ["high_impact", "low_impact", "bodyweight"],
                    "description": "Intensity/equipment level. Use low_impact for injuries.",
                },
            },
            "required": ["muscle_group", "intensity"],
        },
    },
}


def run(muscle_group: str, intensity: str) -> list:
    group = EXERCISES.get(muscle_group, {})
    exercises = group.get(intensity, group.get("bodyweight", []))
    return exercises
