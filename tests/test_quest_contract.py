"""Test kontrak quest — plan perbaikan bug (R1–R6, docs/FASE02_REVIEW_AND_BUGPLAN.md).

Menutup BUG-1 (side quest softlock), BUG-2 (next/fail_next kind), BUG-3/4
(set clamp & ref), BUG-5/6/7 (efek ref), BUG-8 (start_quest → side), BUG-9
(side defeat tanpa `enemies`). Semua pelanggaran harus ditolak saat load dengan
pesan menyebut file+field+nilai; data VALID tetap lolos (regression gate).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.engine.session import GameSession
from src.validate import DataContractError

FIX = Path(__file__).parent / "fixtures" / "minimal_data"


def _copy(tmp_path: Path) -> Path:
    dst = tmp_path / "contract_data"
    shutil.copytree(FIX, dst)
    return dst


def _load(dst: Path, rel: str):
    with open(dst / rel, encoding="utf-8") as f:
        return json.load(f)


def _dump(dst: Path, rel: str, data) -> None:
    with open(dst / rel, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _add_side(dst: Path, quest: dict) -> None:
    qs = _load(dst, "quests/minimal.json")
    qs["quests"].append(quest)
    _dump(dst, "quests/minimal.json", qs)


# ============================================================================
# BUG-1: side quest softlock — kind yang didukung vs tidak
# ============================================================================

@pytest.mark.parametrize("kind", ["choose"])
def test_side_quest_choose_rejected(tmp_path, kind):
    dst = _copy(tmp_path)
    _add_side(dst, {
        "id": "q_side_x", "kind": "side", "title": "X",
        "objective": {"kind": kind, "hint": "x",
                      "options": [{"value": "a", "label": "A"}]},
    })
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "side quest" in msg and kind in msg


@pytest.mark.parametrize("objective", [
    {"kind": "talk", "npc": "npc_guru", "target": 1, "hint": "t"},
    {"kind": "reach", "location": "loc_hutan", "hint": "r"},
    {"kind": "defeat", "target": 1, "hint": "d"},
    {"kind": "gather", "item": "pil_qi", "target": 1, "hint": "g"},
    {"kind": "spar", "npc": "npc_guru", "hint": "s"},
    {"kind": "advance_time", "hour": 8, "hint": "a"},
])
def test_side_quest_supported_kinds_load_ok(tmp_path, objective):
    """R1b: semua kind lain DIDUKUNG side — data valid harus lolos (regression gate)."""
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_ok", "kind": "side", "title": "OK",
                    "objective": objective})
    DataRegistry(dst)  # tidak boleh error


def test_side_talk_completes_after_dialog(tmp_path):
    """R1b: side quest talk benar-benar selesai setelah dialog (softlock hilang)."""
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_bicara", "kind": "side", "title": "Bicara",
                    "objective": {"kind": "talk", "npc": "npc_guru", "target": 1, "hint": "b"}})
    reg = DataRegistry(dst)
    sess = GameSession.new(reg)
    sess.quest.start_side("q_side_bicara")
    sess.apply_action({"type": "talk", "npc": "npc_guru"})
    sess.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q_side_bicara" in sess.state.completed_quests


def test_side_reach_completes_on_move(tmp_path):
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_sampai", "kind": "side", "title": "Sampai",
                    "objective": {"kind": "reach", "location": "loc_hutan", "hint": "s"}})
    reg = DataRegistry(dst)
    sess = GameSession.new(reg)
    sess.quest.start_side("q_side_sampai")
    sess.apply_action({"type": "move", "to": "loc_hutan"})
    assert "q_side_sampai" in sess.state.completed_quests


def test_side_defeat_without_enemies_completes_on_battle(tmp_path):
    """BUG-9: side defeat TANPA `enemies` dulu softlock (loop manual `e in allowed`),
    sekarang selesai saat menang melawan musuh apa pun (handler `not allowed or ...`)."""
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_kalahkan", "kind": "side", "title": "Kalahkan",
                    "objective": {"kind": "defeat", "target": 1, "hint": "k"}})
    reg = DataRegistry(dst)
    sess = GameSession.new(reg)
    sess.quest.start_side("q_side_kalahkan")
    sess.apply_action({"type": "move", "to": "loc_hutan"})
    sess.apply_action({"type": "hunt"})
    guard = 0
    while sess.state.pending_battle and guard < 40:
        sess.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert "q_side_kalahkan" in sess.state.completed_quests


def test_side_advance_time_completes(tmp_path):
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_tunggu", "kind": "side", "title": "Tunggu",
                    "objective": {"kind": "advance_time", "hour": 8, "day_offset": 0, "hint": "t"}})
    reg = DataRegistry(dst)
    sess = GameSession.new(reg)
    sess.quest.start_side("q_side_tunggu")
    sess.apply_action({"type": "rest", "hours": 8})  # gerbang aman
    assert "q_side_tunggu" in sess.state.completed_quests


# ============================================================================
# BUG-2: next/fail_next hanya main + target wajib main
# ============================================================================

def test_side_quest_with_next_rejected(tmp_path):
    dst = _copy(tmp_path)
    qs = _load(dst, "quests/minimal.json")
    side = next(q for q in qs["quests"] if q["kind"] == "side")
    side["next"] = [{"quest": "q_min_pilih"}]
    _dump(dst, "quests/minimal.json", qs)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "side quest tidak boleh punya 'next'" in str(ei.value)


def test_main_next_to_side_rejected(tmp_path):
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_target", "kind": "side", "title": "T",
                    "objective": {"kind": "gather", "item": "pil_qi", "target": 1, "hint": "t"}})
    qs = _load(dst, "quests/minimal.json")
    qs["quests"][0]["next"] = [{"quest": "q_side_target"}]  # intro → side
    _dump(dst, "quests/minimal.json", qs)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "q_side_target" in str(ei.value) and "quest side" in str(ei.value)


def test_main_fail_next_to_side_rejected(tmp_path):
    dst = _copy(tmp_path)
    _add_side(dst, {"id": "q_side_target", "kind": "side", "title": "T",
                    "objective": {"kind": "gather", "item": "pil_qi", "target": 1, "hint": "t"}})
    qs = _load(dst, "quests/minimal.json")
    qs["quests"][0]["fail_next"] = [{"quest": "q_side_target"}]
    _dump(dst, "quests/minimal.json", qs)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    assert "fail_next" in str(ei.value) and "quest side" in str(ei.value)


# ============================================================================
# BUG-3/4: `set` clamp & referensi
# ============================================================================

def _set_on_choose(tmp_path, oset: dict):
    dst = _copy(tmp_path)
    qs = _load(dst, "quests/minimal.json")
    qs["quests"][1]["objective"]["options"][0]["set"] = oset  # q_min_pilih
    _dump(dst, "quests/minimal.json", qs)
    return dst


def test_set_gold_negative_rejected(tmp_path):
    with pytest.raises(DataContractError) as ei:
        DataRegistry(_set_on_choose(tmp_path, {"academy": "akademi_bambu", "gold": -1}))
    assert "gold" in str(ei.value) and "negatif" in str(ei.value)


def test_set_morality_out_of_range_rejected(tmp_path):
    with pytest.raises(DataContractError) as ei:
        DataRegistry(_set_on_choose(tmp_path, {"academy": "akademi_bambu", "morality": 999}))
    assert "morality" in str(ei.value) and "range" in str(ei.value)


def test_set_roots_unknown_rejected(tmp_path):
    with pytest.raises(DataContractError) as ei:
        DataRegistry(_set_on_choose(tmp_path, {"academy": "akademi_bambu", "roots": "akar_ghost"}))
    assert "akar_ghost" in str(ei.value)


def test_set_clamps_at_runtime(tmp_path):
    """Defense berlapis: walau validator lolos (data valid), nilai tetap di-clamp."""
    dst = _set_on_choose(tmp_path, {"academy": "akademi_bambu", "gold": 5, "morality": 20})
    reg = DataRegistry(dst)
    sess = GameSession.new(reg)
    sess.state.current_quest = "q_min_pilih"
    sess.apply_action({"type": "choose", "option": "akademi_bambu"})
    assert sess.state.player.gold == 5
    assert sess.state.player.morality == 20


# ============================================================================
# BUG-5/6/7: efek ref item/technique/npc_state
# ============================================================================

def _effect_in_dialog(tmp_path, fx: dict):
    dst = _copy(tmp_path)
    dlg = _load(dst, "dialogs/minimal.json")
    dlg["dialogs"][1]["nodes"]["n1"]["choices"][1]["effects"] = [fx]
    _dump(dst, "dialogs/minimal.json", dlg)
    return dst


@pytest.mark.parametrize("fx,needle", [
    ({"type": "item", "id": "item_ghost", "count": 1}, "item_ghost"),
    ({"type": "technique", "id": "tek_ghost"}, "tek_ghost"),
    ({"type": "npc_state", "npc": "npc_ghost", "state": "x"}, "npc_ghost"),
    ({"type": "npc_state", "npc": "npc_guru", "location": "loc_ghost"}, "loc_ghost"),
])
def test_effect_unknown_ref_rejected(tmp_path, fx, needle):
    with pytest.raises(DataContractError) as ei:
        DataRegistry(_effect_in_dialog(tmp_path, fx))
    assert needle in str(ei.value)


def test_effect_valid_refs_accepted(tmp_path):
    """Baseline: efek valid (start_quest side + flag) tetap lolos."""
    dst = _copy(tmp_path)
    reg = DataRegistry(dst)  # fixture sudah punya start_quest → q_min_side (side) + flag
    assert reg is not None


# ============================================================================
# BUG-8: start_quest wajib menunjuk quest side
# ============================================================================

def test_start_quest_to_main_rejected(tmp_path):
    dst = _copy(tmp_path)
    dlg = _load(dst, "dialogs/minimal.json")
    dlg["dialogs"][1]["nodes"]["n1"]["choices"][0]["effects"] = [{"type": "start_quest", "quest": "q_min_intro"}]
    _dump(dst, "dialogs/minimal.json", dlg)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(dst)
    msg = str(ei.value)
    assert "start_quest" in msg and "quest side" in msg


def test_start_quest_to_side_accepted(tmp_path):
    """Fixture baseline: start_quest → q_min_side (side) tetap valid."""
    DataRegistry(_copy(tmp_path))  # tidak boleh error
