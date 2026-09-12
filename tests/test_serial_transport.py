from dataclasses import replace
from unittest.mock import Mock

import pytest

from cyberdeck_eink.config import load_config
from cyberdeck_eink import serial_transport as transport


def test_default_records_existing_application_settings():
    config = load_config().display
    assert config.baud_rate == 115200
    assert config.expected_serial_device == '/dev/ttyAMA10'


def test_unknown_baud_never_opens_port(monkeypatch):
    constructor = Mock()
    monkeypatch.setattr(transport.serial, 'Serial', constructor)
    with pytest.raises(ValueError, match='baud rate is unverified'):
        transport.open_serial(replace(load_config().display, baud_rate=None))
    constructor.assert_not_called()


def test_regular_file_is_not_uart(tmp_path, monkeypatch):
    path = tmp_path / 'serial0'
    path.write_text('not a UART')
    config = replace(load_config().display, serial_device=str(path), baud_rate=9600,
                     expected_serial_device=None)
    constructor = Mock()
    monkeypatch.setattr(transport.serial, 'Serial', constructor)
    assert transport.serial_diagnostics(config)['character_device'] is False
    with pytest.raises(ValueError, match='character device'):
        transport.open_serial(config)
    constructor.assert_not_called()


def test_wrong_alias_target_never_opens_port(tmp_path, monkeypatch):
    path = tmp_path / 'serial0'
    path.symlink_to('/dev/null')
    config = replace(load_config().display, serial_device=str(path), baud_rate=9600)
    constructor = Mock()
    monkeypatch.setattr(transport.serial, 'Serial', constructor)
    assert transport.serial_diagnostics(config)['mapping_matches'] is False
    with pytest.raises(ValueError, match='unexpected device'):
        transport.open_serial(config)
    constructor.assert_not_called()


def test_transport_uses_resolved_port_and_exclusive_8n1(tmp_path, monkeypatch):
    path = tmp_path / 'serial0'
    path.symlink_to('/dev/null')
    config = replace(load_config().display, serial_device=str(path), baud_rate=9600,
                     expected_serial_device='/dev/null')
    constructor = Mock()
    monkeypatch.setattr(transport.serial, 'Serial', constructor)
    transport.open_serial(config)
    constructor.assert_called_once_with(
        port='/dev/null', exclusive=True, bytesize=8, parity='N', stopbits=1,
        xonxoff=False, rtscts=False, dsrdtr=False, baudrate=9600,
        timeout=2.0, write_timeout=2.0,
    )


def test_diagnostics_never_open_port(monkeypatch):
    constructor = Mock()
    monkeypatch.setattr(transport.serial, 'Serial', constructor)
    transport.serial_diagnostics(load_config().display)
    constructor.assert_not_called()
