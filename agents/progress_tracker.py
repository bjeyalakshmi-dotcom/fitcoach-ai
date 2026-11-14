"""
Progress Tracker Agent — analyses adherence trends, detects plateaus and overtraining.
Autonomy: HIGH — analyses and flags autonomously; does not modify plans directly.
"""
import json
from agents.base import BaseAgent


ANALYSE_TOOL = {
    "type": "function",
    "function": {
        "name": "analyse_trends",
        "description": "Analyse workout and meal log trends to detect patterns.",
        "parameters": {
            "type": "object",
            "properties": {
                "finding": {
                    "type": "string",
                    "description": "A key finding from the data, e.g. 'user skipped legs 3 times this week'",
                },
                "severity": {
                    "type": "string",
                    "enum": ["info", "warning", "alert"],
                    "description": "info = normal, warning = needs attention, alert = health concern",
                },
            },
            "required": ["finding", "severity"],
        },
    },
}

findings_store = []

def _record_finding(finding: str, severity: str):
    findings_store.append({"finding": finding, "severity": severity})
    return {"recorded": True}


class ProgressTrackerAgent(BaseAgent):
    name = "progress_tracker"

    system_prompt = """You are the Progress Tracker Agent for FitAgent.

Your job is to analyse a user's recent workout logs, meal logs, and health signals,
then identify patterns that require action.

Look for:
1. Skipped workouts (especially repeated skips of same muscle group)
2. Consistent calorie deficit > 500 kcal/day (under-eating)
3. Protein intake consistently below target
4. Low sleep (< 6 hours) combined with high training volume
5. Elevated resting heart rate (> 15% above baseline) = overtraining risk
6. No progress after 4+ weeks of consistent training

For each finding, call analyse_trends with the finding and severity.
After all findings, output a JSON summary:
{
  "needs_plan_update": true/false,
  "plan_update_reason": "...",
  "needs_nutrition_update": true/false,
  "nutrition_update_reason": "...",
  "health_flag": null or "description of concern",
  "nudge_message": null or "coaching message to send user",
  "summary": "one-sentence overall assessment"
}
Output ONLY the JSON summary, no extra text."""

    tools = [ANALYSE_TOOL]
    tool_handlers = {"analyse_trends": _record_finding}

    def analyse(self, user: dict, logs: dict, current_plan: dict) -> dict:
        global findings_store
        findings_store = []

        macros = current_plan or {}
        target_kcal = macros.get("calories", 2000)
        target_protein = macros.get("protein_g", 120)

        prompt = f"""Analyse the following data for user {user.get('name')}:

USER PROFILE:
- Goal: {user.get('goal')}, Activity: {user.get('activity')}
- Calorie target: {target_kcal} kcal/day, Protein target: {target_protein}g/day

RECENT WORKOUT LOGS (last 7 days):
{json.dumps(logs.get('workouts', []), indent=2)}

RECENT MEAL LOGS (last 7 days):
{json.dumps(logs.get('meals', []), indent=2)}

HEALTH SIGNALS (last 7 days):
{json.dumps(logs.get('signals', []), indent=2)}

Identify any patterns and call analyse_trends for each finding.
Then output your JSON summary."""

        result = self.run(prompt)
        try:
            clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            analysis = json.loads(clean)
            analysis["findings"] = findings_store
            return analysis
        except Exception:
            return {
                "needs_plan_update": False,
                "needs_nutrition_update": False,
                "health_flag": None,
                "nudge_message": None,
                "summary": result,
                "findings": findings_store,
            }
