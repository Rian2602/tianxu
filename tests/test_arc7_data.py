"""Playthrough data story Arc VII (final act) yang NYATA (`data/`) — bukan fixture.

Memvalidasi bahwa data produksi Arc VII benar-benar dapat dimainkan engine
end-to-end: 3 quest (The Last Night → I Am Not You → Second Life FINAL DECISION),
Final Confrontation dengan Jiang Yan imprint ("Aku bukan kau" verbatim),
Entity's Truth, dan 5 ending (Preserve/Destroy/Transform/Sacrifice + Hidden
Resolution Second Life) dengan ACCESS & forbidden condition (docs 11 Ending
Matrix). Engine `flags` (multi-flag AND) + `flag_not` (negasi) diuji di sini —
Hidden Resolution memerlukan KOMBINASI kondisi independen, bukan satu flag.

Skip bila data Arc I-VI tidak ada.
"""

from __future__ import annotations

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession
from tests.test_arc6_data import _play_arc5, _to_arc6_q4
from tests.test_arc5_data import _to_family_crisis_branch, _talk, _reach

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc07.json").exists(),
    reason="data story Arc VII belum ada di data/",
)


@pytest.fixture(scope="module")
def registry() -> DataRegistry:
    return DataRegistry()


def _play_arc6(s: GameSession, principle_idx: int = 0) -> None:
    """Mainkan Arc VI Q4 (Final Choice) → quest Arc VII Q1 aktif."""
    _to_arc6_q4(s)
    s.apply_action({"type": "talk", "npc": "npc_mentor"})
    for _ in range(10):
        v = s.view()
        d = v.get("dialog") or {}
        if len(d.get("choices") or []) == 4:
            s.apply_action({"type": "dialog_choice", "choice_index": principle_idx})
            break
        s.apply_action({"type": "dialog_choice", "choice_index": 0})
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.current_quest == "quest_a07_c01_001", s.state.current_quest


def _play_arc5_family(registry: DataRegistry, family_idx: int = 0, branch_idx: int = 1, stance_idx: int = 2) -> GameSession:
    """Arc V penuh — MG changed + Family Crisis family_idx (0=protect, 1=destroy,
    2=truth, 3=despair). DRY: uses _to_family_crisis_branch."""
    s = _to_family_crisis_branch(registry, branch_idx=branch_idx, stance_idx=stance_idx)
    s.apply_action({"type": "dialog_choice", "choice_index": family_idx})  # Q3
    _reach(s, "loc_training_hall"); _reach(s, "loc_archive_public")
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")
    _talk(s, "npc_entity")                                # Q4
    _reach(s, "loc_forbidden_archive"); _reach(s, "loc_tianxu_deepest_chamber")  # Q5
    assert s.state.current_quest == "quest_a06_c01_001", s.state.current_quest
    return s


def _play_arc7(s: GameSession, decision_idx: int) -> None:
    """Mainkan Arc VII penuh; pilih final decision di quest 3."""
    # Q1 The Last Night: talk Lin Yue
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue")
    assert s.state.current_quest == "quest_a07_c02_002", s.state.current_quest
    assert s.state.flags.get("flag_last_night_complete") is True
    # Q2 I Am Not You: turun ke loc_below_deepest + konfrontasi imprint
    _reach(s, "loc_archive_public"); _reach(s, "loc_forbidden_archive")
    _reach(s, "loc_tianxu_deepest_chamber"); _reach(s, "loc_below_deepest")
    _talk(s, "npc_jiang_yan_imprint")
    assert s.state.current_quest == "quest_a07_c03_003", s.state.current_quest
    assert s.state.flags.get("flag_i_am_not_you_said") is True
    assert s.state.flags.get("flag_entity_truth_known") is True
    # Q3 Second Life FINAL DECISION
    s.apply_action({"type": "talk", "npc": "npc_jiang_yan_imprint"})
    v = s.view()
    choices = (v.get("dialog") or {}).get("choices") or []
    assert decision_idx < len(choices), \
        f"pilihan {decision_idx} tak tersedia (hanya {len(choices)}: {[c['label'][:20] for c in choices]})"
    s.apply_action({"type": "dialog_choice", "choice_index": decision_idx})
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.current_quest is None


