from pathlib import Path

from pa_bench_sdk.scenario import ScenarioLoader
from pa_bench_sdk.verifier import VerifierRunner, TaskVerifier


def test_verifier_runner_executes_checks():
    loader = ScenarioLoader(Path("data"))
    scenario = loader.load("scenario_001_multi_meeting_coordination")

    runner = VerifierRunner(Path("data"))
    result = runner.run(scenario)

    assert isinstance(result.reward, float)
    assert result.details is not None
    checks = result.details.get("checks", [])
    assert all(isinstance(check, TaskVerifier) for check in checks)
    assert len(checks) >= 1
