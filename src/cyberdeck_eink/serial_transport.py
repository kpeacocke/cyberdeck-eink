"""UART transport helpers."""

from __future__ import annotations

from pathlib import Path
import os
import stat
import grp
import socket

import serial

from .config import DisplayConfig


def serial_diagnostics(config: DisplayConfig) -> dict[str, object]:
    device = Path(config.serial_device)
    exists = device.exists()
    resolved = str(device.resolve()) if exists else None
    readable = os.access(device, os.R_OK) if exists else False
    writable = os.access(device, os.W_OK) if exists else False

    character_device = stat.S_ISCHR(device.stat().st_mode) if exists else False
    expected = config.expected_serial_device
    mapping_matches = resolved == expected if expected else None

    return {
        "local_hostname": socket.gethostname(),
        "character_device": character_device,
        "expected_serial_device": expected,
        "mapping_matches": mapping_matches,
        "owner_group": grp.getgrgid(device.stat().st_gid).gr_name if exists else None,
        "mode": stat.filemode(device.stat().st_mode) if exists else None,
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
    if config.baud_rate is None:
        raise ValueError("Display baud rate is unverified; set display.baud_rate before opening UART")
    result = serial_diagnostics(config)
    if not result["character_device"]:
        raise ValueError("Configured UART is not an existing character device")
    if result["mapping_matches"] is False:
        raise ValueError("Configured UART resolves to an unexpected device")
    return serial.Serial(
        port=str(result["resolved"]),
        exclusive=True,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        baudrate=config.baud_rate,
        timeout=config.timeout_seconds,
        write_timeout=config.timeout_seconds,
    )
