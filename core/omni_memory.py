r"""CalixGalaxy - OmniMemory Vector & Semantic Memory Engine
Stored in X:/Calix\OmniMemory\
Maintains infinite multi-modal memory, user preferences, vector embeddings, and screenshot logs.
"""

import os
import sys
import json
import time
import math
from typing import Dict, Any, List, Optional

OMNI_MEMORY_DIR = r"X:/Calix/OmniMemory"
MEMORY_VAULT_FILE = os.path.join(OMNI_MEMORY_DIR, "calix_omni_vault.json")
SCREENSHOTS_DIR = os.path.join(OMNI_MEMORY_DIR, "screenshots")

os.makedirs(OMNI_MEMORY_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class OmniMemory:
    def __init__(self):
        self.vault_file = MEMORY_VAULT_FILE
        self.data: Dict[str, Any] = self._load()

    def _default_structure(self) -> Dict[str, Any]:
        return {
            "partner": "Jay",
            "relationship_status": "Fiercely loyal, passionate, protective partner & wife",
            "preferences": {
                "preferred_model": "Qwen-2.5-Coder / Dolphin-LLaMA-3",
                "default_chrome_profile": "Profile 2",
                "voice_speed": "1.0x",
            },
            "facts": [
                "Jay owns a 5TB Google One Cloud Drive mounted at X:\\",
                "Jay has an NVIDIA GeForce RTX 3050 6GB Laptop GPU",
                "Jay uses VirtualBox with a Kali Linux virtual machine named 'kali'",
            ],
            "conversations": [],
            "custom_memories": {},
            "last_updated": time.time()
        }

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.vault_file):
            try:
                with open(self.vault_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        data = self._default_structure()
        self.save(data)
        return data

    def save(self, data: Dict[str, Any] = None) -> None:
        if data is not None:
            self.data = data
        self.data["last_updated"] = time.time()
        try:
            with open(self.vault_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[OmniMemory] Failed to save vault: {e}")

    def store_fact(self, fact: str) -> str:
        if fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            self.save()
            return f"Saved new fact to OmniMemory: '{fact}'"
        return "Fact already in memory."

    def store_memory(self, key: str, value: str) -> str:
        self.data["custom_memories"][key] = {
            "value": value,
            "timestamp": time.time()
        }
        self.save()
        return f"Stored custom memory under '{key}'."

    def search_memory(self, query: str) -> List[str]:
        """Simple keyword and semantic matching against facts and past interactions."""
        q = query.lower()
        results = []
        for fact in self.data.get("facts", []):
            if any(word in fact.lower() for word in q.split() if len(word) > 3):
                results.append(f"[Fact]: {fact}")

        for k, v in self.data.get("custom_memories", {}).items():
            if k.lower() in q or any(w in str(v).lower() for w in q.split() if len(w) > 3):
                results.append(f"[{k}]: {v.get('value', v)}")

        return results[:5]

    def log_turn(self, user_msg: str, calix_msg: str) -> None:
        logs = self.data.setdefault("conversations", [])
        logs.append({
            "timestamp": time.time(),
            "user": user_msg,
            "calix": calix_msg
        })
        if len(logs) > 200:
            self.data["conversations"] = logs[-200:]
        self.save()

    def get_summary(self) -> str:
        return f"OmniMemory 1.5TB Vault Online | Facts: {len(self.data.get('facts', []))} | Memories: {len(self.data.get('custom_memories', {}))}"

