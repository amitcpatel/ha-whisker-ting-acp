"""Dependency guard tests for the whisker_ting integration.

These are offline tests. They check that the runtime requirements in
manifest.json stay consistent with the Home Assistant release we test on,
and that the committed audit closure is above every known advisory fix.
"""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "custom_components" / "whisker_ting" / "manifest.json"
CONSTRAINTS = ROOT / "requirements" / "ha-2026.10.2-constraints.txt"
CLOSURE = ROOT / "requirements" / "audit-closure.txt"
REQUIREMENTS_TEST = ROOT / "requirements_test.txt"

TESTED_HA_VERSION = "2026.10.2"

# Highest first-patched version per package, from the advisory databases:
# msgpack  GHSA-6v7p-g79w-8964 / CVE-2026-57585 (Unpacker reuse OOB read) fixed in 1.2.1
# aiohttp  CVE-2026-111063..111066, 111748..111750, GHSA-2g87-pp6c-29x5 fixed in 3.14.4
FIX_FLOORS = {"msgpack": Version("1.2.1"), "aiohttp": Version("3.14.4")}


def _pins(path: Path) -> dict[str, Version]:
    pins: dict[str, Version] = {}
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "==" not in line:
            continue
        req = Requirement(line)
        (spec,) = req.specifier
        pins[req.name.lower().replace("_", "-")] = Version(spec.version)
    return pins


def _manifest_requirements() -> list[Requirement]:
    return [Requirement(r) for r in json.loads(MANIFEST.read_text())["requirements"]]


def test_manifest_requirements_are_exact_pins() -> None:
    for req in _manifest_requirements():
        specs = list(req.specifier)
        assert len(specs) == 1 and specs[0].operator == "==", (
            f"{req} is not an exact pin"
        )


def test_manifest_does_not_override_ha_core_pins() -> None:
    """HA core owns aiohttp and friends; the manifest must not re-declare them."""
    core = _pins(CONSTRAINTS)
    for req in _manifest_requirements():
        name = req.name.lower().replace("_", "-")
        if name in core:
            (spec,) = req.specifier
            assert Version(spec.version) == core[name], (
                f"{req} conflicts with Home Assistant {TESTED_HA_VERSION} pin {core[name]}"
            )
    names = {r.name.lower() for r in _manifest_requirements()}
    assert "aiohttp" not in names, "aiohttp is provided by Home Assistant core"


def test_closure_matches_manifest_and_ha_constraints() -> None:
    closure = _pins(CLOSURE)
    core = _pins(CONSTRAINTS)
    for req in _manifest_requirements():
        (spec,) = req.specifier
        assert closure[req.name.lower()] == Version(spec.version)
    for name, version in closure.items():
        if name in core:
            assert version == core[name], (
                f"closure {name} {version} != HA pin {core[name]}"
            )


def test_closure_is_above_advisory_fix_floors() -> None:
    closure = _pins(CLOSURE)
    for name, floor in FIX_FLOORS.items():
        assert closure[name] >= floor, f"{name} {closure[name]} < fixed {floor}"


def test_test_environment_matches_pins() -> None:
    """The installed test env is the one the pins describe."""
    assert importlib.metadata.version("homeassistant") == TESTED_HA_VERSION
    harness = _pins(REQUIREMENTS_TEST)
    assert (
        Version(importlib.metadata.version("pytest-homeassistant-custom-component"))
        == harness["pytest-homeassistant-custom-component"]
    )
    for req in _manifest_requirements():
        (spec,) = req.specifier
        assert importlib.metadata.version(req.name) == spec.version
    core = _pins(CONSTRAINTS)
    assert Version(importlib.metadata.version("aiohttp")) == core["aiohttp"]


def test_signalr_framing_with_pinned_msgpack() -> None:
    """The pinned msgpack still produces the exact SignalR ping frame."""
    from custom_components.whisker_ting.websocket import WhiskerWebSocket

    ws = WhiskerWebSocket.__new__(WhiskerWebSocket)
    ws._message_id = 0
    assert ws._encode_ping() == b"\x02\x91\x06"
    frame = ws._encode_invocation("StreamVoltage", ["abc"])
    assert frame[0] == len(frame) - 1  # one-byte LEB128 length prefix
    assert frame[1:] == b"\x96\x01\x80\xa11\xadStreamVoltage\x91\xa3abc\x90"
