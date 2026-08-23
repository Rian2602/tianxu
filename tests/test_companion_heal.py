"""TDD tests for companion healing — RED phase.

Companion healing: pemain bisa heal companion dalam battle dengan Qi cost.
Simplified from 4 cycles to 2 (ponytail: do less).
"""

from __future__ import annotations

from src.engine.battle import companion_hp_max


def _setup_companion(session, registry):
    """Setup companion aktif untuk testing."""
    comp = registry.companions[0]  # first companion from data
    scale = registry.config.get("companion", {})
    hp_max = companion_hp_max(comp, session.state.player.realm_level, scale)
    session.state.companion = {"id": comp["id"], "hp": hp_max, "active": True}
    session.state.companions = [session.state.companion]
    session.state.active_companion = comp["id"]


def test_companion_heal_restores_hp(session, registry):
    """Companion heal mengembalikan HP companion dengan Qi cost."""
    _setup_companion(session, registry)
    comp = session.state.companion
    comp["hp"] = 5  # set HP rendah
    original_qi = session.state.player.qi

    # Heal companion
    session.apply_action({"type": "companion_heal"})

    # Verify: HP naik, Qi berkurang
    assert comp["hp"] > 5, f"companion HP harus naik dari 5, got {comp['hp']}"
    assert session.state.player.qi < original_qi, "Qi harus berkurang"


def test_companion_heal_requires_qi(session, registry):
    """Companion heal gagal jika Qi tidak cukup."""
    _setup_companion(session, registry)
    session.state.companion["hp"] = 5
    session.state.player.qi = 0

    session.apply_action({"type": "companion_heal"})

    # HP tidak berubah
    assert session.state.companion["hp"] == 5, "HP tidak boleh berubah tanpa Qi"
    logs = [e.get("text", "") for e in session.state.log if e.get("type") == "system"]
    assert any("qi" in log.lower() or "tidak" in log.lower() for log in logs), \
        f"harus ada pesan error tentang Qi: {logs[-3:]}"


def test_companion_heal_uses_config_qi_cost(session, registry):
    """Qi cost diambil dari config."""
    registry.config["companion_heal"] = {"qi_cost": 15, "heal_amount": 20}
    _setup_companion(session, registry)
    session.state.companion["hp"] = 5
    session.state.player.qi = 20

    session.apply_action({"type": "companion_heal"})

    assert session.state.player.qi == 5, f"Qi harus 20-15=5, got {session.state.player.qi}"
    assert session.state.companion["hp"] == 25, f"HP harus 5+20=25, got {session.state.companion['hp']}"


def test_companion_heal_caps_at_max_hp(session, registry):
    """Companion heal tidak melebihi max HP."""
    _setup_companion(session, registry)
    from src.engine.battle import companion_stats
    cs = companion_stats(session.state, registry)
    max_hp = cs["hp_max"]
    session.state.companion["hp"] = max_hp - 2  # hampir full

    session.apply_action({"type": "companion_heal"})

    assert session.state.companion["hp"] <= max_hp, \
        f"HP tidak boleh melebihi max {max_hp}, got {session.state.companion['hp']}"


def test_companion_heal_rejects_ko_companion(session, registry):
    """Heal companion yang sudah KO harus ditolak."""
    _setup_companion(session, registry)
    session.state.companion["hp"] = 0
    session.state.companion["active"] = False
    original_qi = session.state.player.qi

    session.apply_action({"type": "companion_heal"})

    assert session.state.companion["hp"] == 0, "HP KO companion tidak boleh berubah"
    assert session.state.player.qi == original_qi, "Qi tidak boleh berkurang"
    logs = [e.get("text", "") for e in session.state.log if e.get("type") == "system"]
    assert any("tidak ada" in log.lower() or "bisa di-heal" in log.lower() for log in logs), \
        f"harus ada pesan error: {logs[-3:]}"
