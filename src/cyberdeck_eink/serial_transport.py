"""UART transport helpers."""

from __future__ import annotations

from pathlib import Path
import os

import serial

from .config import DisplayConfig


def serial_diagnostics(config: DisplayConfig) -> dict[str, object]:
    device = Path(config.serial_device)
    exists = device.exists()
    resolved = str(device.resolve()) if exists else None
    readable = os.access(device, os.R_OK) if exists else False
    writable = os.access(device, os.W_OK) if exists else False

    return {
        "device": str(device),
        "exists": exists,
        "resolved": resolved,
        "readable": readable,
        "writable": writable,
        "baud_rate": config.baud_rate,
        "timeout_seconds": config.timeout_seconds,
    }


def open_serial(config: DisplayConfig) -> serial.Serial:
    """Open the configured UART. The caller owns the returned handle."""
    return serial.Serial(
        port=config.serial_device,
        baudrate=config.baud_rate,
        timeout=config.timeout_seconds,
        write_timeout=config.timeout_seconds,
    )
