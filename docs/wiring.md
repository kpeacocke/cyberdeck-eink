# Wiring

This document records the physical connection between the Raspberry Pi 5 and the cyberdeck e-ink display.

## KP cyberdeck

The software defaults are already committed in `config/default.yaml`:

- interface: UART
- serial alias: `/dev/serial0`
- baud: `115200`

The final physical header mapping has **not** been committed because it has not yet been verified from the deck itself.

| Signal | Wire colour | Physical pin | GPIO | Status |
| --- | --- | ---: | ---: | --- |
| TX | TBD | TBD | TBD | verify on deck |
| RX | TBD | TBD | TBD | verify on deck |
| Power | TBD | TBD | n/a | verify on deck |
| Ground | TBD | TBD | n/a | verify on deck |

## Why `/dev/serial0`

Use Raspberry Pi OS's serial alias rather than baking a specific `ttyAMA*` device into the application. The alias follows the UART selected by the operating-system configuration and is less brittle when overlays or UART assignments change.

To see what it currently maps to:

```bash
readlink -f /dev/serial0
```

The project diagnostic reports the same information:

```bash
cyberdeck-eink diagnose
```

## Verification commands

Run these on the Pi before changing wiring or enabling a display driver:

```bash
ls -l /dev/serial* /dev/ttyAMA* 2>/dev/null
readlink -f /dev/serial0
id
pinctrl get
```

Do not commit SSH keys, passwords, tokens or other credentials to this repository.
