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
        gomail_url: Optional[str],
        gocalendar_url: Optional[str],
        env_file: Optional[Path],
        worlds_base_url: str,
    ):
        self.data_path = data_path
        self.scenario_id = scenario_id
        self.gomail_url = gomail_url
        self.gocalendar_url = gocalendar_url
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
        "--gomail-url",
        help="Optional override for GOMAIL_INSTANCE_URL",
    )
    parser.add_argument(
        "--gocalendar-url",
        help="Optional override for GOCALENDAR_INSTANCE_URL",
    )
    parser.add_argument(
        "--worlds-base-url",
        help="Base Worlds Vibrant Labs API URL (can also be set via WORLDS_BASE_URL in .env)",
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
        gomail_url=parsed.gomail_url,
        gocalendar_url=parsed.gocalendar_url,
        env_file=parsed.env_file,
        worlds_base_url=parsed.worlds_base_url,
    )


async def run_load(args: CLIArgs):
    loader = ScenarioLoader(args.data_path)
    scenario = loader.load(args.scenario_id)
    endpoints = await resolve_instance_urls(
        gmail_url=args.gomail_url,
        calendar_url=args.gocalendar_url,
        env_path=args.env_file,
        base_url=args.worlds_base_url,
    )

    client = WorldsClient()
    print(f"Loading scenario {scenario.metadata.scenario_id}")
    print(f"Task: {scenario.metadata.description}")
    today = scenario.metadata.today or "not specified"
    print(f"Today: {today}")
    print("Setting gomail state...")
    gomail_payload = dict(scenario.gmail_state)
    gocalendar_payload = dict(scenario.calendar_state)
    if scenario.metadata.today:
        gomail_payload["today"] = scenario.metadata.today
        gocalendar_payload["today"] = scenario.metadata.today
    await client.set_states(
        endpoints,
        gmail_state=gomail_payload,
        calendar_state=gocalendar_payload,
    )
    print("✅ Scenario loaded successfully.")
    print(f"Gomail instance: {endpoints.gmail_clone}")
    print(f"Gocalendar instance: {endpoints.calendar_clone}")


async def run_verify(args: CLIArgs):
    loader = ScenarioLoader(args.data_path)
    scenario = loader.load(args.scenario_id)
    endpoints = await resolve_instance_urls(
        gmail_url=args.gomail_url,
        calendar_url=args.gocalendar_url,
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
