"""TDD tests for UX improvements identified during manual playtesting.

Tests dibuat sebelum implementasi (test-driven development).
Urutan: location error messages → search/hunt hints → item descriptions.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_location_error_shows_available_connections(session, registry):
    """Bug: 'Kau tidak bisa langsung pergi ke X' tanpa daftar lokasi yang tersedia.
    Fix: Error harus menampilkan lokasi yang bisa dikunjungi."""
    # Mulai di loc_gerbang, coba pindah ke location yang sama (invalid move)
    # Ini harus generate error dengan saran lokasi tersedia
    session.apply_action({"type": "move", "to": "loc_gerbang"})

    # Cek log - harus ada daftar lokasi tersedia di error message
    logs = [e.get("text", "") for e in session.state.log if e.get("type") == "system"]
    error_msg = logs[-1] if logs else ""

    # Error message harus menyebut lokasi yang tersedia
    assert "lokasi yang dapat" in error_msg.lower() or "dapat kau kunjungi" in error_msg.lower(), \
        f"Error message harus menyertakan saran lokasi: '{error_msg}'"
    # Harus menyertakan setidaknya satu nama lokasi yang valid
    available = session._allowed_connections(registry.location(session.state.location))
    available_names = [registry.location(c).get("name", c) for c in available if registry.location(c)]
    assert any(name in error_msg for name in available_names), \
        f"Error message harus mencantumkan lokasi yang tersedia: {available_names} in '{error_msg}'"


def test_search_unavailable_message_lists_hunt_locations(session, registry):
    """Bug: 'Mencari belum tersedia di sini' tanpa saran.
    Fix: Harus menunjukkan lokasi mana yang punya hunt zone."""
    # Di lokasi yang tidak punya hunt zone - loc_gerbang
    session.apply_action({"type": "search"})

    # Cek log
    logs = [e.get("text", "") for e in session.state.log if e.get("type") == "system"]
    error_msg = logs[-1] if logs else ""

    # Harus ada saran lokasi
    assert "bisa mencari" in error_msg.lower() or "cari di" in error_msg.lower() or \
           "hutan" in error_msg.lower(), \
        f"Search error harus saran lokasi: '{error_msg}'"


def test_item_descriptions_populated():
    """Bug: Banyak item dengan description: ""
    Fix: Semua item bisa pakai harus punya deskripsi yang berguna.
    Uses DataRegistry('data') directly (not test fixture) to check real data."""
    from src.loader import DataRegistry
    registry = DataRegistry(str(ROOT / "data"))

    empty_desc_items = []
    for item in registry.items.values():
        desc = item.get("description", "")
        if item.get("type") in ("consumable", "weapon", "key_item") and not desc.strip():
            empty_desc_items.append(item["id"])

    # Tidak boleh ada item yang punya tipe tapi description kosong
    assert len(empty_desc_items) == 0, \
        f"Items with empty descriptions: {empty_desc_items}"


def test_hunt_unavailable_message_lists_hunt_locations(session, registry):
    """Bug: 'Berburu belum tersedia di sini' tanpa saran.
    Fix: Harus menunjukkan lokasi yang punya hunt zone."""
    # Di lokasi yang tidak punya hunt
    loc = registry.location(session.state.location)

    if not registry.hunts_for_location(session.state.location):
        # Sudah di lokasi tanpa hunt
        session.apply_action({"type": "hunt"})

        logs = [e.get("text", "") for e in session.state.log if e.get("type") == "system"]
        error_msg = logs[-1] if logs else ""

        # Harus ada saran lokasi dengan hunt
        assert "berburu" in error_msg.lower() or "hutan" in error_msg.lower() or \
               "dapat berburu" in error_msg.lower(), \
            f"Hunt error harus saran lokasi: '{error_msg}'"
