"""Playthrough data story Arc III yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc III benar-benar dapat dimainkan engine
end-to-end: 5 quest (ruang mural → Mo Chen → Deceased → stance 3-branch →
memory gerbang), Mo Chen mengenali simbol_kuno + menghilang (npc_state),
memory_a03_m01 (reliability SANGAT RENDAH — puncak misleading, docs 06),
state_identity_stance per branch, arc_summary + ending. Skip bila data Arc
I/II tidak ada (data tidak di-commit — AGENTS.md).
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc03.json").exists(),
    reason="data story Arc III belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


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


def _through_arc1_2(registry) -> GameSession:
    """Mainkan Arc I + Arc II penuh sampai quest_a03_c01_001 (jalur investigate)."""
    s = _new_session(registry)
    _talk(s, "npc_aptitude_examiner")
    _talk(s, "npc_aptitude_examiner")
    _reach(s, "loc_training_hall")
    # Complete lesson chain: proctor → lin_yue → shen_luo → gu_han → proctor
    _talk(s, "npc_proctor")
    _talk(s, "npc_lin_yue")
    _talk(s, "npc_shen_luo")
    _talk(s, "npc_gu_han")
    _talk(s, "npc_proctor")
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
    s.apply_action({"type": "dialog_choice", "choice_index": 1})  # investigate
    # Branch quest: investigate → reach archive (GAP-A3: deeper branching)
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    # Convergence: reach hidden cave (x2: quest 007 + 008) then training_hall (quest 009)
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    assert s.state.current_quest == "quest_a03_c01_001", s.state.current_quest
    return s


def test_arc3_data_contract_ok(registry):
    """Kontrak validator: quest Arc III lengkap + arc_03 di config + memory baru + NPC baru."""
    ids = [q["id"] for q in registry.quests]
    assert "quest_a03_c01_001" in ids
    assert "quest_a03_c02_002" in ids
    assert "quest_a03_c03_003" in ids
    assert "quest_a03_c04_004" in ids
    assert "quest_a03_c05_005" in ids
    assert ids.index("quest_a03_c01_001") < ids.index("quest_a03_c05_005")
    # quest Arc II terakhir kini menyambung ke Arc III (DAG lintas arc)
    q209 = next(q for q in registry.quests if q["id"] == "quest_a02_c04_009")
    assert q209.get("next") == [{"quest": "quest_a03_c01_001"}]
    # memory + NPC baru
    assert "memory_a03_m01" in registry.memory_by_id
    assert "npc_mo_chen" in registry.npc_by_id
    assert "npc_archive_clerk" in registry.npc_by_id
    # lokasi baru
    for lid in ("loc_hidden_room_mural", "loc_mo_chen_meeting", "loc_archive_public"):
        assert lid in registry.location_by_id, lid
    # config arc_03
    assert registry.config["arcs"][2]["id"] == "arc_03"
    assert registry.config["arcs"][2]["final_quest"] == "quest_a03_c05_005"
    assert registry.config["arcs"][2]["memories_total"] == 6


def test_arc3_mural_room_and_mo_chen(registry):
    """Q1 ruang mural (flag_mural_analyzed) → Q2 Mo Chen mengenali simbol_kuno + menghilang."""
    s = _through_arc1_2(registry)
    # Q1: reach ruang mural — terhubung dari pavilion Yanzhi
    _reach(s, "loc_pavilion_yanzhi")
    _reach(s, "loc_hidden_room_mural")
    assert s.state.current_quest == "quest_a03_c02_002"
    assert s.state.flags.get("flag_mural_analyzed") is True
    # Q2: talk Mo Chen (simbol_kuno dimiliki sejak Arc I → node n3 dikenali)
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mo_chen_meeting")
    _talk(s, "npc_mo_chen")
    assert s.state.current_quest == "quest_a03_c03_003"
    assert s.state.flags.get("flag_name_jiang_yan_known") is True
    assert s.state.flags.get("flag_mo_chen_met") is True
    # Mo Chen menghilang (npc_state available=false) — tak bisa diajak bicara lagi
    npc = registry.npc("npc_mo_chen")
    assert s._is_npc_available(npc) is False


def _to_stance_branch(registry: DataRegistry) -> GameSession:
    """Mainkan Arc I-II → mural → Mo Chen → archive clerk → dialog branch
    Lin Yue (DRY: dipakai deceased, stance branches, gate memory)."""
    s = _through_arc1_2(registry)
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_hidden_room_mural")
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_training_hall")
    _reach(s, "loc_mo_chen_meeting")
    _talk(s, "npc_mo_chen")
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _talk(s, "npc_archive_clerk")
    assert s.state.current_quest == "quest_a03_c04_004"
    assert s.state.flags.get("flag_jiang_yan_deceased_confirmed") is True
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.branch_pending == "dlg_a03_branch"
    return s


def test_arc3_deceased_and_stance_branch(registry):
    """Q3 Deceased (flag) → Q4 diskusi Lin Yue → branch 3-cabang state_identity_stance."""
    s = _to_stance_branch(registry)
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # deny
    assert s.state.current_quest == "quest_a03_c05_005"
    assert s.state.flags.get("state_identity_stance") == "deny"
    assert s.state.relations.get("npc_gu_han", 0) >= 2
    assert s.state.relations.get("npc_mei_ruo", 0) >= -1


@pytest.mark.parametrize("idx,stance,rel_npc,rel_min", [
    (0, "deny", "npc_gu_han", 2),
    (1, "accept_cautious", "npc_lin_yue", 1),
    (2, "seek_truth", "npc_mei_ruo", 4),
])
def test_arc3_stance_three_branches(registry, idx, stance, rel_npc, rel_min):
    """Tiga stance → state_identity_stance berbeda → semua konvergen ke quest_a03_c05_005
    (prinsip convergence docs 03). Seek Truth memberi relation Mei Ruo TERBESAR."""
    s = _to_stance_branch(registry)
    s.apply_action({"type": "dialog_choice", "choice_index": idx})
    assert s.state.current_quest == "quest_a03_c05_005", f"stance {stance} harus konvergen"
    assert s.state.flags.get("state_identity_stance") == stance
    assert s.state.relations.get(rel_npc, 0) >= rel_min
    if stance == "seek_truth":
        s2 = _to_stance_branch(registry)
        s2.apply_action({"type": "dialog_choice", "choice_index": 0})  # deny
        assert s.state.relations.get("npc_mei_ruo", 0) > s2.state.relations.get("npc_mei_ruo", 0)


def test_arc3_gate_memory_and_ending(registry):
    """Q5 memory gerbang (memory_a03_m01) → arc_summary + ending end_a03_gate_opened."""
    s = _to_stance_branch(registry)
    s.apply_action({"type": "dialog_choice", "choice_index": 2})  # seek_truth
    # Q5: kembali ke ruang mural → memory gerbang
    _reach(s, "loc_pavilion_yanzhi"); _reach(s, "loc_hidden_room_mural")
    # quest utama Arc III selesai — DAG lanjut ke Arc IV (quest_a04_c01_001)
    assert s.state.current_quest == "quest_a04_c01_001"
    assert s.state.flags.get("flag_memory_gate_a03_seen") is True
    assert s.state.flags.get("belief_protagonist_may_be_cause") is True
    assert "memory_a03_m01" in [m["id"] for m in s.state.memories]
    v = s.view()
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "Echoes of Another Self"
    assert v["arc_summary"]["ending"]["id"] == "end_a03_gate_opened"
    # enum flag → branch humanized (docs 13: state_identity_stance)
    assert v["arc_summary"]["branch"] == "Seek Truth"


def test_arc3_memory_reliability(registry):
    """memory_a03_m01 reliability SANGAT RENDAH (docs 06: puncak misleading)."""
    mem = registry.memory_by_id["memory_a03_m01"]
    assert mem["reliability"] == "SANGAT RENDAH"
    assert "Kalau dunia harus membenciku" in mem["text"]
