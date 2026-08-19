"""Playthrough data story Arc IV yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc IV benar-benar dapat dimainkan engine
end-to-end: 4 quest (Archive Beneath → What We Sealed → Grandmaster →
What Tian Xu Feeds On), dialog akses Arsip Terlarang yang bervariasi sesuai
branch Arc II (Obey/Investigate/Confront — state-conditional, docs 03b/08),
Version III verbatim, Grandmaster (first meaningful appearance), opsi
menyebarkan kebenaran (state_truth_spread_level — isi DESIGN GAP docs 03),
arc_summary + ending. Skip bila data Arc I-III tidak ada.
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc04.json").exists(),
    reason="data story Arc IV belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


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


def _new_session(registry: DataRegistry) -> GameSession:
    return GameSession.new(registry)


def _through_arc1_2_3(registry, branch_idx: int = 1) -> GameSession:
    """Mainkan Arc I + II + III penuh sampai quest_a04_c01_001."""
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
    s.apply_action({"type": "dialog_choice", "choice_index": branch_idx})
    # Branch-specific quests (GAP-A3: deeper branching)
    if branch_idx == 0:  # obey → talk to proctor
        _reach(s, "loc_training_hall"); _talk(s, "npc_proctor")
    elif branch_idx == 1:  # investigate → reach archive
        _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    else:  # confront → talk to grandmaster
        _reach(s, "loc_training_hall"); _reach(s, "loc_grandmaster_chamber"); _talk(s, "npc_grandmaster")
    # Convergence: reach hidden cave (x2: quest 007 + 008) then training_hall (quest 009)
    _reach(s, "loc_training_hall"); _reach(s, "loc_outer_region"); _reach(s, "loc_hidden_cave")
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
    assert s.state.current_quest == "quest_a04_c01_001", s.state.current_quest
    return s


def test_arc4_data_contract_ok(registry):
    """Kontrak validator: quest Arc IV lengkap + arc_04 di config + NPC/lokasi baru."""
    ids = [q["id"] for q in registry.quests]
    for qid in ("quest_a04_c01_001", "quest_a04_c02_002", "quest_a04_c03_003",
                "quest_a04_c04_004"):
        assert qid in ids, qid
    assert ids.index("quest_a04_c01_001") < ids.index("quest_a04_c04_004")
    # quest Arc III terakhir kini menyambung ke Arc IV (DAG lintas arc)
    q305 = next(q for q in registry.quests if q["id"] == "quest_a03_c05_005")
    assert q305.get("next") == [{"quest": "quest_a04_c01_001"}]
    # NPC + lokasi baru
    assert "npc_grandmaster" in registry.npc_by_id
    for lid in ("loc_forbidden_archive", "loc_grandmaster_chamber", "loc_tianxu_deepest_chamber"):
        assert lid in registry.location_by_id, lid
    # config arc_04
    assert registry.config["arcs"][3]["id"] == "arc_04"
    assert registry.config["arcs"][3]["final_quest"] == "quest_a04_c04_004"
    # dialog akses 3-jalur terdaftar
    assert registry.dialog("dlg_a04_d01") is not None
    assert registry.dialog("dlg_a04_d03") is not None


@pytest.mark.parametrize("branch_idx,expected_node,needle", [
    (0, "n_obey", "izin khusus"),          # Obey → rep tianxu +3 → dibantu guru
    (1, "n_investigate", "akses mandiri"),  # Investigate → flag_archive_suspicious
    (2, "n_confront", "simpatisan"),        # Confront → rep tianxu -3 → jalur alternatif
])
def test_arc4_access_dialog_three_paths(registry, branch_idx, expected_node, needle):
    """Dialog akses Arsip Terlarang bervariasi sesuai branch Arc II (docs 03b:
    state-conditional content availability, bukan pilihan baru)."""
    s = _through_arc1_2_3(registry, branch_idx)
    _reach(s, "loc_pavilion_yanzhi")
    s.apply_action({"type": "talk", "npc": "npc_mei_ruo"})
    assert s.state.pending_dialog
    v = s.view()
    assert v["dialog"]["node_id"] == expected_node, v["dialog"]["node_id"]
    assert needle in v["dialog"]["text"]
    # tutup dialog → quest 001 selesai → flag V1/V2 dibandingkan
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.current_quest == "quest_a04_c02_002"
    assert s.state.flags.get("flag_history_v1_v2_compared") is True


def test_arc4_archive_and_version_iii(registry):
    """Q1 talk Mei Ruo (akses) → Q2 talk Mei Ruo (Version III) → flag."""
    s = _through_arc1_2_3(registry)
    _reach(s, "loc_pavilion_yanzhi")
    _talk(s, "npc_mei_ruo")
    assert s.state.current_quest == "quest_a04_c02_002"
    # Q2: Version III dibaca bersama Mei Ruo (dialog dlg_a04_d02)
    _talk(s, "npc_mei_ruo")
    assert s.state.current_quest == "quest_a04_c03_003"
    assert s.state.flags.get("flag_version_iii_read") is True
    assert s.state.flags.get("flag_origin_cultivation_known_partial") is True
    # rel mei_ruo naik dari kolaborasi investigatif (docs: state_rel_mei_ruo +=)
    assert s.state.relations.get("npc_mei_ruo", 0) >= 3


def test_arc4_grandmaster_and_ending(registry):
    """Q3 Grandmaster → Q4 ruang terdalam → arc_summary + ending end_a04_false_history."""
    s = _through_arc1_2_3(registry)
    _reach(s, "loc_pavilion_yanzhi")
    _talk(s, "npc_mei_ruo")
    _talk(s, "npc_mei_ruo")  # Q2: Version III
    # Q3: Grandmaster
    _reach(s, "loc_training_hall")
    _reach(s, "loc_grandmaster_chamber")
    _talk(s, "npc_grandmaster")
    assert s.state.current_quest == "quest_a04_c04_004"
    assert s.state.flags.get("flag_grandmaster_met") is True
    assert s.state.flags.get("flag_stakes_of_stopping_source_known") is True
    assert s.state.relations.get("npc_grandmaster", 0) >= 3
    # Q4: ruang terdalam (lewat arsip terlarang)
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    assert s.state.current_quest == "quest_a05_c01_001"  # DAG lanjut ke Arc V
    assert s.state.flags.get("flag_tianxu_feeds_segel_known") is True
    assert s.state.flags.get("flag_arc4_complete") is True


def test_arc4_version_iii_quote_verbatim(registry):
    """Kutipan Version III verbatim dari docs 03b/02 (harus dijaga persis)."""
    d = registry.dialog("dlg_a04_d02")
    texts = " ".join(n.get("text", "") for n in d["nodes"].values())
    assert "Yang kami segel bukan musuh" in texts
    assert "akibat dari kesalahan kami sendiri" in texts


def test_arc4_spread_truth_ongoing_state(registry):
    """Opsi 'menyebarkan kebenaran' → state_truth_spread_level (isi DESIGN GAP
    docs 03: ongoing state, bukan satu quest terpusat)."""
    s = _through_arc1_2_3(registry)
    _reach(s, "loc_pavilion_yanzhi")
    _talk(s, "npc_mei_ruo")  # Q1: akses
    # Q2: buka dialog Version III — jalan eksplisit: n1 → n_v3 → pilih opsi spread
    s.apply_action({"type": "talk", "npc": "npc_mei_ruo"})
    assert s.state.pending_dialog
    v = s.view()
    assert v["dialog"]["dialog_id"] == "dlg_a04_d02"
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # (Baca catatan pendiri)
    v = s.view()
    assert v["dialog"]["node_id"] == "n_v3", v["dialog"]["node_id"]
    spread = [c for c in v["dialog"]["choices"]
              if "membagikan" in c["label"] or "sebagian kebenaran" in c["label"]]
    assert spread, "opsi menyebarkan kebenaran tidak ditemukan di n_v3"
    s.apply_action({"type": "dialog_choice", "choice_index": spread[0]["index"]})
    assert s.state.flags.get("state_truth_spread_level") == 1
    # reputasi orthodox turun karena kebenaran beredar (docs: Orthodox negatif)
    assert s.state.factions.get("faction_tianxu_orthodox", 0) <= -2


def test_arc4_grandmaster_relationship_initial(registry):
    """state_rel_grandmaster pertama kali diperkenalkan di Arc IV (docs 03b:
    state baru, first introduced di sini, bukan hostile default)."""
    d = registry.dialog("dlg_a04_d03")
    texts = " ".join(n.get("text", "") for n in d["nodes"].values())
    # baris plant payoff Arc VI (docs 03b: setup, bukan payoff itu sendiri)
    assert "Aku juga pernah menginginkannya" in texts
