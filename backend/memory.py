import os
import json
import time
from datetime import datetime

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")

class Memory:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.conversation_file = os.path.join(MEMORY_DIR, "conversations.json")
        self.facts_file = os.path.join(MEMORY_DIR, "facts.json")
        self.reminders_file = os.path.join(MEMORY_DIR, "reminders.json")
        self.conversations = self._load(self.conversation_file)
        self.facts = self._load(self.facts_file)
        self.reminders = self._load(self.reminders_file)
        print(f"[MEMORY] Loaded {len(self.conversations)} conversations, {len(self.facts)} facts, {len(self.reminders)} reminders")

    def _load(self, filepath):
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []

    def _save(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_conversation(self, user_msg, assistant_msg):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "assistant": assistant_msg
        }
        self.conversations.append(entry)

        if len(self.conversations) > 500:
            self.conversations = self.conversations[-500:]

        self._save(self.conversation_file, self.conversations)

    def get_recent_conversations(self, limit=20):
        return self.conversations[-limit:]

    def remember_fact(self, key, value):
        self.facts.append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        self._save(self.facts_file, self.facts)

    def get_facts(self):
        return self.facts

    def search_facts(self, query):
        query_lower = query.lower()
        return [f for f in self.facts if query_lower in f["key"].lower() or query_lower in f["value"].lower()]

    def add_reminder(self, message, remind_at):
        reminder = {
            "id": int(time.time()),
            "message": message,
            "remind_at": remind_at,
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self.reminders.append(reminder)
        self._save(self.reminders_file, self.reminders)
        return reminder

    def get_pending_reminders(self):
        now = datetime.now()
        return [r for r in self.reminders if not r["completed"] and datetime.fromisoformat(r["remind_at"]) <= now]

    def complete_reminder(self, reminder_id):
        for r in self.reminders:
            if r["id"] == reminder_id:
                r["completed"] = True
                self._save(self.reminders_file, self.reminders)
                return True
        return False

    def get_all_reminders(self):
        return self.reminders
