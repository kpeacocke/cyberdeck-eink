"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml


@dataclass(frozen=True)
class DisplayConfig:
    interface: str
    serial_device: str
    baud_rate: int | None
    timeout_seconds: float
    rotation: int
    driver: str
    expected_serial_device: str | None = None


@dataclass(frozen=True)
class DeviceConfig:
    name: str
    host: str
    ssh_user: str


@dataclass(frozen=True)
class AppConfig:
    device: DeviceConfig
    display: DisplayConfig
    raw: dict
    source: Path


def _default_config_path() -> Path:
    repo_default = Path(__file__).resolve().parents[2] / "config" / "default.yaml"
    if repo_default.exists():
        return repo_default
    raise FileNotFoundError("Could not locate config/default.yaml")


def resolve_config_path(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env_path = os.getenv("CYBERDECK_EINK_CONFIG")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return _default_config_path()


def load_config(explicit: str | None = None) -> AppConfig:
    path = resolve_config_path(explicit)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    device = raw.get("device", {})
    display = raw.get("display", {})

    required_device = ("name", "host", "ssh_user")
    required_display = (
        "interface",
        "serial_device",
        "baud_rate",
        "timeout_seconds",
        "rotation",
        "driver",
    )

    missing = [f"device.{key}" for key in required_device if key not in device]
    missing.extend(f"display.{key}" for key in required_display if key not in display)
    if missing:
        raise ValueError("Missing required configuration keys: " + ", ".join(missing))

    if display["interface"] != "uart":
        raise ValueError("Version 0.1 supports only display.interface: uart")

    if display["baud_rate"] is not None and int(display["baud_rate"]) <= 0:
        raise ValueError("display.baud_rate must be greater than zero")

    if int(display["rotation"]) not in (0, 90, 180, 270):
        raise ValueError("display.rotation must be one of 0, 90, 180 or 270")

    return AppConfig(
        device=DeviceConfig(
            name=str(device["name"]),
            host=str(device["host"]),
            ssh_user=str(device["ssh_user"]),
        ),
        display=DisplayConfig(
            interface=str(display["interface"]),
            serial_device=str(display["serial_device"]),
            baud_rate=int(display["baud_rate"]) if display["baud_rate"] is not None else None,
            timeout_seconds=float(display["timeout_seconds"]),
            rotation=int(display["rotation"]),
            driver=str(display["driver"]),
            expected_serial_device=display.get("expected_serial_device"),
        ),
        raw=raw,
        source=path,
    )
