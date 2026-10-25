# Whisker Ting Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/aidenmitchell/ha-whisker-ting.svg)](https://github.com/aidenmitchell/ha-whisker-ting/releases)

Home Assistant integration for [Whisker Labs Ting](https://www.tingfire.com/) electrical fire safety sensors.

## Features

- **Real-time voltage monitoring** via WebSocket connection
  - Current voltage
  - Voltage high/low
  - Average peaks
- **Fire hazard status** monitoring
  - Electrical Fire Hazard (EFH) detection
  - Utility Fire Hazard (UFH) detection
  - Learning mode status
- **Device diagnostics**
  - Firmware version
  - WiFi/Bluetooth MAC addresses
  - Serial number

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/aidenmitchell/ha-whisker-ting` as an Integration
5. Click "Download" on the Whisker Ting integration
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/aidenmitchell/ha-whisker-ting/releases)
2. Extract and copy the `custom_components/whisker_ting` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Whisker Ting"
4. Enter your Whisker Labs account credentials (email and password)

## Sensors

| Sensor | Description |
|--------|-------------|
| Current voltage | Real-time voltage reading (WebSocket) |
| Voltage high | Peak high voltage |
| Voltage low | Peak low voltage |
| Hazard status | Overall hazard status (no_hazards, hazard_detected, learning) |
| EFH status | Electrical Fire Hazard status |
| UFH status | Utility Fire Hazard status |

## Binary Sensors

| Sensor | Description |
|--------|-------------|
| Fire hazard | On when any fire hazard is detected |
| Learning mode | On when the device is in learning mode |

## Requirements

- Home Assistant 2024.1.0 or newer (minimum declared in `hacs.json`; tested on 2026.10.2, see below)
- Whisker Labs Ting device
- Whisker Labs account

## Dependencies and security audit

The integration has one runtime requirement of its own and uses one package
that Home Assistant core already ships:

| Package | Who provides it | Version |
|---------|-----------------|---------|
| `msgpack` | this integration (`manifest.json` `requirements`) | `==1.2.3`, exact pin |
| `aiohttp` | Home Assistant core | whatever your HA release pins (3.14.5 in 2026.10.2) |

Rules this repo follows:

- `aiohttp` is **not** listed in `manifest.json`. Home Assistant pins it in
  `homeassistant/package_constraints.txt`; re-declaring it can only conflict
  with core. The integration uses HA's shared session
  (`async_get_clientsession`).
- `msgpack` is an exact pin. Home Assistant core does not pin `msgpack`, so
  this does not fight HA's constraints. 1.2.3 is above the fix for
  GHSA-6v7p-g79w-8964 / CVE-2026-57585 (fixed in 1.2.1) and ships wheels for
  Python 3.14 on manylinux and musllinux (HA OS / container).
- Tested platform: Home Assistant 2026.10.2, Python 3.14, via
  `pytest-homeassistant-custom-component==0.13.373` (see `requirements_test.txt`).

Reproducible audit input:

- `requirements/ha-2026.10.2-constraints.txt` is a verbatim copy of HA
  2026.10.2's `package_constraints.txt`.
- `requirements/audit-closure.txt` is the integration's resolved runtime
  closure (direct + transitive) under those constraints.
- `script/audit_deps.sh` re-resolves the closure with `uv`, fails if it drifted
  from the committed file, then runs `pip-audit` on it. Use `--update` after a
  deliberate bump.

When moving to a new HA release: copy that release's `package_constraints.txt`
into `requirements/`, bump `HA_VERSION` in `script/audit_deps.sh`, the
harness in `requirements_test.txt` and `TESTED_HA_VERSION` in
`tests/test_dependencies.py`, then run `script/audit_deps.sh --update` and the
tests.

```bash
uv venv -p 3.14 .venv
uv pip install -p .venv/bin/python -r requirements_test.txt
.venv/bin/python -m pytest
script/audit_deps.sh
```

## Troubleshooting

### Voltage shows "Unknown" briefly on startup

This is normal - the integration waits for the WebSocket connection to receive its first data packet before displaying values.

### Authentication errors

Ensure you're using the same email and password you use in the Whisker Labs mobile app.

## Credits

This integration is not affiliated with or endorsed by Whisker Labs, Inc.

## License

MIT License - see [LICENSE](LICENSE) for details.
