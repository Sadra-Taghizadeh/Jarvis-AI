import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIBrain:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://opencode.ai/zen/v1")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = os.getenv("AI_MODEL", "openai/gpt-4o-mini")
        print(f"[AI_INIT] Model: {self.model} | Base URL: {base_url}")

        self.system_prompt = """You are Jarvis, an AI assistant that controls the user's computer and remembers things.

ACTION TYPES:

COMPUTER CONTROL:
- open_app: {"action": "open_app", "app": "notepad"}
- write_and_open: {"action": "write_and_open", "text": "content", "app": "notepad"}
- google_search: {"action": "google_search", "query": "search term"}
- type_in_chrome: {"action": "type_in_chrome", "url": "example.com"}
- press_key: {"action": "press_key", "key": "ctrl+s"}
- file_operation: {"action": "file_operation", "operation": "write|read|append", "path": "C:\\file.txt", "content": "text"}
- system_info: {"action": "system_info"}
- run_command: {"action": "run_command", "command": "dir"}
- wait: {"action": "wait", "seconds": 2}
- chain: {"action": "chain", "steps": [...]}

SEARCH & READ (IMPORTANT - use this to get real data from the web):
- search_and_read: {"action": "search_and_read", "query": "rasht weather this week"}
  This searches Google AND reads the results using vision AI. Use this when you need REAL information from the web (weather, news, facts, prices, etc).

SCREEN:
- screenshot: {"action": "screenshot", "question": "What do you see?"}
- save_screenshot_to_desktop: {"action": "save_screenshot_to_desktop", "filename": "screenshot.png"}
- describe_screen: {"action": "describe_screen"}
- find_element: {"action": "find_element", "element": "search button"}

FILES:
- save_to_desktop: {"action": "save_to_desktop", "content": "text", "filename": "file.txt"}

MEMORY:
- remember: {"action": "remember", "key": "favorite color", "value": "blue"}
- recall: {"action": "recall", "query": "favorite color"}

REMINDERS:
- remind: {"action": "remind", "message": "Take medicine", "time": "2024-01-15T15:00:00"}
- list_reminders: {"action": "list_reminders"}

CRITICAL RULES:
1. When user asks for REAL information (weather, news, prices, facts) → ALWAYS use search_and_read
2. NEVER make up or guess information. Use search_and_read to get real data first.
3. For "search X" → use google_search (just opens search)
4. For "search X and tell me Y" or "what is the weather" → use search_and_read (searches AND reads results)
5. For "screenshot" or "save screenshot" → use save_screenshot_to_desktop
6. For "go to website" → use type_in_chrome (opens new tab)
7. For "open notepad and write X" → use write_and_open
8. NEVER use run_command for screenshots or file saving
9. For casual chat → respond normally without JSON
10. ALWAYS respond with ONLY the JSON action, no extra text"""

        self.conversation_history = []

    def _clean_message(self, text):
        import re
        text = re.sub(r'<system-reminder>.*?</system-reminder>', '', text, flags=re.DOTALL)
        return text.strip()

    def chat(self, user_message: str, memory=None) -> dict:
        clean_msg = self._clean_message(user_message)
        if not clean_msg:
            return {"type": "chat", "message": "I didn't catch that. Could you repeat?"}

        self.conversation_history.append({"role": "user", "content": clean_msg})

        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if memory:
            facts = memory.get_facts()
            if facts:
                facts_text = "\n".join([f"- {f['key']}: {f['value']}" for f in facts[-20:]])
                messages.append({"role": "system", "content": f"Things the user told you to remember:\n{facts_text}"})

            recent = memory.get_recent_conversations(5)
            if recent:
                clean_history = []
                for r in recent:
                    clean_history.append(f"User: {self._clean_message(r['user'])}\nJarvis: {self._clean_message(r['assistant'][:100])}")
                history_text = "\n".join(clean_history)
                messages.append({"role": "system", "content": f"Recent conversation history:\n{history_text}"})

        messages.extend(self.conversation_history)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=8192
            )

            raw_message = response.choices[0].message.content
            print(f"[AI_CHAT] Raw response: {repr(raw_message[:300])}")

            assistant_message = self._clean_message(raw_message)
            print(f"[AI_CHAT] Cleaned response: {repr(assistant_message[:300])}")

            if not assistant_message or not assistant_message.strip():
                assistant_message = "I'm not sure how to respond to that. Could you rephrase?"

            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return self._parse_response(assistant_message)

        except Exception as e:
            print(f"[AI_CHAT] ERROR: {e}")
            return {"type": "error", "message": str(e)}

    def _parse_response(self, message: str) -> dict:
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', message, re.DOTALL)
        if json_match:
            message = json_match.group(1).strip()

        try:
            if message.strip().startswith("{"):
                data = json.loads(message)

                if "action_sequence" in data:
                    steps = []
                    for s in data["action_sequence"]:
                        mapped = self._map_action(s)
                        if mapped:
                            steps.append(mapped)
                    if len(steps) == 1:
                        return {"type": "action", "action": steps[0]}
                    elif len(steps) > 1:
                        return {"type": "action", "action": {"action": "chain", "steps": steps}}

                if "action" in data:
                    return {"type": "action", "action": data}

                if "actions" in data:
                    steps = [self._map_action(a) for a in data["actions"]]
                    steps = [s for s in steps if s]
                    if len(steps) == 1:
                        return {"type": "action", "action": steps[0]}
                    elif len(steps) > 1:
                        return {"type": "action", "action": {"action": "chain", "steps": steps}}

        except json.JSONDecodeError:
            pass

        return {"type": "chat", "message": message}

    def _map_action(self, action: dict) -> dict:
        action_type = action.get("action", "")

        mapping = {
            "launch_application": lambda: {"action": "open_app", "app": action.get("name", action.get("app", ""))},
            "open_app": lambda: {"action": "open_app", "app": action.get("name", action.get("app", ""))},
            "type_text": lambda: {"action": "type_text", "text": action.get("text", "")},
            "press_key": lambda: {"action": "press_key", "key": "+".join(action.get("keys", [action.get("key", "")]))},
            "wait": lambda: {"action": "wait", "seconds": action.get("seconds", action.get("ms", 1000) / 1000)},
            "search_web": lambda: {"action": "search_and_read", "query": action.get("query", "")},
            "search_and_read": lambda: {"action": "search_and_read", "query": action.get("query", "")},
            "open_url": lambda: {"action": "type_in_chrome", "url": action.get("url", "")},
            "google_search": lambda: {"action": "google_search", "query": action.get("query", "")},
            "screenshot": lambda: {"action": "screenshot", "question": action.get("question", "What is on the screen?")},
            "describe_screen": lambda: {"action": "describe_screen"},
            "system_info": lambda: {"action": "system_info"},
        }

        if action_type in mapping:
            return mapping[action_type]()

        return action