@pytest.mark.parametrize("family_idx,persist_flag,persist_val", [
    (0, "state_lin_yue_status", "loyal"),          # protect
    (1, "state_shen_luo_status", "loyal"),         # destroy
    (2, "state_mei_ruo_status", "loyal"),          # truth
    (3, "state_gu_han_status", "disillusioned"),   # despair
])
def test_arc5_family_status_persists_to_arc7_ending(registry, family_idx, persist_flag, persist_val):
    """docs 04: status Family Crisis = branching PERMANEN yang dibawa ke Arc
    VI-VII — status anggota tidak hilang saat convergence Arc V→VI→VII, dan
    ending tetap tercapai dari 4 jalur (protect/destroy/truth/despair)."""
    s = _play_arc5_family(registry, family_idx=family_idx)
    _play_arc6(s, principle_idx=0)   # preserve
    _play_arc7(s, decision_idx=0)    # preserve
    # status dari keputusan Family Crisis MASIH ada di akhir game
    assert s.state.flags.get(persist_flag) == persist_val, f"{persist_flag} hilang saat convergence"
    # ending tercapai dengan benar
    v = s.view()
    assert s.state.flags.get("state_ending_achieved") == "preserve"
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["ending"]["id"] == "ending_unbroken_heaven"


def test_arc7_data_contract_ok(registry):
    """Kontrak validator: quest Arc VII lengkap + arc_07 di config + NPC/lokasi baru."""
    ids = [q["id"] for q in registry.quests]
    for qid in ("quest_a07_c01_001", "quest_a07_c02_002", "quest_a07_c03_003"):
        assert qid in ids, qid
    assert ids.index("quest_a07_c01_001") < ids.index("quest_a07_c03_003")
    # quest Arc VI terakhir menyambung ke Arc VII
    q604 = next(q for q in registry.quests if q["id"] == "quest_a06_c04_004")
    assert q604.get("next") == [{"quest": "quest_a07_c01_001"}]
    # NPC + lokasi baru
    assert "npc_jiang_yan_imprint" in registry.npc_by_id
    for lid in ("loc_tianxu_main_hall", "loc_below_deepest"):
        assert lid in registry.location_by_id, lid
    # config arc_07 + 5 ending
    arc7 = registry.config["arcs"][6]
    assert arc7["id"] == "arc_07"
    assert arc7["final_quest"] == "quest_a07_c03_003"
    ends = {e["id"] for e in arc7["endings"]}
    assert ends == {"ending_unbroken_heaven", "ending_mortal_dawn", "ending_new_heaven",
                    "ending_nameless_guardian", "ending_second_life"}, ends
    # dialog terdaftar
    assert registry.dialog("dlg_a07_d01") is not None
    assert registry.dialog("dlg_a07_d02") is not None
    assert registry.dialog("dlg_a07_d03") is not None


def test_arc7_last_night_opens_final_confrontation(registry):
    """Q1 The Last Night (talk Lin Yue, crisis) → Q2 I Am Not You (imprint)."""
    s = _play_arc5(registry)
    _play_arc6(s, principle_idx=0)
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue")
    assert s.state.current_quest == "quest_a07_c02_002"
    # konfrontasi di bawah ruang terdalam
    _reach(s, "loc_archive_public"); _reach(s, "loc_forbidden_archive")
    _reach(s, "loc_tianxu_deepest_chamber"); _reach(s, "loc_below_deepest")
    _talk(s, "npc_jiang_yan_imprint")
    assert s.state.current_quest == "quest_a07_c03_003"
    assert s.state.flags.get("flag_i_am_not_you_said") is True
    assert s.state.flags.get("flag_entity_truth_known") is True


def test_arc7_im_not_you_verbatim_and_entity_truth(registry):
    """Dialog dlg_a07_d02: 'Aku membuatmu...' → 'Tidak. Aku bukan kau.' + Entity's Truth."""
    dlg = registry.dialog("dlg_a07_d02")
    alltext = " ".join(n.get("text", "") for n in dlg["nodes"].values())
    labels = " ".join(ch.get("label", "") for n in dlg["nodes"].values()
                       for ch in n.get("choices", []))
    assert "Aku membuatmu untuk menyelesaikan apa yang gagal kuselesaikan" in alltext
    assert "Tidak. Aku bukan kau." in labels  # penolakan identitas (MSB §32)
    assert "Kau membunuhku sekali" in alltext  # Entity's Truth (MSB §34)


@pytest.mark.parametrize("idx,principle,ending", [
    (0, "preserve", "ending_unbroken_heaven"),
    (1, "destroy", "ending_mortal_dawn"),
    (2, "transform", "ending_new_heaven"),
    (3, "sacrifice", "ending_nameless_guardian"),
])
def test_arc7_four_main_endings(registry, idx, principle, ending):
    """FINAL DECISION: 4 prinsip → state_ending_achieved berbeda → 4 ending utama."""
    s = _play_arc5(registry)
    _play_arc6(s, principle_idx=idx)
    _play_arc7(s, decision_idx=idx)
    assert s.state.flags.get("state_ending_achieved") == principle
    v = s.view()
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "Second Life"
    assert v["arc_summary"]["ending"]["id"] == ending


