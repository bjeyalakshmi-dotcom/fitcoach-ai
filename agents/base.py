"""
Base agent class — handles the OpenAI tool-use loop.
All specialist agents inherit from this.
"""
import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL, MAX_TOKENS

client = OpenAI(api_key=OPENAI_API_KEY)


class BaseAgent:
    name: str = "base"
    system_prompt: str = ""
    tools: list = []        # OpenAI function-tool format
    tool_handlers: dict = {}

    def _run_loop(self, messages: list) -> str:
        """Standard OpenAI tool-use loop. Returns final text reply."""
        # Prepend system message if defined
        full_messages = (
            [{"role": "system", "content": self.system_prompt}] + messages
            if self.system_prompt
            else list(messages)
        )

        while True:
            kwargs = dict(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=full_messages,
            )
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            if choice.finish_reason == "stop":
                return (choice.message.content or "").strip()

            # Append the assistant turn (may contain tool_calls)
            full_messages.append(choice.message)

            if choice.finish_reason == "tool_calls":
                for tc in choice.message.tool_calls:
                    handler = self.tool_handlers.get(tc.function.name)
                    try:
                        args = json.loads(tc.function.arguments)
                        result = handler(**args) if handler else {"error": f"Unknown tool: {tc.function.name}"}
                    except Exception as e:
                        result = {"error": str(e)}

                    full_messages.append({
                        "role":         "tool",
                        "tool_call_id": tc.id,
                        "content":      json.dumps(result),
                    })

    def run(self, user_message: str, context: dict = None) -> str:
        prompt = user_message
        if context:
            prompt = f"Context:\n{json.dumps(context, indent=2)}\n\n{user_message}"
        return self._run_loop([{"role": "user", "content": prompt}])
