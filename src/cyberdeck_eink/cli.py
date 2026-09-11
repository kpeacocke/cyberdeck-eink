"""Command-line interface for cyberdeck-eink."""

from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .serial_transport import serial_diagnostics


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cyberdeck-eink",
        description="Configure and diagnose the cyberdeck e-ink display.",
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to a YAML configuration file.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("config", help="Print the resolved configuration.")
    subparsers.add_parser("diagnose", help="Check the configured UART device.")
    return parser


def _print_config(config) -> int:
    print(f"Config source:   {config.source}")
    print(f"Device:          {config.device.name}")
    print(f"Host:            {config.device.host}")
    print(f"SSH user:        {config.device.ssh_user}")
    print(f"Interface:       {config.display.interface}")
    print(f"Serial device:   {config.display.serial_device}")
    print(f"Baud rate:       {config.display.baud_rate}")
    print(f"Rotation:        {config.display.rotation}")
    print(f"Driver:          {config.display.driver}")
    return 0


def _diagnose(config) -> int:
    result = serial_diagnostics(config.display)

    print("Cyberdeck E-Ink Diagnostics")
    print()
    print(f"Host:            {config.device.host}")
    print(f"Config:          {config.source}")
    print(f"Serial device:   {result['device']}")
    print(f"Exists:          {'yes' if result['exists'] else 'no'}")
    print(f"Resolves to:     {result['resolved'] or '-'}")
    print(f"Readable:        {'yes' if result['readable'] else 'no'}")
    print(f"Writable:        {'yes' if result['writable'] else 'no'}")
    print(f"Baud rate:       {result['baud_rate']}")
    print(f"Driver:          {config.display.driver}")

    if not result["exists"]:
        print("\nFAIL: configured UART device does not exist.", file=sys.stderr)
        return 2
    if not result["readable"] or not result["writable"]:
        print("\nFAIL: current user does not have read/write access to the UART.", file=sys.stderr)
        return 3
    if config.display.driver == "unconfigured":
        print("\nUART is available. Display controller driver is not configured yet.")
        return 0

    print("\nUART configuration looks usable.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    if args.command == "config":
        return _print_config(config)
    if args.command == "diagnose":
        return _diagnose(config)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
