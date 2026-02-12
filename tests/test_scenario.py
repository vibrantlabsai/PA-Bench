from pathlib import Path

from pa_bench_sdk.scenario import ScenarioLoader


def test_scenario_loader_returns_states(tmp_path):
    base_path = Path("data")
    loader = ScenarioLoader(base_path)

    scenario = loader.load("scenario_001_multi_meeting_coordination")

    assert scenario.metadata.scenario_id == "scenario_001_multi_meeting_coordination"
    assert scenario.metadata.description
    assert "gomail" in scenario.raw_data
    assert "gocalendar" in scenario.raw_data
    assert scenario.gmail_state == scenario.raw_data["gomail"]
    assert scenario.calendar_state == scenario.raw_data["gocalendar"]
    assert scenario.metadata.today == scenario.raw_data["today"]


def test_loader_list_scenarios_includes_known_folder():
    loader = ScenarioLoader("data")
    scenarios = loader.list_scenarios()

    assert "scenario_001_multi_meeting_coordination" in scenarios
