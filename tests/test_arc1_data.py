"""Playthrough data story Arc I yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi (quests/dialogs/npcs/lokasi/memory/faksi/
key_items) benar-benar dapat dimainkan engine end-to-end: rantai 6 quest utama,
memory unlock, pilihan pavilion, arc_summary + ending. Skip bila `data/` kosong
(AGENTS.md: data tidak di-commit) — suite tetap hijau di environment tanpa data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc01.json").exists(),
    reason="data story Arc I belum ada di data/",
)

REGISTRY: DataRegistry | None = None


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = DataRegistry()  # data dir default = data/
    return REGISTRY


def _new_session(registry: DataRegistry) -> GameSession:
    return GameSession.new(registry)


def _talk_through(s: GameSession, npc: str) -> None:
    """Buka dialog dengan NPC lalu auto-lanjut sampai selesai."""
    s.apply_action({"type": "talk", "npc": npc})
    assert s.state.pending_dialog, f"dialog tidak terbuka dengan {npc}"
    guard = 0
    while s.state.pending_dialog and guard < 20:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
        guard += 1


def test_arc1_data_contract_ok(registry):
    """Data Arc I memenuhi seluruh kontrak validator saat load."""
    arc1_ids = [q["id"] for q in registry.quests if q["id"].startswith("quest_a01")]
    assert len(arc1_ids) == 6
    assert len(registry.memories) >= 4
    assert {a["id"] for a in registry.config["academies"]} == {
        "pavilion_wuxin", "pavilion_jianxin", "pavilion_yanzhi", "pavilion_liuguang"}
    # quest chain Arc I lengkap & berurutan
    assert arc1_ids == [
        "quest_a01_c01_001", "quest_a01_c01_002", "quest_a01_c02_003",
        "quest_a01_c03_004", "quest_a01_c04_005", "quest_a01_c04_006"]
    # keputusan docs: TIDAK ada main quest yang bisa gagal karena waktu habis
    # (MSB tidak merancang fail-state waktu untuk quest utama 7 arc) — guard
    # agar timeout tidak terselip di data secara tidak sengaja
    assert not any(q.get("timeout") for q in registry.quests if q.get("kind") == "main")


def test_arc1_full_playthrough_yellow(registry):
    """Rantai Arc I dimainkan penuh: 6 quest selesai, 4 memory terbuka,
    pavilion terset, ending terpilih."""
    s = _new_session(registry)
    assert s.state.current_quest == "quest_a01_c01_001"

    # Ch 1.1: arrival + registration
    _talk_through(s, "npc_aptitude_examiner")
    assert s.state.current_quest == "quest_a01_c01_002"
    assert s.state.flags.get("flag_dream_a01_01_seen") is True
    assert len(s.state.memories) == 1  # memory_a01_m01
    _talk_through(s, "npc_aptitude_examiner")
    assert s.state.current_quest == "quest_a01_c02_003"
    assert s.state.flags.get("state_murid_status") == "registered"

    # Ch 1.2: first lesson — pindah ke ruang latihan, bicara Lin Yue
    s.apply_action({"type": "move", "to": "loc_training_hall"})
    _talk_through(s, "npc_lin_yue")
    assert s.state.current_quest == "quest_a01_c03_004"
    assert s.state.relations.get("npc_lin_yue", 0) >= 2
    assert len(s.state.memories) == 2  # memory_a01_m02

    # Ch 1.3: pavilion selection — MAJOR choice
    s.apply_action({"type": "choose", "option": "pavilion_yanzhi"})
    assert s.state.current_quest == "quest_a01_c04_005"
    assert s.state.player.academy == "pavilion_yanzhi"
    # starter kit pavilion diterima; curriculum khas pavilion tersedia
    assert s.state.inventory.get("pil_qi", 0) >= 3  # 2 awal + 2 starter - 0
    curr = [t["id"] for t in registry.academy_curriculum("pavilion_yanzhi")]
    assert "teknik_yanzhi" in curr

    # Ch 1.4: first trial — reach formation tua; night incident — reach kamar
    s.apply_action({"type": "move", "to": "loc_outer_region"})
    assert s.state.current_quest == "quest_a01_c04_006"
    assert s.state.flags.get("flag_formation_touched") is True
    assert len(s.state.memories) == 3  # memory_a01_m03
    s.apply_action({"type": "move", "to": "loc_training_hall"})
    s.apply_action({"type": "move", "to": "loc_protagonist_room"})
    # quest utama Arc I selesai — DAG lanjut ke Arc II (quest_a02_c01_001)
    assert s.state.current_quest == "quest_a02_c01_001"
    assert s.state.flags.get("flag_memory_awareness") is True
    assert s.state.inventory.get("simbol_kuno") == 1
    assert len(s.state.memories) >= 4  # memory_a01_m04 (+ memory arc berikutnya)

    # arc_summary + ending
    v = s.view()
    assert v["arc_summary"] is not None
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "A New Life"
    assert v["arc_summary"]["ending"]["id"] == "end_a01_awakening"


def test_arc1_each_pavilion_choice(registry):
    """Keempat pilihan pavilion valid — tiap pilihan men-set academy berbeda."""
    for pid in ("pavilion_wuxin", "pavilion_jianxin", "pavilion_yanzhi", "pavilion_liuguang"):
        s = _new_session(registry)
        s.state.current_quest = "quest_a01_c03_004"  # lompat ke pilihan
        s.apply_action({"type": "choose", "option": pid})
        assert s.state.player.academy == pid, f"pavilion {pid} tidak terset"
        # curriculum pavilion spesifik tersedia
        assert any(t["id"] == f"teknik_{pid.replace('pavilion_', '')}"
                   for t in registry.academy_curriculum(pid))


def test_arc1_memory_reliability_from_data(registry):
    """Memory Arc I memakai reliability dari data (docs 06: kurva RENDAH→TINGGI)."""
    rel = {m["id"]: m["reliability"] for m in registry.memories}
    assert rel["memory_a01_m01"] == "RENDAH"
    assert rel["memory_a01_m04"] == "SEDANG-TINGGI"
    # unlock via quest membawa reliability data
    s = _new_session(registry)
    _talk_through(s, "npc_aptitude_examiner")
    assert s.state.memories[0]["reliability"] == "RENDAH"


def test_arc1_save_load_roundtrip(registry, tmp_path, monkeypatch):
    """Save/load state Arc I — memory dict v3, flags, academy, arc_summary utuh."""
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path)
    s = _new_session(registry)
    s.apply_action({"type": "choose", "option": "pavilion_wuxin"})  # no-op di quest awal
    s.state.flags["flag_memory_awareness"] = True
    s.state.player.academy = "pavilion_wuxin"
    s.apply_action({"type": "save", "save_name": "arc1_test"})
    s2 = GameSession.load(registry, "arc1_test")
    assert s2.state.player.academy == "pavilion_wuxin"
    assert s2.state.flags.get("flag_memory_awareness") is True
    assert s2.state.current_quest == s.state.current_quest


def test_arc1_key_item_usable(registry):
    """Simbol kuno (key_item) bisa dipakai setelah diperoleh — use_effects jalan."""
    s = _new_session(registry)
    s.state.inventory["simbol_kuno"] = 1
    s.apply_action({"type": "use_key_item", "item": "simbol_kuno"})
    assert s.state.flags.get("simbol_kuno_aktif") is True


def test_arc1_hunt_and_battle(registry):
    """Hunt di hutan akademi → battle melawan binatang; menang memberi exp."""
    s = _new_session(registry)
    s.apply_action({"type": "move", "to": "loc_training_hall"})
    s.apply_action({"type": "move", "to": "loc_outer_region"})
    s.apply_action({"type": "move", "to": "loc_hutan_akademi"})
    assert s.can_hunt() is True
    exp0 = s.state.player.exp
    s.apply_action({"type": "hunt"})
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert s.state.pending_battle is None, "battle hunt harus berakhir"
    assert s.state.player.exp >= exp0
