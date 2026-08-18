"""Playthrough data story Arc V yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc V benar-benar dapat dimainkan engine
end-to-end: 5 quest (Spiritual Collapse → Mountain Gate MAJOR → Family Crisis
4-status → Entity → memory besar), branch Mountain Gate 2-cabang (changed vs
repeated — docs 03b: MAJOR outcome), Family Crisis 4-status sesuai keputusan
(docs 04: status found family), Entity first contact (docs 09 world event),
memory_a05_m01 reliability TINGGI, arc_summary + ending. Skip bila data
Arc I-IV tidak ada.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc05.json").exists(),
    reason="data story Arc V belum ada di data/",
)

REGISTRY: DataRegistry | None = None


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = DataRegistry()
    return REGISTRY


def _new_session(registry: DataRegistry) -> GameSession:
    return GameSession.new(registry)


def _talk(s: GameSession, npc: str, *, close: bool = True) -> None:
    """Buka dialog dengan NPC; auto-lanjut sampai selesai (atau tutup 1x)."""
    s.apply_action({"type": "talk", "npc": npc})
    assert s.state.pending_dialog, f"dialog tidak terbuka dengan {npc} @ {s.state.location}"
    if close:
        guard = 0
        while s.state.pending_dialog and guard < 20:
            s.apply_action({"type": "dialog_choice", "choice_index": -1})
            guard += 1


def _spar_win(s: GameSession, npc: str) -> None:
    s.apply_action({"type": "spar", "npc": npc})
    assert s.state.pending_battle, "spar tidak membuka battle"
    guard = 0
    while s.state.pending_battle and guard < 40:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert s.state.pending_battle is None, "battle spar tidak berakhir"


def _reach(s: GameSession, loc: str) -> None:
    s.apply_action({"type": "move", "to": loc})


def _through_arc1_2_3_4(registry, branch_idx: int = 1) -> GameSession:
    """Mainkan Arc I + II + III + IV penuh sampai quest_a05_c01_001."""
    s = _new_session(registry)
    # Arc I
    _talk(s, "npc_aptitude_examiner")
    _talk(s, "npc_aptitude_examiner")
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue")
    s.apply_action({"type": "choose", "option": "pavilion_jianxin"})
    _reach(s, "loc_outer_region")
    _reach(s, "loc_training_hall")
    _reach(s, "loc_protagonist_room")
    # Arc II
    _reach(s, "loc_training_hall")
    _talk(s, "npc_proctor"); _spar_win(s, "npc_proctor")
    _talk(s, "npc_proctor"); _spar_win(s, "npc_proctor")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.apply_action({"type": "dialog_choice", "choice_index": branch_idx})
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    # Arc III
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_hidden_room_mural")
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mo_chen_meeting")
    _talk(s, "npc_mo_chen")
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _talk(s, "npc_archive_clerk")
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.apply_action({"type": "dialog_choice", "choice_index": 2})  # seek_truth
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_hidden_room_mural")
    # Arc IV
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_training_hall")
    _reach(s, "loc_archive_public")
    _talk(s, "npc_archive_clerk")
    _reach(s, "loc_training_hall"); _reach(s, "loc_pavilion_yanzhi")
    _talk(s, "npc_mei_ruo")
    _talk(s, "npc_mei_ruo")
    _reach(s, "loc_training_hall"); _reach(s, "loc_grandmaster_chamber")
    _talk(s, "npc_grandmaster")
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    assert s.state.current_quest == "quest_a05_c01_001", s.state.current_quest
    return s


def test_arc5_data_contract_ok(registry):
    """Kontrak validator: quest Arc V lengkap + arc_05 di config + NPC/lokasi/memory baru."""
    ids = [q["id"] for q in registry.quests]
    for qid in ("quest_a05_c01_001", "quest_a05_c02_002", "quest_a05_c03_003",
                "quest_a05_c04_004", "quest_a05_c05_005"):
        assert qid in ids, qid
    assert ids.index("quest_a05_c01_001") < ids.index("quest_a05_c05_005")
    # quest Arc IV terakhir menyambung ke Arc V
    q404 = next(q for q in registry.quests if q["id"] == "quest_a04_c04_004")
    assert q404.get("next") == [{"quest": "quest_a05_c01_001"}]
    # NPC + lokasi baru
    for nid in ("npc_villager_elder", "npc_mountain_guard", "npc_entity"):
        assert nid in registry.npc_by_id, nid
    for lid in ("loc_affected_village", "loc_mountain_gate"):
        assert lid in registry.location_by_id, lid
    # config arc_05
    assert registry.config["arcs"][4]["id"] == "arc_05"
    assert registry.config["arcs"][4]["final_quest"] == "quest_a05_c05_005"
    # memory besar Arc V
    assert "memory_a05_m01" in registry.memory_by_id
    # dialog branch terdaftar
    assert registry.dialog("dlg_a05_branch_mg") is not None
    assert registry.dialog("dlg_a05_branch_family") is not None


def test_arc5_spiritual_collapse_and_mountain_gate(registry):
    """Q1 Spiritual Collapse → Q2 Mountain Gate MAJOR → dialog pilihan 2-cabang."""
    s = _through_arc1_2_3_4(registry)
    # keluar dari ruang terdalam menuju desa terdampak
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region")
    _reach(s, "loc_affected_village")
    _talk(s, "npc_villager_elder")
    assert s.state.current_quest == "quest_a05_c02_002"
    assert s.state.flags.get("world_event_a05_spiritual_collapse") == "active"
    # Q2: gerbang gunung → branch dialog
    _reach(s, "loc_outer_region"); _reach(s, "loc_mountain_gate")
    _talk(s, "npc_mountain_guard", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.branch_pending == "dlg_a05_branch_mg"
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # changed
    assert s.state.current_quest == "quest_a05_c03_003"
    assert s.state.flags.get("flag_mountain_gate_changed") is True
    assert s.state.relations.get("npc_lin_yue", 0) >= 2


@pytest.mark.parametrize("idx,flag,rel_npc,rel_min", [
    (0, "flag_mountain_gate_changed", "npc_lin_yue", 2),
    (1, "flag_mountain_gate_repeated", "npc_gu_han", 2),
])
def test_arc5_mountain_gate_two_branches(registry, idx, flag, rel_npc, rel_min):
    """MAJOR outcome Mountain Gate: 2 cabang → flag + relation berbeda → konvergen."""
    s = _through_arc1_2_3_4(registry)
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region")
    _reach(s, "loc_affected_village")
    _talk(s, "npc_villager_elder")
    _reach(s, "loc_outer_region"); _reach(s, "loc_mountain_gate")
    _talk(s, "npc_mountain_guard", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.apply_action({"type": "dialog_choice", "choice_index": idx})
    assert s.state.current_quest == "quest_a05_c03_003", f"{flag} harus konvergen"
    assert s.state.flags.get(flag) is True
    assert s.state.relations.get(rel_npc, 0) >= rel_min


@pytest.mark.parametrize("idx,status_map,rel_npc,rel_min", [
    (0, {"state_lin_yue_status": "loyal", "state_mei_ruo_status": "loyal",
         "state_shen_luo_status": "separated", "state_gu_han_status": "disillusioned"},
     "npc_lin_yue", 3),
    (1, {"state_shen_luo_status": "loyal", "state_gu_han_status": "loyal",
         "state_lin_yue_status": "separated", "state_mei_ruo_status": "disillusioned"},
     "npc_shen_luo", 3),
    (2, {"state_mei_ruo_status": "loyal", "state_lin_yue_status": "loyal",
         "state_gu_han_status": "separated", "state_shen_luo_status": "disillusioned"},
     "npc_mei_ruo", 3),
    (3, {"state_lin_yue_status": "separated", "state_shen_luo_status": "separated",
         "state_mei_ruo_status": "disillusioned", "state_gu_han_status": "disillusioned"},
     "npc_gu_han", 0),
])
def test_arc5_family_crisis_four_branches(registry, idx, status_map, rel_npc, rel_min):
    """Found Family Crisis: 4 keputusan → status tiap anggota berbeda (docs 04) → konvergen."""
    s = _through_arc1_2_3_4(registry)
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region")
    _reach(s, "loc_affected_village")
    _talk(s, "npc_villager_elder")
    _reach(s, "loc_outer_region"); _reach(s, "loc_mountain_gate")
    _talk(s, "npc_mountain_guard", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # changed
    # Q3: family crisis → dialog krisis → branch dialog (talk anggota found family)
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    for npc in ("npc_lin_yue", "npc_shen_luo", "npc_mei_ruo", "npc_gu_han"):
        s.apply_action({"type": "talk", "npc": npc})
        if s.state.pending_dialog:
            break
    # dialog krisis → auto-lanjut sampai dialog branch muncul (bukan melewatinya)
    guard = 0
    while s.state.pending_dialog and guard < 20:
        v = s.view()
        did = v["dialog"]["dialog_id"] if v.get("dialog") else None
        if did == "dlg_a05_branch_family":
            break
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
        guard += 1
    v = s.view()
    assert v.get("dialog") and v["dialog"]["dialog_id"] == "dlg_a05_branch_family", v.get("dialog")
    s.apply_action({"type": "dialog_choice", "choice_index": idx})
    assert s.state.current_quest == "quest_a05_c04_004", f"branch {idx} harus konvergen"
    for flag, val in status_map.items():
        assert s.state.flags.get(flag) == val, f"{flag} = {s.state.flags.get(flag)}"
    assert s.state.relations.get(rel_npc, 0) >= rel_min


def test_arc5_entity_and_memory_to_ending(registry):
    """Q4 Entity first contact → Q5 memory besar → ending + arc_summary."""
    s = _through_arc1_2_3_4(registry)
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region")
    _reach(s, "loc_affected_village")
    _talk(s, "npc_villager_elder")
    _reach(s, "loc_outer_region"); _reach(s, "loc_mountain_gate")
    _talk(s, "npc_mountain_guard", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # changed
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    for npc in ("npc_lin_yue", "npc_shen_luo", "npc_mei_ruo", "npc_gu_han"):
        s.apply_action({"type": "talk", "npc": npc})
        if s.state.pending_dialog:
            break
    # dialog krisis → auto-lanjut sampai dialog branch muncul
    guard = 0
    while s.state.pending_dialog and guard < 20:
        v = s.view()
        did = v["dialog"]["dialog_id"] if v.get("dialog") else None
        if did == "dlg_a05_branch_family":
            break
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
        guard += 1
    v = s.view()
    assert v.get("dialog") and v["dialog"]["dialog_id"] == "dlg_a05_branch_family", v.get("dialog")
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # protect
    # Q4: entity di ruang terdalam
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    _talk(s, "npc_entity")
    assert s.state.current_quest == "quest_a05_c05_005"
    assert s.state.flags.get("flag_entity_first_contact") is True
    # Q5: memory besar (reach ulang ruang terdalam)
    _reach(s, "loc_forbidden_archive")
    _reach(s, "loc_tianxu_deepest_chamber")
    assert s.state.current_quest == "quest_a06_c01_001"  # DAG lanjut ke Arc VI
    assert s.state.flags.get("flag_memory_kill_attempt_seen") is True
    assert s.state.flags.get("flag_cycle_formation_known_partial") is True
    assert s.state.flags.get("belief_protagonist_may_be_cause") is False
    assert "memory_a05_m01" in [m["id"] for m in s.state.memories]
    v = s.view()
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "The World That Remembers"
    assert v["arc_summary"]["ending"]["id"] == "end_a05_world_remembers"


def test_arc5_memory_reliability(registry):
    """memory_a05_m01 reliability TINGGI dari data (docs 06 — puncak kejelasan)."""
    mem = registry.memory_by_id["memory_a05_m01"]
    assert mem["reliability"] == "TINGGI"
