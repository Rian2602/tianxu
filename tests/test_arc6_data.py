"""Playthrough data story Arc VI yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc VI benar-benar dapat dimainkan engine
end-to-end: 4 quest (Someone Like Me → The Betrayal That Wasn't → The Gate →
What the Sword Remembers), revelasi pengkhianat = Mentor, memory_a06_m01
(ground truth TINGGI), Final Choice 4-prinsip (preserve/destroy/transform/
sacrifice → state_final_principle), arc_summary + ending. Skip bila data
Arc I-V tidak ada.
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession
from tests.test_arc5_data import _through_arc1_2_3_4, _to_family_crisis_branch, _talk, _reach

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc06.json").exists(),
    reason="data story Arc VI belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


def _play_arc5(registry: DataRegistry, branch_idx: int = 1, stance_idx: int = 2) -> GameSession:
    """Mainkan Arc V penuh sampai quest_a06_c01_001 (data Arc V nyata).

    DRY: bangun session dari _to_family_crisis_branch, lalu selesaikan
    Family Crisis + Entity + Memory → Arc VI.
    """
    s = _to_family_crisis_branch(registry, branch_idx=branch_idx, stance_idx=stance_idx)
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # protect
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    _talk(s, "npc_entity")                                # Q4
    _reach(s, "loc_forbidden_archive")
    _reach(s, "loc_tianxu_deepest_chamber")               # Q5 memory
    assert s.state.current_quest == "quest_a06_c01_001", s.state.current_quest
    return s


def _to_arc6_q4(s: GameSession) -> None:
    """Mainkan Arc VI Q1-Q3 sampai quest_a06_c04_004."""
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_jiang_yan_records")                    # Q1 reach catatan
    _reach(s, "loc_archive_public"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mentor_ground")
    _talk(s, "npc_mentor")                                # Q2 reveal pengkhianat
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_training_hall"); _reach(s, "loc_mentor_ground")


def test_arc6_data_contract_ok(registry):
    """Kontrak validator: quest Arc VI lengkap + arc_06 di config + NPC/lokasi/memory baru."""
    ids = [q["id"] for q in registry.quests]
    for qid in ("quest_a06_c01_001", "quest_a06_c02_002", "quest_a06_c03_003",
                "quest_a06_c04_004"):
        assert qid in ids, qid
    assert ids.index("quest_a06_c01_001") < ids.index("quest_a06_c04_004")
    # quest Arc V terakhir menyambung ke Arc VI
    q505 = next(q for q in registry.quests if q["id"] == "quest_a05_c05_005")
    assert q505.get("next") == [{"quest": "quest_a06_c01_001"}]
    # NPC + lokasi baru
    assert "npc_mentor" in registry.npc_by_id
    for lid in ("loc_mentor_ground", "loc_jiang_yan_records"):
        assert lid in registry.location_by_id, lid
    # config arc_06
    assert registry.config["arcs"][5]["id"] == "arc_06"
    assert registry.config["arcs"][5]["final_quest"] == "quest_a06_c04_004"
    # memory ground truth Arc VI
    assert "memory_a06_m01" in registry.memory_by_id
    # dialog terdaftar
    assert registry.dialog("dlg_a06_d01") is not None
    assert registry.dialog("dlg_a06_d03") is not None


def test_arc6_jiang_yan_origin_and_betrayal(registry):
    """Q1 Someone Like Me (reach catatan) → Q2 reveal pengkhianat = Mentor."""
    s = _play_arc5(registry)
    # Q1: catatan Jiang Yan
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_jiang_yan_records")
    assert s.state.current_quest == "quest_a06_c02_002"
    assert s.state.flags.get("flag_jiang_yan_origin_known") is True
    # Q2: Mentor reveal pengkhianatan
    _reach(s, "loc_archive_public"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mentor_ground")
    _talk(s, "npc_mentor")
    assert s.state.current_quest == "quest_a06_c03_003"
    assert s.state.flags.get("flag_betrayal_identity_known") is True
    assert s.state.relations.get("npc_mentor", 0) >= 3


def test_arc6_gate_memory_truth(registry):
    """Q3 The Gate → memory_a06_m01 (ground truth) + makna Second Life."""
    s = _play_arc5(registry)
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_archive_public")
    _reach(s, "loc_jiang_yan_records")
    _reach(s, "loc_archive_public"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mentor_ground")
    _talk(s, "npc_mentor")
    # Q3: ruang terdalam = The Gate
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    assert s.state.current_quest == "quest_a06_c04_004"
    assert s.state.flags.get("flag_the_gate_full_truth_known") is True
    assert s.state.flags.get("flag_second_life_meaning_known") is True
    assert "memory_a06_m01" in [m["id"] for m in s.state.memories]


@pytest.mark.parametrize("idx,principle", [
    (0, "preserve"),
    (1, "destroy"),
    (2, "transform"),
    (3, "sacrifice"),
])
def test_arc6_final_choice_four_principles(registry, idx, principle):
    """Final Choice: 4 prinsip → state_final_principle berbeda → Arc VI selesai."""
    s = _play_arc5(registry)
    _to_arc6_q4(s)
    # Q4: talk Mentor → revelation pedang → pilih prinsip
    s.apply_action({"type": "talk", "npc": "npc_mentor"})
    assert s.state.pending_dialog
    for _ in range(10):
        v = s.view()
        d = v.get("dialog") or {}
        if len(d.get("choices") or []) == 4:
            s.apply_action({"type": "dialog_choice", "choice_index": idx})
            break
        s.apply_action({"type": "dialog_choice", "choice_index": 0})
    guard = 0
    while s.state.pending_dialog and guard < 10:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
        guard += 1
    assert s.state.current_quest == "quest_a07_c01_001", s.state.current_quest
    assert s.state.flags.get("state_final_principle") == principle
    assert s.state.flags.get("flag_second_life_meaning_known") is True
    v = s.view()
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "The Last Cycle"
    assert v["arc_summary"]["ending"]["id"] == "end_a06_last_cycle"


def test_arc6_mentor_sword_quote_and_memory_reliability(registry):
    """Revelation pedang verbatim + memory_a06_m01 reliability TINGGI (docs 06)."""
    dlg = registry.dialog("dlg_a06_d03")
    alltext = " ".join(n.get("text", "") for n in dlg["nodes"].values())
    assert "Cara kau memegang pedang" in alltext
    mem = registry.memory_by_id["memory_a06_m01"]
    assert mem["reliability"] == "TINGGI"
    # memory Arc VI adalah ground truth final — kurva reliability memuncak di sini
    mems = [m["reliability"] for m in registry.memories]
    assert "SANGAT RENDAH" in mems  # memory_a03_m01 (puncak misleading) masih ada
