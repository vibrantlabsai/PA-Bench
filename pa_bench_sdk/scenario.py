"""
Scenario loading helpers for PA Bench.

Scenarios already ship with Gmail/Calendar clone states. The loader simply
reads the stored JSON blobs, validates the expected structure, and exposes
metadata alongside the two world states.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


ScenarioId = str


@dataclass
class ScenarioMetadata:
    scenario_id: ScenarioId
    description: str
    today: Optional[str]


@dataclass
class ScenarioDefinition:
    metadata: ScenarioMetadata
    gmail_state: Dict[str, Any]
    calendar_state: Dict[str, Any]
    raw_data: Dict[str, Any]
    path: Path


class ScenarioLoader:
    """Loads scenario data that already packages clone states."""

    def __init__(self, base_path: Union[str, Path] = "data"):
        self.base_path = Path(base_path)

    def load(self, scenario_id: ScenarioId) -> ScenarioDefinition:
        scenario_path = self.base_path / scenario_id

        if not scenario_path.exists():
            raise FileNotFoundError(
                f"Scenario '{scenario_id}' not found at {scenario_path}"
            )

        data_path = scenario_path / "data.json"
        task_path = scenario_path / "task.json"

        if not data_path.exists() or not task_path.exists():
            raise FileNotFoundError(
                "Expected `data.json` and `task.json` next to verifier.py"
            )

        with open(data_path, encoding="utf-8") as f:
            raw_data = json.load(f)

        with open(task_path, encoding="utf-8") as f:
            task_data = json.load(f)

        description = task_data.get("description", "No description provided")
        today = raw_data.get("today") or task_data.get("today")

        gmail_state = raw_data.get("gmail-clone")
        calendar_state = raw_data.get("calendar-clone")

        if gmail_state is None or calendar_state is None:
            raise ValueError(
                "Scenario data must define both 'gmail-clone' and 'calendar-clone' states"
            )

        metadata = ScenarioMetadata(
            scenario_id=scenario_id,
            description=description,
            today=today,
        )

        return ScenarioDefinition(
            metadata=metadata,
            gmail_state=gmail_state,
            calendar_state=calendar_state,
            raw_data=raw_data,
            path=scenario_path,
        )

    def list_scenarios(self) -> List[ScenarioId]:
        if not self.base_path.exists():
            return []
        return sorted(
            [
                entry.name
                for entry in self.base_path.iterdir()
                if entry.is_dir() and entry.name.startswith("scenario_")
            ]
        )
