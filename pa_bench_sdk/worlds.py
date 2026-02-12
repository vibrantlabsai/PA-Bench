"""
Client helpers for interacting with Vibrant Labs worlds.

Works with Gomail and Gocalendar clones by name and mirrors the simple
client pattern from the existing scraper scripts.
"""

from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

DEFAULT_WORLDS_BASE_URL: Optional[str] = None
DEFAULT_ENV_PATH = Path(__file__).parent.parent / ".env"


@dataclass
class InstanceEndpoints:
    gmail_clone: str
    calendar_clone: str

    def for_clone(self, clone_name: str) -> str:
        if clone_name == "gomail":
            return self.gmail_clone
        if clone_name == "gocalendar":
            return self.calendar_clone
        raise KeyError(f"Unknown clone: {clone_name}")

    def as_mapping(self) -> Dict[str, str]:
        return {
            "gomail": self.gmail_clone,
            "gocalendar": self.calendar_clone,
        }


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def _persist_env_file(env_path: Path, endpoints: InstanceEndpoints, base_url: str) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"WORLDS_BASE_URL={base_url}\n")
        f.write(f"GOMAIL_INSTANCE_URL={endpoints.gmail_clone}\n")
        f.write(f"GOCALENDAR_INSTANCE_URL={endpoints.calendar_clone}\n")


async def _create_instance(
    session: aiohttp.ClientSession, base_url: str, env_type: str
) -> str:
    url = f"{base_url}/envs/{env_type}/create"
    async with session.post(url) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Failed to create {env_type}: {resp.status} - {text}")
        data = await resp.json()
        instance_id = data.get("instance_id", data.get("id"))
        if not instance_id:
            raise RuntimeError("Instance creation response missing identifier")
        return f"http://{instance_id}.worlds.vibrantlabs.com"


async def create_instances(
    base_url: str,
) -> InstanceEndpoints:
    async with aiohttp.ClientSession() as session:
        gmail = _create_instance(session, base_url, "gomail")
        calendar = _create_instance(session, base_url, "gocalendar")
        gmail_url, calendar_url = await asyncio.gather(gmail, calendar)
    return InstanceEndpoints(gmail_clone=gmail_url, calendar_clone=calendar_url)


async def resolve_instance_urls(
    gmail_url: Optional[str] = None,
    calendar_url: Optional[str] = None,
    env_path: Optional[Path] = None,
    base_url: Optional[str] = None,
    create_if_missing: bool = True,
) -> InstanceEndpoints:
    env_path = env_path or DEFAULT_ENV_PATH
    if env_path.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except ImportError:
            _load_env_file(env_path)

    # Load base_url from env - must be present
    if base_url is None:
        base_url = os.environ.get("WORLDS_BASE_URL")
    if base_url is None:
        raise EnvironmentError(
            "WORLDS_BASE_URL is not set. "
            "Set it via environment variable or .env file."
        )

    gmail_value = gmail_url or os.environ.get("GOMAIL_INSTANCE_URL")
    calendar_value = calendar_url or os.environ.get("GOCALENDAR_INSTANCE_URL")

    if gmail_value and calendar_value:
        return InstanceEndpoints(
            gmail_clone=gmail_value,
            calendar_clone=calendar_value,
        )

    if not create_if_missing:
        missing = []
        if not gmail_value:
            missing.append("GOMAIL_INSTANCE_URL")
        if not calendar_value:
            missing.append("GOCALENDAR_INSTANCE_URL")
        raise EnvironmentError(
            f"Instance URLs undefined: {', '.join(missing)}. "
            "Set them via env vars or .env."
        )

    endpoints = await create_instances(base_url)
    os.environ["GOMAIL_INSTANCE_URL"] = endpoints.gmail_clone
    os.environ["GOCALENDAR_INSTANCE_URL"] = endpoints.calendar_clone
    os.environ["WORLDS_BASE_URL"] = base_url
    _persist_env_file(env_path, endpoints, base_url)
    return endpoints


class WorldsClient:
    """Minimal HTTP client for Vibrant Labs clones."""

    async def _post(self, url: str, payload: Dict[str, Any]) -> None:
        endpoint = f"{url}/api/set_state"
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"set_state failed: {resp.status} – {text}")

    async def _get(self, url: str) -> Dict[str, Any]:
        endpoint = f"{url}/api/get_state"
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"get_state failed: {resp.status} – {text}")
                return await resp.json()

    async def set_states(
        self, endpoints: InstanceEndpoints, gmail_state: Dict[str, Any], calendar_state: Dict[str, Any]
    ) -> None:
        await self._post(endpoints.gmail_clone, gmail_state)
        await self._post(endpoints.calendar_clone, calendar_state)

    async def get_states(self, endpoints: InstanceEndpoints) -> Dict[str, Dict[str, Any]]:
        gmail_state = await self._get(endpoints.gmail_clone)
        calendar_state = await self._get(endpoints.calendar_clone)
        return {
            "gomail": gmail_state,
            "gocalendar": calendar_state,
        }
