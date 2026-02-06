"""
Command-line helpers for the PA Bench SDK.

Provides `load-scenario` and `verify` commands that mirror the original
scripts while reusing the new SDK internals.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Optional

from .scenario import ScenarioLoader
from .verifier import VerifierRunner
from .worlds import (
    InstanceEndpoints,
    WorldsClient,
    resolve_instance_urls,
    DEFAULT_WORLDS_BASE_URL,
)


DEFAULT_DATA_PATH = Path("data")


class CLIArgs:
    def __init__(
        self,
        data_path: Path,
        scenario_id: str,
        gmail_url: Optional[str],
        calendar_url: Optional[str],
        env_file: Optional[Path],
        worlds_base_url: str,
    ):
        self.data_path = data_path
        self.scenario_id = scenario_id
        self.gmail_url = gmail_url
        self.calendar_url = calendar_url
        self.env_file = env_file
        self.worlds_base_url = worlds_base_url


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pa-bench")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Base path containing scenario folders (default: data/)",
    )
    parser.add_argument(
        "--gmail-url",
        help="Optional override for GMAIL_INSTANCE_URL",
    )
    parser.add_argument(
        "--calendar-url",
        help="Optional override for CALENDAR_INSTANCE_URL",
    )
    parser.add_argument(
        "--worlds-base-url",
        default=DEFAULT_WORLDS_BASE_URL,
        help="Base Worlds Vibrant Labs API URL (default: http://worlds.vibrantlabs.com)",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=None,
        help="Optional .env file to load instance URLs from",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser(
        "load-scenario", help="Load data into Vibrant Labs clones"
    )
    load_parser.add_argument(
        "scenario_id", help="Scenario folder name (e.g. scenario_001)"
    )

    verify_parser = subparsers.add_parser(
        "verify", help="Run the scenario verifier against the current world state"
    )
    verify_parser.add_argument(
        "scenario_id", help="Scenario folder name (e.g. scenario_001)"
    )

    return parser


def _build_cli_args(parsed: argparse.Namespace) -> CLIArgs:
    return CLIArgs(
        data_path=parsed.data_path,
        scenario_id=parsed.scenario_id,
        gmail_url=parsed.gmail_url,
        calendar_url=parsed.calendar_url,
        env_file=parsed.env_file,
        worlds_base_url=parsed.worlds_base_url,
    )


async def run_load(args: CLIArgs):
    loader = ScenarioLoader(args.data_path)
    scenario = loader.load(args.scenario_id)
    endpoints = await resolve_instance_urls(
        gmail_url=args.gmail_url,
        calendar_url=args.calendar_url,
        env_path=args.env_file,
        base_url=args.worlds_base_url,
    )

    client = WorldsClient()
    print(f"Loading scenario {scenario.metadata.scenario_id}")
    print(f"Task: {scenario.metadata.description}")
    today = scenario.metadata.today or "not specified"
    print(f"Today: {today}")
    print("Setting gmail state...")
    gmail_payload = dict(scenario.gmail_state)
    calendar_payload = dict(scenario.calendar_state)
    if scenario.metadata.today:
        gmail_payload["today"] = scenario.metadata.today
        calendar_payload["today"] = scenario.metadata.today
    await client.set_states(
        endpoints,
        gmail_state=gmail_payload,
        calendar_state=calendar_payload,
    )
    print("✅ Scenario loaded successfully.")
    print(f"Gmail instance: {endpoints.gmail_clone}")
    print(f"Calendar instance: {endpoints.calendar_clone}")


async def run_verify(args: CLIArgs):
    loader = ScenarioLoader(args.data_path)
    scenario = loader.load(args.scenario_id)
    endpoints = await resolve_instance_urls(
        gmail_url=args.gmail_url,
        calendar_url=args.calendar_url,
        env_path=args.env_file,
        base_url=args.worlds_base_url,
    )
    client = WorldsClient()

    print(f"Fetching states for scenario {scenario.metadata.scenario_id}")
    states = await client.get_states(endpoints)

    runner = VerifierRunner(args.data_path)
    result = runner.run(scenario, state=states)

    print(f"Verification result for {scenario.metadata.scenario_id}:")
    print(f"  Reward: {result.reward}")
    print(f"  Message: {result.message}")
    checks = []
    if result.details:
        checks = result.details.get("checks", [])
    for check in checks:
        print(f"    - {check.name}: {'PASS' if check.verdict else 'FAIL'} - {check.reason}")

    if not result.passed:
        raise SystemExit(1)


def main():
    parser = _create_parser()
    namespace = parser.parse_args()
    args = _build_cli_args(namespace)

    if namespace.command == "load-scenario":
        asyncio.run(run_load(args))
    elif namespace.command == "verify":
        asyncio.run(run_verify(args))


if __name__ == "__main__":
    main()
