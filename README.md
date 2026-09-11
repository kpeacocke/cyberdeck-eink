# Cyberdeck E-Ink

A small Python project for driving and testing the UART-connected e-ink display in KP's Raspberry Pi 5 cyberdeck.

The project keeps hardware settings out of application code. The committed defaults describe KP's deck, while other users can copy `config/example.yaml` and override the serial device, baud rate, rotation and wiring metadata without changing Python.

## Current scope

The first version deliberately does three things:

1. loads and validates display configuration;
2. diagnoses the configured UART device on Raspberry Pi OS; and
3. provides a clean driver boundary for the display-specific protocol once the exact e-ink controller is confirmed.

It does **not** guess at the controller protocol or GPIO pin mapping. Sending arbitrary bytes to an unknown display controller is a bad hardware test.

## KP cyberdeck defaults

- Deck address: `192.168.1.29`
- SSH user: `kpeacocke`
- Authentication: SSH key (never stored in this repository)
- Display interface: UART
- Raspberry Pi serial alias: `/dev/serial0`
- Baud rate: `115200`

See [`config/default.yaml`](config/default.yaml).

## Install on the deck

```bash
ssh kpeacocke@192.168.1.29
git clone https://github.com/kpeacocke/cyberdeck-eink.git
cd cyberdeck-eink
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Diagnose the connection

```bash
cyberdeck-eink diagnose
```

or with another settings file:

```bash
cyberdeck-eink --config ~/my-display.yaml diagnose
```

The diagnostic checks whether the configured serial alias exists, what it resolves to, whether the current user can read/write it, and reports the loaded settings.

## Show configuration

```bash
cyberdeck-eink config
```

## Configuration precedence

1. an explicit `--config PATH` file;
2. `CYBERDECK_EINK_CONFIG` environment variable;
3. `config/default.yaml` from this repository/package.

For another build, copy the example:

```bash
cp config/example.yaml config/local.yaml
cyberdeck-eink --config config/local.yaml diagnose
```

## Project layout

```text
config/                 Hardware and connection settings
docs/                   Wiring and hardware notes
src/cyberdeck_eink/     Python package
tests/                  Configuration tests
```

## Next hardware step

Confirm the exact e-ink controller/model and KP's final colour-to-header-pin mapping. Once confirmed, add a controller driver under `src/cyberdeck_eink/drivers/` and replace the `null` wiring fields in `config/default.yaml` with the observed values.

## Licence

MIT. See [`LICENSE`](LICENSE).
