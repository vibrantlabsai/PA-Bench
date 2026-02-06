import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pa_bench_sdk.cli import (
    CLIArgs,
    DEFAULT_WORLDS_BASE_URL,
    run_load,
    run_verify,
)
from pa_bench_sdk.scenario import ScenarioLoader
from pa_bench_sdk.verifier import VerificationResult
from pa_bench_sdk.worlds import InstanceEndpoints


FIXTURE_SCENARIO = "scenario_001_multi_meeting_coordination"


def make_args():
    return CLIArgs(
        data_path=Path("data"),
        scenario_id=FIXTURE_SCENARIO,
        gmail_url="http://gmail.instance",
        calendar_url="http://calendar.instance",
        env_file=None,
        worlds_base_url=DEFAULT_WORLDS_BASE_URL,
    )


@patch("pa_bench_sdk.cli.resolve_instance_urls", new_callable=AsyncMock)
@patch("pa_bench_sdk.cli.WorldsClient")
def test_cli_load_sets_states(mock_world_client, mock_resolve):
    mock_resolve.return_value = InstanceEndpoints(
        gmail_clone="http://gmail.instance",
        calendar_clone="http://calendar.instance",
    )
    mock_client = mock_world_client.return_value
    mock_client.set_states = AsyncMock()

    args = make_args()
    asyncio.run(run_load(args))

    mock_client.set_states.assert_awaited_once()
    loader = ScenarioLoader(Path("data"))
    scenario = loader.load(FIXTURE_SCENARIO)
    call = mock_client.set_states.await_args
    gmail_payload = call.kwargs["gmail_state"]
    calendar_payload = call.kwargs["calendar_state"]
    assert gmail_payload["today"] == scenario.metadata.today
    assert calendar_payload["today"] == scenario.metadata.today


@patch("pa_bench_sdk.cli.resolve_instance_urls", new_callable=AsyncMock)
@patch("pa_bench_sdk.cli.VerifierRunner")
@patch("pa_bench_sdk.cli.WorldsClient")
def test_cli_verify_fetches_states(
    mock_world_client, mock_verifier_runner, mock_resolve
):
    mock_resolve.return_value = InstanceEndpoints(
        gmail_clone="http://gmail.instance",
        calendar_clone="http://calendar.instance",
    )
    mock_client = mock_world_client.return_value
    mock_client.get_states = AsyncMock(
        return_value={
            "gmail-clone": {},
            "calendar-clone": {},
        }
    )

    mock_verifier_runner.return_value.run.return_value = VerificationResult(
        passed=True,
        reward=1.0,
        message="stubbed pass",
        details={"checks": []},
    )
    args = make_args()
    asyncio.run(run_verify(args))
    mock_client.get_states.assert_awaited_once()
