"""Playthrough data story Arc II yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc II benar-benar dapat dimainkan engine
end-to-end: 9 quest (midterm→team trial→investigasi→accusation 3-branch→
konvergensi gua→artefak→return), sparring ujian, memory_a02_m01, branch
Obey/Investigate/Confront + efek state, arc_summary + ending. Skip bila data
Arc I tidak ada (data tidak di-commit — AGENTS.md).
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc02.json").exists(),
    reason="data story Arc II belum ada di data/",
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


def _through_arc1(registry) -> GameSession:
    """Mainkan Arc I penuh sampai quest_a02_c01_001."""
    s = _new_session(registry)
    _talk(s, "npc_aptitude_examiner")
    _talk(s, "npc_aptitude_examiner")
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue")
    s.apply_action({"type": "choose", "option": "pavilion_jianxin"})
    _reach(s, "loc_outer_region")
    _reach(s, "loc_training_hall")
    _reach(s, "loc_protagonist_room")
    assert s.state.current_quest == "quest_a02_c01_001", s.state.current_quest
    return s


def test_arc2_data_contract_ok(registry):
    """Kontrak validator: quest Arc II lengkap + arc_02 di config + memory baru."""
    ids = [q["id"] for q in registry.quests]
    assert ids == [
        "quest_a01_c01_001", "quest_a01_c01_002", "quest_a01_c02_003",
        "quest_a01_c03_004", "quest_a01_c04_005", "quest_a01_c04_006",
        "quest_a02_c01_001", "quest_a02_c01_002", "quest_a02_c02_003",
        "quest_a02_c02_004", "quest_a02_c02_005", "quest_a02_c03_006",
        "quest_a02_c04_007", "quest_a02_c04_008", "quest_a02_c04_009",
        "quest_a02_c04_007a", "quest_a02_c04_007b", "quest_a02_c04_007c",
        "quest_a03_c01_001", "quest_a03_c02_002", "quest_a03_c03_003",
        "quest_a03_c04_004", "quest_a03_c05_005",
        "quest_a04_c01_001", "quest_a04_c02_002", "quest_a04_c03_003",
        "quest_a04_c04_004",
        "quest_a05_c01_001", "quest_a05_c02_002", "quest_a05_c03_003",
        "quest_a05_c04_004", "quest_a05_c05_005",
        "quest_a06_c01_001", "quest_a06_c02_002", "quest_a06_c03_003",
        "quest_a06_c04_004",
        "quest_a07_c01_001", "quest_a07_c02_002", "quest_a07_c03_003",
        # Tian Xu Orthodox Faction (Phase 6)
        "quest_faction_orthodox_001", "quest_faction_orthodox_002",
        # Reformation Faction (GAP-B2)
        "quest_faction_reform_001", "quest_faction_reform_002",
        # Gu Han Character Arc (Phase 5)
        "quest_char_gu_han_001", "quest_char_gu_han_002",
        # Lin Yue Character Arc (Phase 1)
        "quest_char_lin_yue_001", "quest_char_lin_yue_002",
        # Mei Ruo Character Arc (Phase 4)
        "quest_char_mei_ruo_001", "quest_char_mei_ruo_002", "quest_char_mei_ruo_003",
        # Memory Investigation (GAP-B1)
        "quest_memory_a01_m01_investigate", "quest_memory_a01_m04_investigate",
        # Shen Luo Character Arc (Phase 3)
        "quest_char_shen_luo_001", "quest_char_shen_luo_002",
    ]
    assert "memory_a02_m01" in registry.memory_by_id
    assert registry.config["arcs"][1]["id"] == "arc_02"
    assert registry.config["arcs"][1]["final_quest"] == "quest_a02_c04_009"
    assert "npc_proctor" in registry.npc_by_id
    assert "catatan_siklus" in registry.key_items
    assert "artefak_pertama" in registry.key_items


def test_arc2_trials_and_investigation(registry):
    """Midterm + team trial (spar) → outer region → disturbance → missing disciple."""
    s = _through_arc1(registry)
    _reach(s, "loc_training_hall")
    # 1. midterm
    _talk(s, "npc_proctor")
    _spar_win(s, "npc_proctor")
    assert s.state.current_quest == "quest_a02_c01_002"
    assert s.state.flags.get("state_reputation_academic") == 1
    # 2. team trial
    _talk(s, "npc_proctor")
    _spar_win(s, "npc_proctor")
    assert s.state.current_quest == "quest_a02_c02_003"
    assert s.state.flags.get("flag_team_recognized") is True
    # 3. outer region
    _reach(s, "loc_outer_region")
    assert s.state.current_quest == "quest_a02_c02_004"
    assert s.state.flags.get("flag_outer_region_unlocked") is True
    # 4. disturbance — docs 03: di wilayah luar (loc_outer_region)
    _reach(s, "loc_hidden_cave")  # q004 butuh outer — belum selesai
    _reach(s, "loc_outer_region")  # q004 selesai
    assert s.state.current_quest == "quest_a02_c02_005"
    assert s.state.flags.get("flag_disturbance_investigated") is True
    # 5. missing disciple — tempat persembunyian di gua
    _reach(s, "loc_hidden_cave")
    assert s.state.current_quest == "quest_a02_c03_006"
    assert s.state.flags.get("flag_evidence_missing_disciple") is True
    assert s.state.inventory.get("catatan_siklus") == 1


def _to_accusation_branch(registry: DataRegistry) -> GameSession:
    """Mainkan Arc I → midterm → team trial → investigasi → sampai dialog
    percabangan dlg_a02_branch (DRY: dipakai accusation + convergence)."""
    s = _through_arc1(registry)
    _reach(s, "loc_training_hall")
    _talk(s, "npc_proctor"); _spar_win(s, "npc_proctor")
    _talk(s, "npc_proctor"); _spar_win(s, "npc_proctor")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue", close=False)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.branch_pending == "dlg_a02_branch"
    return s


@pytest.mark.parametrize("idx,flag,needle", [
    (0, "state_rel_proctor", "obey"),
    (1, "flag_archive_suspicious", "investigate"),
    (2, "state_rep_tianxu_orthodox", "confront"),
])
def test_arc2_accusation_three_branches(registry, idx, flag, needle):
    """First Major Choice: 3 cabang → efek state berbeda → branch-specific quests
    (GAP-A3: deeper branching) → konvergen ke quest_a02_c04_007."""
    s = _to_accusation_branch(registry)
    assert s.view()["mode"] == "dialog"
    s.apply_action({"type": "dialog_choice", "choice_index": idx})
    # Branch-specific quest (not directly 007 anymore)
    branch_quests = {0: "quest_a02_c04_007a", 1: "quest_a02_c04_007b", 2: "quest_a02_c04_007c"}
    assert s.state.current_quest == branch_quests[idx], f"branch {needle} harus masuk quest branch-specific"
    # efek branch sesuai docs 03 (obey→rel master+, investigate→archive_suspicious, confront→rep tianxu-)
    if needle == "obey":
        assert s.state.relations.get("npc_proctor", 0) >= 5
        assert s.state.factions.get("faction_tianxu_orthodox", 0) >= 3
        assert s.state.flags.get("flag_branch_obey") is True
    elif needle == "investigate":
        assert s.state.flags.get("flag_archive_suspicious") is True
        assert s.state.relations.get("npc_mei_ruo", 0) >= 3
    else:  # confront
        assert s.state.flags.get("flag_branch_confront") is True
        assert s.state.factions.get("faction_tianxu_orthodox", 0) <= -3
        assert s.state.relations.get("npc_gu_han", 0) >= 3


def test_arc2_convergence_to_ending(registry):
    """Konvergensi: branch quest → hidden cave → artefak (memory_a02_m01) → return → arc_summary."""
    s = _to_accusation_branch(registry)
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # obey
    # 6b. obey branch quest: talk to proctor
    _talk(s, "npc_proctor")
    assert s.state.current_quest == "quest_a02_c04_007", f"after obey branch, should converge"
    # 7. hidden cave
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    assert s.state.current_quest == "quest_a02_c04_008"
    assert s.state.flags.get("flag_hidden_cave_explored") is True
    # 8. artifact
    _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
    assert s.state.current_quest == "quest_a02_c04_009"
    assert s.state.flags.get("flag_memory_lin_yue_elder_seen") is True
    assert s.state.inventory.get("artefak_pertama") == 1
    assert "memory_a02_m01" in [m["id"] for m in s.state.memories]
    # 9. return
    _reach(s, "loc_outer_region"); _reach(s, "loc_training_hall")
    # quest utama Arc II selesai — DAG lanjut ke Arc III (quest_a03_c01_001)
    assert s.state.current_quest == "quest_a03_c01_001"
    assert s.state.flags.get("flag_arc2_complete") is True
    v = s.view()
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "The First Trial"
    assert v["arc_summary"]["ending"]["id"] == "end_a02_first_artifact"
    # pilihan akhir arc ditampilkan dari branch yang dipilih (docs 13/arc config)
    assert v["arc_summary"]["branch"] == "Obey"


def test_arc2_memory_reliability(registry):
    """memory_a02_m01 reliability SEDANG dari data (docs 06)."""
    mem = registry.memory_by_id["memory_a02_m01"]
    assert mem["reliability"] == "SEDANG"


def test_arc2_artifact_key_item_usable(registry):
    """artefak_pertama dapat dipakai — use_effects jalan."""
    s = _new_session(registry)
    s.state.inventory["artefak_pertama"] = 1
    s.apply_action({"type": "use_key_item", "item": "artefak_pertama"})
    assert s.state.flags.get("artefak_pertama_aktif") is True
