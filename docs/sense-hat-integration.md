# Sense HAT integration

The Sense HAT and e-ink display are one cyberdeck status subsystem, implemented across two repositories with a hard responsibility boundary.

## Responsibilities

`cyberdeck-eink` owns physical display concerns: UART selection, wiring metadata, diagnostics and the display-driver boundary.

`pi-environment-panel` owns runtime state: Sense HAT collection, GPS/weather/system state, persistence and the rendered e-ink page.

Do not duplicate Sense HAT access in this repository. Consumers should read the panel state written under the configured panel state directory (`latest.json` by default) rather than opening I2C devices independently.

## Sense HAT data model

The panel records:

- temperature, humidity, pressure and dew point;
- compass heading;
- pitch, roll and yaw;
- accelerometer X/Y/Z;
- gyroscope X/Y/Z;
- derived movement magnitude;
- derived `MOVING` / `STATIONARY` status.

The e-ink page intentionally displays only the field-useful subset: heading, motion state and GPS fix. The complete values remain available in `latest.json`.

## Important hardware note

The standard Raspberry Pi Sense HAT does **not** provide an ambient-light sensor. Display auto-brightness therefore needs a separate light sensor or another source; it is not part of the current Sense HAT integration.

Sense HAT temperature is also affected by heat from the Raspberry Pi and neighbouring HATs. The existing `temperature_offset_c` setting should be calibrated for the assembled deck if the value is intended to approximate ambient temperature.

## Data flow

```text
Sense HAT ----\
GPS -----------+--> pi-environment-panel --> latest.json
UPS -----------+            |
Pi health -----/             +--> e-ink render --> cyberdeck display

cyberdeck-eink --> UART/wiring diagnostics and controller boundary
```

## Extension rule

New cyberdeck sensors should normally be added as collectors in `pi-environment-panel`, represented in its state model, and exposed through `latest.json`. Only display-transport or wiring-specific work belongs in `cyberdeck-eink`.
