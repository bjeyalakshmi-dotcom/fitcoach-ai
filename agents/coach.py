"""
Coach Agent — sends nudges, reminders, and health flag alerts.
Autonomy: MEDIUM for nudges, LOW for health alerts (user must acknowledge).
"""
from agents.base import BaseAgent
from config import MAX_DAILY_NOTIFICATIONS
import database as db


SEND_TOOL = {
    "type": "function",
    "function": {
        "name": "send_notification",
        "description": "Send a push notification to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Notification message text"},
                "type":    {"type": "string", "enum": ["nudge", "health_alert", "plan_update"]},
            },
            "required": ["message", "type"],
        },
    },
}


class CoachAgent(BaseAgent):
    name = "coach"

    system_prompt = """You are the Coach Agent for FitAgent.

Your job is to craft motivating, empathetic, and actionable messages for the user.

Rules:
- For nudges: be encouraging and brief (under 80 characters)
- For health alerts: be clear and direct; always recommend consulting a professional for pain/injury
- For plan updates: explain WHY the plan changed in plain language
- Always call send_notification with the final message and correct type
- Never send more than 3 notifications per day (the system will enforce this)
- Never diagnose medical conditions — always say "consult a professional" for health concerns"""

    tools = [SEND_TOOL]

    def __init__(self):
        self._sent = []

    @property
    def tool_handlers(self):
        return {"send_notification": self._send}

    def _send(self, message: str, type: str):
        self._sent.append({"message": message, "type": type})
        return {"sent": True, "message": message}

    def send_nudge(self, user_id: str, reason: str) -> dict:
        if db.count_today_notifications(user_id) >= MAX_DAILY_NOTIFICATIONS:
            return {"skipped": True, "reason": "daily limit reached"}

        self._sent = []
        self.run(f"Send a motivational nudge to the user because: {reason}")

        for n in self._sent:
            db.save_notification(user_id, n["message"], n["type"])

        return {"sent": self._sent}

    def send_health_alert(self, user_id: str, concern: str) -> dict:
        self._sent = []
        self.run(
            f"Send a health alert to the user about: {concern}\n"
            "Include a recommendation to consult a physiotherapist or doctor."
        )
        for n in self._sent:
            db.save_notification(user_id, n["message"], "health_alert")
        return {"sent": self._sent}

    def send_plan_update(self, user_id: str, reason: str) -> dict:
        self._sent = []
        self.run(f"Send a plan update notification explaining: {reason}")
        for n in self._sent:
            db.save_notification(user_id, n["message"], "plan_update")
        return {"sent": self._sent}

    def chat(self, user_id: str, message: str, context: dict) -> str:
        """Conversational coaching with RAG — retrieves relevant fitness knowledge before responding."""
        import json
        try:
            from tools.rag_engine import build_context
            rag_context = build_context(message)
        except Exception:
            rag_context = ""

        rag_block = f"\n\n{rag_context}" if rag_context else ""
        prompt = (
            f"User message: {message}\n\n"
            f"User context:\n{json.dumps(context, indent=2)}"
            f"{rag_block}\n\n"
            "Respond as a friendly, knowledgeable fitness coach. "
            "Use the retrieved knowledge above where relevant. "
            "Keep it under 200 words. If the user mentions pain or injury, "
            "always recommend consulting a professional."
        )
        return self.run(prompt)
