"""Test kompanion — jalur Summoning (ENGINE_ARCHITECTURE §9.4).

Kasus:
- Pemberian: pilih akademi Summoning → dapat 1 binatang roh; jalur lain tidak.
- Battle: kompanion bertindak otomatis tiap giliran (serangan dasar).
- Musuh bisa menyerang kompanion (punya HP sendiri); KO → tidak aktif.
- Rest di titik aman membangkitkan kompanion.
- Scaling: stat = base + level × scale; level = level ranah pemain.
"""

from __future__ import annotations

import random

from src.engine.battle import companion_stats
from src.engine.cultivation import gain_exp
from src.engine.session import GameSession
from src.loader import DataRegistry


def _finish_dialog(session: GameSession) -> None:
    while session.state.pending_dialog:
        v = session.dialog.view()
        if v["choices"]:
            session.apply_action({"type": "dialog_choice", "choice_index": 0})
        else:
            session.apply_action({"type": "dialog_choice", "choice_index": -1})


def choose_academy(session: GameSession, academy: str) -> None:
    """Selesaikan quest ujian & pilih akademi (god_mode: spar menang 1 serangan)."""
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    _finish_dialog(session)
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    _finish_dialog(session)
    session.apply_action({"type": "move", "to": "loc_arena"})
    session.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    _finish_dialog(session)
    session.apply_action({"type": "battle_action", "action": "attack"})  # menang spar (god_mode)
    session.apply_action({"type": "choose", "option": academy})


def _grant_direct(session: GameSession) -> None:
    """Skenario langsung: pemain sudah di jalur Summoning dengan kompanion aktif."""
    session.state.player.academy = "akademi_summoning"
    comp = next(c for c in session.reg.companions if c["id"] == "komp_roh_awan")
    scale = session.reg.config.get("companion", {})
    hp_max = int(comp["base_hp"]) + session.state.player.realm_level * int(scale.get("hp_per_level", 12))
    session.state.companion = {"id": "komp_roh_awan", "hp": hp_max, "active": True}


def _to_hunting(session: GameSession, from_arena: bool = False) -> None:
    """Pindah ke Wilayah Berburu lalu mulai berburu (jalur koneksi valid)."""
    if from_arena:
        session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "move", "to": "loc_gerbang_akademi"})
    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    assert session.state.pending_battle


def test_pemberian_kompanion_jalur_summoning(session: GameSession, god_mode) -> None:
    choose_academy(session, "akademi_summoning")
    assert session.state.companion is not None
    assert session.state.companion["id"] == "komp_roh_awan"
    assert session.state.companion["active"] is True


def test_jalur_lain_tanpa_kompanion(session: GameSession, god_mode) -> None:
    choose_academy(session, "akademi_elemen")
    assert session.state.player.academy == "akademi_elemen"  # pilihan benar-benar terdaftar
    assert session.state.companion is None


def test_kompanion_bertindak_otomatis(session: GameSession, god_mode) -> None:
    """Kompanion menyerang sendiri — pemain bertahan saja, musuh tetap mati."""
    choose_academy(session, "akademi_summoning")
    _to_hunting(session, from_arena=True)
    session.apply_action({"type": "battle_action", "action": "guard"})  # pemain tidak menyerang
    assert not session.state.pending_battle  # kompanion yang menghabisi musuh


def test_musuh_bisa_menyerang_kompanion(session: GameSession, monkeypatch) -> None:
    """Musuh 50% menarget kompanion — dipaksa random → HP kompanion turun."""
    _grant_direct(session)
    _to_hunting(session)
    before = session.state.companion["hp"]
    monkeypatch.setattr(random, "random", lambda: 0.0)  # selalu target kompanion
    session.apply_action({"type": "battle_action", "action": "guard"})
    after = session.state.companion["hp"]
    assert after < before


def test_kompanion_ko_dan_bangkit_saat_rest(session: GameSession, monkeypatch) -> None:
    _grant_direct(session)
    session.state.companion["hp"] = 1  # sekarat → 1 serangan musuh cukup untuk KO
    _to_hunting(session)
    monkeypatch.setattr(random, "random", lambda: 0.0)  # musuh selalu serang kompanion
    session.apply_action({"type": "battle_action", "action": "guard"})
    assert session.state.companion["active"] is False

    # akhiri battle (kabur berhasil — random dipaksa 0.0), lalu rest di titik aman
    session.apply_action({"type": "battle_action", "action": "flee"})
    assert not session.state.pending_battle
    session.apply_action({"type": "move", "to": "loc_gerbang_akademi"})
    session.apply_action({"type": "move", "to": "loc_pasar"})
    session.apply_action({"type": "rest"})
    assert session.state.companion["active"] is True
    comp = companion_stats(session.state, session.reg)
    assert session.state.companion["hp"] == comp["hp_max"]


def test_scaling_stat_kompanion(session: GameSession, registry: DataRegistry) -> None:
    _grant_direct(session)
    comp = companion_stats(session.state, registry)
    assert comp["hp_max"] == 20 + 1 * 12  # base_hp + level×hp_per_level
    assert comp["attack"] == 5 + 1 * 2
    # naik level → stat ikut naik
    gain_exp(session.state, registry, 10)  # cukup untuk level 2
    comp2 = companion_stats(session.state, registry)
    assert comp2["hp_max"] == 20 + 2 * 12
    assert comp2["attack"] == 5 + 2 * 2
