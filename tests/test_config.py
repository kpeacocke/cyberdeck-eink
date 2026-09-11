from pathlib import Path

import pytest

from cyberdeck_eink.config import load_config


def test_load_valid_config(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
device:
  name: Test Deck
  host: test.local
  ssh_user: tester

display:
  interface: uart
  serial_device: /dev/serial0
  baud_rate: 115200
  timeout_seconds: 2.0
  rotation: 0
  driver: unconfigured
""".strip(),
        encoding="utf-8",
    )

    config = load_config(str(config_file))

    assert config.device.name == "Test Deck"
    assert config.device.host == "test.local"
    assert config.display.serial_device == "/dev/serial0"
    assert config.display.baud_rate == 115200


def test_rejects_invalid_rotation(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
device:
  name: Test Deck
  host: test.local
  ssh_user: tester

display:
  interface: uart
  serial_device: /dev/serial0
  baud_rate: 115200
  timeout_seconds: 2.0
  rotation: 45
  driver: unconfigured
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="rotation"):
        load_config(str(config_file))
