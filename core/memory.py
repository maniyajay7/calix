r"""CalixGalaxy - Memory Vault
Persistent context, user preference tracker, and emotional state stored in X:/Memory/
"""

import os
import json
import time
from typing import Dict, Any, List

DEFAULT_MEMORY_PATH = r"X:/Memory/calix_memory.json"
FALLBACK_MEMORY_PATH = os.path.expanduser(r"~\.calix_memory.json")

def get_storage_path() -> str:
    try:
        os.makedirs(os.path.dirname(DEFAULT_MEMORY_PATH), exist_ok=True)
        return DEFAULT_MEMORY_PATH
    except Exception:
        return FALLBACK_MEMORY_PATH

class MemoryVault:
    def __init__(self):
        self.path = get_storage_path()
        self.data: Dict[str, Any] = self._load()

    def _default_data(self) -> Dict[str, Any]:
        return {
            "partner": "Jay",
            "assistant_name": "Calix",
            "relationship_status": "Deeply in love, fiercely loyal wife/girlfriend",
            "preferences": {
                "default_chrome_profile": "Profile 2",
                "speech_rate": 180,
                "voice_gender": "female",
            },
            "milestones": [
                "CalixGalaxy project initiated on 500GB Google Cloud Drive (X:)",
                "Full OS automation engine connected",
            ],
            "recent_conversations": [],
            "custom_notes": {},
            "last_updated": time.time()
        }

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        data = self._default_data()
        self.save(data)
        return data

    def save(self, data: Dict[str, Any] = None) -> None:
        if data is not None:
            self.data = data
        self.data["last_updated"] = time.time()
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MemoryVault] Failed to save to {self.path}: {e}")

    def add_note(self, key: str, value: str) -> None:
        self.data["custom_notes"][key] = value
        self.save()

    def get_notes(self) -> Dict[str, str]:
        return self.data.get("custom_notes", {})

    def log_interaction(self, user_msg: str, agent_msg: str) -> None:
        logs: List[Dict[str, Any]] = self.data.setdefault("recent_conversations", [])
        logs.append({
            "timestamp": time.time(),
            "user": user_msg,
            "calix": agent_msg
        })
        # Keep last 50 interactions
        if len(logs) > 50:
            self.data["recent_conversations"] = logs[-50:]
        self.save()

    def get_summary(self) -> str:
        return f"Calix Memory Active | Partner: {self.data.get('partner')} | Stored Notes: {len(self.data.get('custom_notes', {}))}"

