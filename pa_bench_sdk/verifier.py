"""
Entry point for running scenario verifiers within this SDK.

Loads the scenario's `verifier.py`, ensures the expected `validation_function`
is present, and adapts its return value into a SDK-side VerificationResult.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .scenario import ScenarioDefinition


@dataclass
class TaskVerifier:
    name: str
    verdict: bool
    reason: str


@dataclass
class VerificationResult:
    passed: bool
    reward: float
    message: str
    details: Optional[Dict[str, Any]] = None


class VerifierRunner:
    """Loads verifier modules that ships with each scenario."""

    def __init__(self, base_path: Union[str, Path] = "data"):
        self.base_path = Path(base_path)

    def _load_module(self, verifier_path: Path):
        spec = importlib.util.spec_from_file_location(
            f"{verifier_path.stem}_verifier", verifier_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to import verifier from {verifier_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def run(
        self,
        scenario: Union[ScenarioDefinition, str],
        state: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> VerificationResult:
        scenario_obj: Optional[ScenarioDefinition]

        if isinstance(scenario, ScenarioDefinition):
            scenario_obj = scenario
            scenario_path = scenario.path
            scenario_id = scenario.metadata.scenario_id
        else:
            scenario_obj = None
            scenario_id = scenario
            scenario_path = self.base_path / scenario_id

        verifier_path = scenario_path / "verifier.py"
        if not verifier_path.exists():
            raise FileNotFoundError(
                f"Verifier not found for scenario '{scenario_id}' at {verifier_path}"
            )

        module = self._load_module(verifier_path)

        validation_function = getattr(module, "validation_function", None)
        if validation_function is None:
            raise AttributeError(
                f"Verifier at {verifier_path} must expose `validation_function`"
            )

        if state is not None:
            resolved_state = state
        elif scenario_obj is not None:
            resolved_state = {
                "gmail-clone": scenario_obj.gmail_state,
                "calendar-clone": scenario_obj.calendar_state,
            }
        else:
            raise ValueError("State must be provided when passing a scenario id")

        reward, checks = validation_function(resolved_state)

        if not isinstance(reward, (int, float)):
            raise TypeError("Verifier reward must be numeric")

        if not isinstance(checks, Sequence):
            raise TypeError("Verifier must return a sequence of TaskVerifier instances")

        task_verifiers = []
        for check in checks:
            if not isinstance(check, TaskVerifier):
                raise TypeError("All checks must be TaskVerifier instances")
            task_verifiers.append(check)

        passed = all(tv.verdict for tv in task_verifiers)
        message = (
            "All verifier checks passed"
            if passed
            else "One or more verifier checks failed"
        )

        return VerificationResult(
            passed=passed,
            reward=float(reward),
            message=message,
            details={
                "checks": task_verifiers,
                "scenario_id": scenario_id,
            },
        )
