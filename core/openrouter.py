import os
from openai import OpenAI


class OpenRouter:
    def __init__(self, model: str):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model

    def add_user_message(self, messages: list, message):
        if isinstance(message, list):
            for part in message:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": part.get("tool_use_id"),
                            "content": part.get("content", ""),
                        }
                    )
            return

        user_message = {
            "role": "user",
            "content": message.get("content") if isinstance(message, dict) else message,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        if hasattr(message, "choices") and message.choices:
            response_message = message.choices[0].message
            tool_calls = getattr(response_message, "tool_calls", None)
            assistant_message = {
                "role": "assistant",
                "content": self._content_to_text(response_message.content),
            }
            if tool_calls:
                assistant_message["tool_calls"] = [
                    tool_call.model_dump() for tool_call in tool_calls
                ]
        else:
            assistant_message = {
                "role": "assistant",
                "content": message.get("content") if isinstance(message, dict) else str(message),
            }
        messages.append(assistant_message)

    def text_from_message(self, message):
        return self._content_to_text(message.choices[0].message.content)

    def _content_to_text(self, content) -> str:
        if isinstance(content, str):
            return content
        if content is None:
            return ""
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        parts.append(part.get("text", ""))
                else:
                    part_type = getattr(part, "type", None)
                    if part_type == "text":
                        parts.append(getattr(part, "text", ""))
            return "\n".join(p for p in parts if p)
        return str(content)

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ):
        params = {
            "model": self.model,
            "max_tokens": 8000,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            params["tools"] = [{
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                }
            } for tool in tools]

        if system:
            params["system"] = system

        message = self.client.chat.completions.create(**params)
        return message