def test_arc7_hidden_resolution_unlocked(registry):
    """Hidden Resolution: 9 kondisi independen terpenuhi → opsi Second Life muncul.

    Jalur: stance seek_truth (Arc III) + family protect/lin_yue loyal (Arc V)
    + prinsip preserve (Arc VI) — kombinasi kondisi docs 11 MSB §36.
    """
    s = _play_arc5(registry)
    _play_arc6(s, principle_idx=0)                   # preserve
    # Hidden Resolution menuntut: flag_the_gate_full_truth_known, flag_tianxu_
    # feeds_segel_known, flag_version_iii_read, flag_jiang_yan_origin_known,
    # flag_betrayal_identity_known, flag_cycle_formation_known_partial,
    # belief_protagonist_may_be_cause==false, state_lin_yue_status != disillusioned,
    # state_identity_stance != deny, state_final_principle != sacrifice
    assert s.state.flags.get("flag_the_gate_full_truth_known") is True
    assert s.state.flags.get("flag_tianxu_feeds_segel_known") is True
    assert s.state.flags.get("flag_version_iii_read") is True
    assert s.state.flags.get("belief_protagonist_may_be_cause") is False
    assert s.state.flags.get("state_identity_stance") == "seek_truth"
    assert s.state.flags.get("state_final_principle") == "preserve"
    _play_arc7(s, decision_idx=4)  # opsi hidden (indeks 4 dari 5)
    assert s.state.flags.get("state_ending_achieved") == "second_life"
    v = s.view()
    assert v["arc_summary"]["ending"]["id"] == "ending_second_life"


def test_arc7_hidden_resolution_blocked_by_forbidden(registry):
    """Forbidden condition (docs 11): deny + sacrifice → opsi hidden TIDAK muncul.

    Hanya 4 pilihan di quest 3 — memilih sacrifice → ending_nameless_guardian.
    Uses stance_idx=0 to truly set Arc III stance to 'deny'.
    """
    s = _play_arc5(registry, stance_idx=0)           # deny (Arc III)
    # verify precondition: Arc III stance is deny
    assert s.state.flags.get("state_identity_stance") == "deny", \
        f"precondition failed: stance={s.state.flags.get('state_identity_stance')}"
    _play_arc6(s, principle_idx=3)                   # sacrifice
    # mainkan Q1 + Q2 sampai quest 3 aktif
    _reach(s, "loc_training_hall")
    _talk(s, "npc_lin_yue")
    _reach(s, "loc_archive_public"); _reach(s, "loc_forbidden_archive")
    _reach(s, "loc_tianxu_deepest_chamber"); _reach(s, "loc_below_deepest")
    _talk(s, "npc_jiang_yan_imprint")
    assert s.state.current_quest == "quest_a07_c03_003"
    # quest 3: buka dialog final decision
    s.apply_action({"type": "talk", "npc": "npc_jiang_yan_imprint"})
    v = s.view()
    choices = (v.get("dialog") or {}).get("choices") or []
    assert len(choices) == 4, [c["label"][:25] for c in choices]
    # pilih sacrifice → ending_nameless_guardian
    s.apply_action({"type": "dialog_choice", "choice_index": 3})
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.current_quest is None
    assert s.state.flags.get("state_ending_achieved") == "sacrifice"
    v = s.view()
    assert v["arc_summary"]["ending"]["id"] == "ending_nameless_guardian"


def test_arc7_hidden_resolution_engine_flags_and_flag_not(registry):
    """Engine: kondisi `flags` (list AND) + `flag_not` (negasi) — dukungan docs 11.

    Dipakai oleh opsi Second Life di dlg_a07_d03. Verifikasi langsung terhadap
    dialog data: opsi hidden punya condition dengan BANYAK flag (bukan satu).
    """
    dlg = registry.dialog("dlg_a07_d03")
    hidden = None
    for node in dlg["nodes"].values():
        for ch in node.get("choices", []):
            if ch.get("option") == "second_life":
                hidden = ch
    assert hidden is not None
    cond = hidden.get("condition") or {}
    flags = cond.get("flags") or []
    flag_not = cond.get("flag_not") or []
    # docs 11: "jangan membuat hidden ending hanya berdasarkan satu flag"
    assert len(flags) >= 7, flags
    assert len(flag_not) >= 3, flag_not
    keys = {f["key"] for f in flags} | {f["key"] for f in flag_not}
    assert "state_final_principle" in keys  # forbidden sacrifice
    assert "state_identity_stance" in keys  # forbidden deny
    assert "state_lin_yue_status" in keys   # forbidden disillusioned
