import json
import random
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"

class ScenarioManager:
    def __init__(self):
        self.scenarios = {
            "easy": self._load_data("easy_cases.json"),
            "medium": self._load_data("medium_cases.json"),
            "hard": self._load_data("hard_cases.json")
        }

    def _load_data(self, filename: str) -> List[Dict[str, Any]]:
        path = DATA_DIR / filename
        if not path.exists():
            return []
        with open(path, "r") as f:
            return json.load(f)

    def get_scenario(self, task_id: str, case_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        level_scenarios = self.scenarios.get(task_id, [])
        if not level_scenarios:
            return None
        
        if case_id:
            for s in level_scenarios:
                if s["id"] == case_id:
                    return s
            return None
        
        return random.choice(level_scenarios)

    def list_tasks(self) -> List[str]:
        return list(self.scenarios.keys())

    def list_cases(self, task_id: str) -> List[str]:
        return [s["id"] for s in self.scenarios.get(task_id, [])]
