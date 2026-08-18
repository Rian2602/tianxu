"""Test adaptifitas engine terhadap data story — F3 (rencana kerja: engine + test).

Prinsip: engine harus berjalan benar pada data story APA PUN yang sah secara
kontrak — bukan hanya fixture minimal. Data dibuat PROGRAMATIK (bukan copy
fixture): rantai quest panjang, percabangan, file fitur opsional dihapus,
bentuk data bervariasi (tanpa description, random_text, NPC tanpa dialog).

Efisiensi: satu build data kecil per skenario (runtime < detik), langsung
memakai engine (bukan lewat CLI/web). Tidak menyentuh data/ atau saves/.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.validate import DataContractError
from src.engine.session import GameSession

# ---------- pembuat data sintetis ----------

DEFAULT_REALMS = [{
    "id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1", "levels": "5",
    "base_hp": "50", "hp_per_level": "5", "base_qi": "30", "qi_per_level": "3",
}]

DEFAULT_LOCATIONS = [{
    "id": "l_start", "name": "Start", "is_safe": True, "connections": ["l2"],
}, {
    "id": "l2", "name": "L2", "is_safe": False, "connections": ["l_start"],
}]

DEFAULT_ITEMS = [{"id": "i1", "name": "I1", "type": "consumable", "hp_restore": 5}]

DEFAULT_ENEMIES = [{"id": "e1", "name": "E1", "hp": 5, "attack": 1, "defense": 0, "exp_reward": 1}]


def _wcsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("id\n", encoding="utf-8")
        return
    cols = list(rows[0].keys())
    lines = [",".join(cols)] + [",".join(str(r.get(c, "")) for c in cols) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_data(tmp_path: Path, *, quests, npcs=(), dialogs=(), locations=DEFAULT_LOCATIONS,
               items=DEFAULT_ITEMS, enemies=DEFAULT_ENEMIES, realms=DEFAULT_REALMS,
               techniques=(), memories=None, companions=None, recipes=None,
               key_items=None, factions=None, config_extra=None, starting=None) -> Path:
    """Tulis dataset sintetis ke tmp_path/data dan kembalikan path-nya."""
    d = tmp_path / "data"
    (d / "quests").mkdir(parents=True, exist_ok=True)
    (d / "dialogs").mkdir()

    def w(name, obj):
        (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

    w("quests/story.json", {"quests": list(quests)})
    w("dialogs/story.json", {"dialogs": list(dialogs)})
    w("npcs.json", {"npcs": list(npcs)})
    w("locations.json", {"locations": list(locations)})
    w("config.json", {
        "starting": starting or {
            "player": {"name": "X", "hp": 50, "qi": 30, "realm": "r1", "realm_level": 1},
            "location": "l_start", "current_quest": quests[0]["id"],
        },
        "time": {"start_day": 1, "start_hour": 8, "month_length_days": 30},
        "academies": [{"id": "ac_1", "name": "Ac 1"}],
        "cultivation": {"grounding_max_hours_per_day": 8, "grounding_exp_per_hour": 4},
        "battle": {"statuses": {}},
        "world": {},
        "morality": {"min": -100, "max": 100},
        "arcs": [],
        "roots": {"tiers": [{"id": "root_1", "name": "R", "exp_multiplier": 1.0}]},
        **(config_extra or {}),
    })
    _wcsv(d / "items.csv", list(items))
    _wcsv(d / "enemies.csv", list(enemies))
    _wcsv(d / "realms.csv", list(realms))
    _wcsv(d / "techniques.csv", list(techniques))
    if memories is not None:
        w("memories.json", {"memories": memories})
    if companions is not None:
        w("companions.json", {"companions": companions})
    if recipes is not None:
        w("recipes.json", {"recipes": recipes})
    if key_items is not None:
        w("key_items.json", {"key_items": key_items})
    if factions is not None:
        w("factions.json", {"factions": factions})
    return d


def _session(tmp_path: Path, **kw):
    d = build_data(tmp_path, **kw)
    reg = DataRegistry(data_dir=d)
    return reg, GameSession.new(reg)


# ============================================================================
# Fitur opsional dihapus — tema baru boleh tidak punya memories/companions/...
# ============================================================================

def test_optional_feature_files_absent(tmp_path):
    """Tanpa memories.json/companions.json/recipes.json/key_items.json/hunts
    → boot, alur talk→choose, dan view tetap jalan."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "talk", "npc": "n1", "target": 1},
         "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
        dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                  "nodes": {"n1": {"speaker": "npc:n1", "text": "hi", "choices": []}}}],
        memories=None, companions=None)
    assert s.view()["mode"] == "explore"
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q1" in s.state.completed_quests
    s.apply_action({"type": "choose", "option": "a"})
    assert "q2" in s.state.completed_quests
    v = s.view()
    assert v["mode"] == "explore" and v["memories"] == [] and v["companion"] is None


def test_no_npcs_no_hunts_no_crash(tmp_path):
    """Dunia tanpa NPC & tanpa zona berburu → game tetap main (quest choose)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[])
    assert s.can_hunt() is False
    v = s.apply_action({"type": "hunt"})
    assert v["mode"] == "choose"  # mode quest aktif tetap; hanya log peringatan
    assert "q1" not in s.state.completed_quests  # hunt tidak menyelesaikan quest
    s.apply_action({"type": "choose", "option": "a"})
    assert "q1" in s.state.completed_quests


# ============================================================================
# Quest utama kind apa pun — DAG harus lanjut (bukan hanya fixture talk/choose)
# ============================================================================

def test_main_quest_gather_completes_and_advances(tmp_path):
    """Main quest kind=gather: selesai saat item cukup, DAG lanjut ke quest berikut."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "Kumpul", "objective": {"kind": "gather", "item": "i1", "target": 1},
         "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[])
    s.state.inventory["i1"] = 1
    s.quest.notify_gather()
    assert "q1" in s.state.completed_quests
    assert s.state.current_quest == "q2", "quest utama gather harus meneruskan DAG"


def test_main_quest_gather_report_to(tmp_path):
    """Main quest gather dengan report_to: kill/lapor ke NPC baru selesai."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "Lapor", "objective": {"kind": "gather", "item": "i1", "target": 1, "report_to": "n1"},
         "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
        dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                  "nodes": {"n1": {"speaker": "npc:n1", "text": "hi", "choices": []}}}])
    s.state.inventory["i1"] = 1
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q1" in s.state.completed_quests, "lapor ke pemberi harus menyelesaikan gather"
    assert s.state.current_quest == "q2"


def test_main_quest_all_kinds_chain(tmp_path):
    """Rantai 6 quest utama (talk→reach→defeat→advance_time→gather→choose):
    setiap kind selesai & DAG maju satu per satu — alur apa pun yang sah didukung."""
    qs = [
        {"id": "qtalk", "kind": "main", "title": "1", "objective": {"kind": "talk", "npc": "n1", "target": 1},
         "next": [{"quest": "qreach"}]},
        {"id": "qreach", "kind": "main", "title": "2", "objective": {"kind": "reach", "location": "l2"},
         "next": [{"quest": "qdefeat"}]},
        {"id": "qdefeat", "kind": "main", "title": "3", "objective": {"kind": "defeat", "target": 1},
         "next": [{"quest": "qadv"}]},
        {"id": "qadv", "kind": "main", "title": "4", "objective": {"kind": "advance_time", "hour": 10},
         "next": [{"quest": "qgather"}]},
        {"id": "qgather", "kind": "main", "title": "5", "objective": {"kind": "gather", "item": "i1", "target": 1},
         "next": [{"quest": "qchoose"}]},
        {"id": "qchoose", "kind": "main", "title": "6", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ]
    reg, s = _session(tmp_path, quests=qs,
                      npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
                      dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                                "nodes": {"n1": {"speaker": "npc:n1", "text": "hi", "choices": []}}}],
                      config_extra={"world": {"hunts": [{"id": "h1", "location": "l2", "pool": ["e1"], "search_item": "i1"}]}})
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.current_quest == "qreach"
    s.apply_action({"type": "move", "to": "l2"})
    assert s.state.current_quest == "qdefeat"
    s.apply_action({"type": "hunt"})
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert s.state.current_quest == "qadv"
    s.apply_action({"type": "advance_time", "hours": 2})  # 8+2=10 → target terpenuhi
    assert s.state.current_quest == "qgather"
    s.state.inventory["i1"] = 1
    s.quest.notify_gather()
    assert s.state.current_quest == "qchoose"
    s.apply_action({"type": "choose", "option": "a"})
    assert s.state.current_quest is None
    assert len(s.state.completed_quests) == 6


# ============================================================================
# Percabangan quest (DAG bercabang) — alur non-linear
# ============================================================================

def test_branch_quest_id_used_not_backward_search(tmp_path):
    """Harden select_branch (engine risk Claude): quest pemicu diambil dari
    `state.branch_quest` eksplisit, bukan pencarian mundur — tahan terhadap
    dua main quest ber-next yang selesai berdekatan tanpa branch dipilih."""
    quests = [
        {"id": "qstart", "kind": "main", "title": "S",
         "objective": {"kind": "choose", "options": [{"value": "x", "label": "X"}]},
         "next": [{"quest": "qb1", "option": "kiri", "choice_id": "dlg_br"},
                  {"quest": "qb2", "option": "kanan", "choice_id": "dlg_br"}]},
        {"id": "qb1", "kind": "main", "title": "B1",
         "objective": {"kind": "advance_time", "hour": 9}},
        {"id": "qb2", "kind": "main", "title": "B2",
         "objective": {"kind": "advance_time", "hour": 9}},
        # main quest ber-next lain yang "selesai" setelahnya (pengganggu pencarian mundur)
        {"id": "qlate", "kind": "main", "title": "L",
         "objective": {"kind": "advance_time", "hour": 9},
         "next": [{"quest": "qlate2"}]},
        {"id": "qlate2", "kind": "main", "title": "L2",
         "objective": {"kind": "advance_time", "hour": 9}},
    ]
    d = build_data(tmp_path, quests=quests, npcs=[],
                   dialogs=[{"id": "dlg_br", "start": "n1", "nodes": {"n1": {
                       "speaker": "narration", "text": "pilih", "choices": [
                           {"label": "Kiri", "option": "kiri"}, {"label": "Kanan", "option": "kanan"}]}}}])
    reg = DataRegistry(data_dir=d)
    s = GameSession.new(reg)
    s.apply_action({"type": "choose", "option": "x"})
    assert s.state.branch_pending == "dlg_br"
    assert s.state.branch_quest == "qstart"  # bukti eksplisit tersimpan
    # korupsi/edge: main quest ber-next lain masuk completed_quests setelahnya
    # (pencarian mundur lama akan salah pilih qlate); branch_quest tetap benar
    s.state.completed_quests.append("qlate")
    s.apply_action({"type": "dialog_choice", "choice_index": 0})
    assert s.state.current_quest == "qb1"  # dari branch_quest=qstart, bukan qlate
    assert s.state.branch_quest is None


def test_branch_quest_survives_save_load(tmp_path, monkeypatch):
    """branch_quest persist di save/load — select_branch tetap benar setelah
    muat (tidak bergantung urutan completed_quests)."""
    import src.engine.session as sess_mod
    import src.engine.state as state_mod
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path / "saves")
    (tmp_path / "saves").mkdir(exist_ok=True)
    quests = [
        {"id": "qstart", "kind": "main", "title": "S",
         "objective": {"kind": "choose", "options": [{"value": "x", "label": "X"}]},
         "next": [{"quest": "qb1", "option": "kiri", "choice_id": "dlg_br"},
                  {"quest": "qb2", "option": "kanan", "choice_id": "dlg_br"}]},
        {"id": "qb1", "kind": "main", "title": "B1",
         "objective": {"kind": "advance_time", "hour": 9}},
        {"id": "qb2", "kind": "main", "title": "B2",
         "objective": {"kind": "advance_time", "hour": 9}},
    ]
    d = build_data(tmp_path, quests=quests, npcs=[],
                   dialogs=[{"id": "dlg_br", "start": "n1", "nodes": {"n1": {
                       "speaker": "narration", "text": "pilih", "choices": [
                           {"label": "Kiri", "option": "kiri"}, {"label": "Kanan", "option": "kanan"}]}}}])
    reg = DataRegistry(data_dir=d)
    s = GameSession.new(reg)
    # simulasi state pasca-branch-quest (save tidak bisa dilakukan di tengah
    # dialog by design — jadi field di-set langsung seperti hasil quest selesai)
    s.state.completed_quests.append("qstart")
    s.state.branch_pending = "dlg_br"
    s.state.branch_quest = "qstart"
    s.apply_action({"type": "save", "save_name": "br"})
    s2 = GameSession.load(reg, "br")
    assert s2.state.branch_pending == "dlg_br"
    assert s2.state.branch_quest == "qstart"
    s2.view()  # alur nyata pasca-load: view memulai dialog branch
    assert s2.state.pending_dialog == "dlg_br"
    s2.apply_action({"type": "dialog_choice", "choice_index": 1})
    assert s2.state.current_quest == "qb2"
    assert s2.state.branch_quest is None


def test_branching_quest_both_paths(tmp_path):
    """Quest bercabang: dialog pemilih cabang → kedua cabang bisa diambil."""
    quests = [
        {"id": "qstart", "kind": "main", "title": "S", "objective": {"kind": "choose", "options": [{"value": "x", "label": "X"}]},
         "next": [{"quest": "qb1", "option": "kiri", "choice_id": "dlg_br"},
                  {"quest": "qb2", "option": "kanan", "choice_id": "dlg_br"}]},
        {"id": "qb1", "kind": "main", "title": "B1", "objective": {"kind": "advance_time", "hour": 9}},
        {"id": "qb2", "kind": "main", "title": "B2", "objective": {"kind": "advance_time", "hour": 9}},
    ]
    d = build_data(tmp_path, quests=quests, npcs=[],
                   dialogs=[{"id": "dlg_br", "start": "n1", "nodes": {"n1": {"speaker": "narration", "text": "pilih", "choices": [
                       {"label": "Kiri", "option": "kiri"}, {"label": "Kanan", "option": "kanan"}]}}}])
    reg = DataRegistry(data_dir=d)
    for idx, expect in ((0, "qb1"), (1, "qb2")):
        s = GameSession.new(reg)
        s.apply_action({"type": "choose", "option": "x"})
        assert s.state.branch_pending == "dlg_br"
        assert s.view()["mode"] == "dialog"
        s.apply_action({"type": "dialog_choice", "choice_index": idx})
        assert s.state.current_quest == expect, f"cabang index {idx} harus → {expect}"


# ============================================================================
# Bentuk data bervariasi — field opsional dihilangkan
# ============================================================================

def test_location_without_description(tmp_path):
    """Lokasi tanpa `description` (opsional) → view tidak KeyError."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "advance_time", "hour": 9}},
    ], npcs=[], locations=[{"id": "l_start", "name": "S", "is_safe": True, "connections": []}])
    v = s.view()
    assert v["location"]["description"] == ""
    assert v["mode"] == "explore"


def test_npc_without_dialog_routes(tmp_path):
    """NPC tanpa dialog_routes/default_dialog → talk tidak crash (degradasi aman)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "talk", "npc": "n1", "target": 1}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start"}], dialogs=[])
    v = s.apply_action({"type": "talk", "npc": "n1"})
    assert v["mode"] == "explore"


def test_dialog_random_text(tmp_path):
    """Dialog dengan random_text (bukan text) → jalan & quest talk selesai."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "talk", "npc": "n1", "target": 1}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
        dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                  "nodes": {"n1": {"speaker": "npc:n1", "random_text": ["a", "b"], "choices": []}}}])
    s.apply_action({"type": "talk", "npc": "n1"})
    v = s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q1" in s.state.completed_quests
    assert v["mode"] == "explore"


# ============================================================================
# Fungsional lain pada data sintetis: side quest, save/load, breakthrough
# ============================================================================

def test_main_quest_spar_flow(tmp_path):
    """Main quest spar: talk → battle dimulai otomatis → menang → DAG lanjut."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qspar", "kind": "main", "title": "Duel", "objective": {"kind": "spar", "npc": "n1"},
         "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start", "can_spar": True,
             "combat": {"hp": 5, "attack": 1, "defense": 0}}],
        dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                  "nodes": {"n1": {"speaker": "npc:n1", "text": "Ayo duel.", "choices": []}}}])
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.pending_battle is not None, "dialog spar harus membuka battle"
    assert s.state.pending_battle.get("spar_npc") == "n1"
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert "qspar" in s.state.completed_quests
    assert s.state.current_quest == "q2", "menang sparring harus meneruskan DAG"


def test_side_quest_spar_completes_on_win(tmp_path):
    """Side quest spar: menang sparing melawan NPC target → quest selesai."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qmain", "kind": "main", "title": "M", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
        {"id": "qside", "kind": "side", "title": "S", "objective": {"kind": "spar", "npc": "n1"}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start", "can_spar": True,
             "combat": {"hp": 5, "attack": 1, "defense": 0}}])
    assert s.quest.start_side("qside") is True
    s.apply_action({"type": "spar", "npc": "n1"})
    assert s.state.pending_battle is not None
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert "qside" in s.state.completed_quests, "side spar harus selesai saat menang"
    assert s.state.current_quest == "qmain"


def test_side_quest_flow_synthetic(tmp_path):
    """Side quest (gather) di dunia sintetis: start → kumpul → selesai."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qmain", "kind": "main", "title": "M", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
        {"id": "qside", "kind": "side", "title": "S", "objective": {"kind": "gather", "item": "i1", "target": 1}},
    ], npcs=[])
    assert s.quest.start_side("qside") is True
    s.state.inventory["i1"] = 1
    s.quest.notify_gather()
    assert "qside" in s.state.completed_quests
    assert s.state.current_quest == "qmain", "side quest tidak menyentuh quest utama"


def test_save_load_roundtrip_synthetic(tmp_path, monkeypatch):
    """Save/load round-trip pada data sintetis (inventori, quest aktif, flags)."""
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path)
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[])
    s.state.flags["x"] = 1
    s.state.inventory["i1"] = 3
    s.apply_action({"type": "save", "save_name": "synth"})
    loaded = GameSession.load(reg, "synth")
    assert loaded.state.flags == s.state.flags
    assert loaded.state.inventory == s.state.inventory
    assert loaded.state.current_quest == s.state.current_quest


def test_minimal_mechanics_columns(tmp_path):
    """Kolom mekanik opsional (base_hp/hp/levels) dihilangkan → engine tidak crash:
    view, battle, companion_stats, gain_exp semuanya jalan (default, bukan KeyError)."""
    from src.engine.battle import companion_stats
    from src.engine.cultivation import gain_exp
    d = build_data(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], enemies=[{"id": "e1", "name": "E", "attack": 1}],
        realms=[{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1"}],  # tanpa levels/base_hp
        companions=[{"id": "c1", "name": "C"}])  # tanpa base_hp/dll
    reg = DataRegistry(data_dir=d)
    s = GameSession.new(reg)
    assert s.view()["player"]["hp_max"] >= 1  # max_hp default, bukan KeyError
    gain_exp(s.state, reg, 100)  # level-up dengan levels default
    s.state.companion = {"id": "c1", "hp": 10, "active": True}
    assert companion_stats(s.state, reg) is not None
    s.battle.start([dict(reg.enemies["e1"])], "hunt")
    assert s.state.pending_battle is not None  # battle start tanpa kolom hp


def test_breakthrough_to_second_realm(tmp_path):
    """Dua ranah → exp cukup memicu level-up & terobosan otomatis (fungsi engine)."""
    realms = DEFAULT_REALMS + [{
        "id": "r2", "name": "R2", "name_pinyin": "R2", "order": "2", "levels": "3",
        "base_hp": "80", "hp_per_level": "8", "base_qi": "50", "qi_per_level": "5",
    }]
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], realms=realms)
    from src.engine.cultivation import gain_exp
    s.state.player.exp = 0
    gain_exp(s.state, reg, 1000)  # jauh melebihi kebutuhan 5 level r1
    assert s.state.player.realm == "r2", "terobosan otomatis ke ranah berikutnya"
    assert 1 <= s.state.player.realm_level <= 3  # naik level lanjut di ranah baru
    msgs = "\n".join(e["text"] for e in s.state.log)
    assert "Terobosan" in msgs


# ============================================================================
# Fitur data-driven lain yang belum teruji: key item, shop, fail_next, memory
# ============================================================================

def test_key_item_use_effects_and_consumed(tmp_path):
    """Key item (data/key_items.json) dengan use_effects + consumed: dipakai →
    efek diterapkan (flag/gold) & item hilang dari inventori."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], items=[{"id": "k1", "name": "Kunci Gerbang", "type": "key_item"}],
        key_items=[{"id": "k1", "description": "Gerbang terbuka.", "consumed": True,
                    "use_effects": [{"type": "flag", "key": "gerbang_terbuka", "value": True},
                                    {"type": "gold", "value": 5}]}])
    s.state.inventory["k1"] = 1
    s.apply_action({"type": "use_key_item", "item": "k1"})
    assert s.state.flags.get("gerbang_terbuka") is True
    assert s.state.player.gold == 5
    assert "k1" not in s.state.inventory, "key item consumed harus hilang"
    assert "Gerbang terbuka" in "\n".join(e["text"] for e in s.state.log)


def test_key_item_not_consumed_stays(tmp_path):
    """Key item tanpa `consumed` → tetap di inventori setelah dipakai."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], items=[{"id": "k2", "name": "Lencana", "type": "key_item"}],
        key_items=[{"id": "k2", "description": "Tanda kehormatan.", "consumed": False,
                    "use_effects": [{"type": "flag", "key": "dihormati", "value": True}]}])
    s.state.inventory["k2"] = 1
    s.apply_action({"type": "use_key_item", "item": "k2"})
    assert s.state.inventory.get("k2") == 1


def test_key_item_without_use_effects_untouchable(tmp_path):
    """Key item tanpa use_effects → tidak bisa dipakai (log jelas), bukan crash."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], items=[{"id": "k3", "name": "Benda Pusaka", "type": "key_item"}],
        key_items=[{"id": "k3", "description": "Hanya hiasan.", "consumed": False}])
    s.state.inventory["k3"] = 1
    s.apply_action({"type": "use_key_item", "item": "k3"})
    assert s.state.inventory.get("k3") == 1
    assert "tidak bisa dipakai" in "\n".join(e["text"] for e in s.state.log)


def test_shop_buy_sell_flow(tmp_path):
    """Toko NPC (data npcs.json): beli → gold turun & item masuk; jual → balik;
    guard gold kurang & item tak dijual tetap berfungsi (bukan crash)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[{"id": "n1", "name": "Pedagang", "location": "l_start",
              "shop": {"buy": [{"item": "i1", "price": 10}],
                       "sell": [{"item": "i1", "price": 4}]}}])
    s.state.player.gold = 100
    s.apply_action({"type": "shop_buy", "item": "i1", "count": 2})
    assert s.state.player.gold == 80 and s.state.inventory.get("i1") == 2
    s.apply_action({"type": "shop_sell", "item": "i1", "count": 1})
    assert s.state.player.gold == 84 and s.state.inventory.get("i1") == 1
    # gold tidak cukup → tolak, tidak ada perubahan
    s.apply_action({"type": "shop_buy", "item": "i1", "count": 99})
    assert s.state.player.gold == 84 and s.state.inventory.get("i1") == 1
    assert "tidak cukup" in "\n".join(e["text"] for e in s.state.log)
    # item yang tidak dijual → tolak
    s.apply_action({"type": "shop_buy", "item": "bukan_dijual"})
    assert "tidak menjual" in "\n".join(e["text"] for e in s.state.log)


def test_main_quest_timeout_fail_next(tmp_path):
    """G3-T1: main quest ber-deadline gagal saat batas tercapai → fail_effects
    diterapkan, tercatat failed, DAG lanjut ke `fail_next`."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "Misi Waktu",
         "objective": {"kind": "reach", "location": "l2"},
         "timeout": {"hours": 24},
         "fail_effects": [{"type": "flag", "key": "misi_gagal", "value": True}],
         "fail_system_msg": "Waktu habis.",
         "fail_next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[])
    assert s.state.current_quest == "q1"
    s.apply_action({"type": "rest", "hours": 24})  # l_start aman → maju 24 jam
    assert "q1" in s.state.failed_quests
    assert s.state.flags.get("misi_gagal") is True, "fail_effects harus diterapkan"
    assert s.state.current_quest == "q2", "fail_next harus meneruskan DAG"
    assert "Waktu habis" in "\n".join(e["text"] for e in s.state.log)


def test_side_quest_timeout_removes(tmp_path):
    """Side quest ber-deadline: gagal → tercatat failed + hapus dari aktif,
    tanpa menyentuh quest utama (side tidak butuh fail_next)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qmain", "kind": "main", "title": "M", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
        {"id": "qside", "kind": "side", "title": "S", "objective": {"kind": "gather", "item": "i1", "target": 1},
         "timeout": {"hours": 24}},
    ], npcs=[])
    assert s.quest.start_side("qside") is True
    s.apply_action({"type": "rest", "hours": 24})
    assert "qside" in s.state.failed_quests
    assert "qside" not in s.state.active_side_quests
    assert s.state.current_quest == "qmain"


def test_memory_reliability_update(tmp_path):
    """Ingatan (memories.json): unlock dengan reliability → view menampilkannya;
    update_reliability mengubahnya (event koreksi cerita); id tak dikenal no-op."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], memories=[{"id": "m1", "title": "Kilasan", "text": "...", "reliability": "high"}])
    from src.engine.memory import unlock, update_reliability
    unlock(s.state, reg, "m1", "low")
    assert s.view()["memories"][0]["reliability"] == "low"
    update_reliability(s.state, "m1", "high")
    assert s.view()["memories"][0]["reliability"] == "high"
    unlock(s.state, reg, "m_ghost")  # id tak dikenal → no-op aman
    assert len(s.state.memories) == 1


def test_search_success_adds_item(tmp_path, monkeypatch):
    """Cari sukses (random < 0.6): item `search_item` zona bertambah & quest
    gather main menerima notify (bukan hanya side)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qmain", "kind": "main", "title": "M", "objective": {"kind": "gather", "item": "i1", "target": 1}},
    ], npcs=[], config_extra={"world": {"hunts": [{"id": "h1", "location": "l_start", "pool": ["e1"], "search_item": "i1"}]}})
    import random as rnd
    monkeypatch.setattr(rnd, "random", lambda: 0.0)
    s.apply_action({"type": "search"})
    assert s.state.inventory.get("i1") == 1
    assert "qmain" in s.state.completed_quests, "search sukses harus memicu notify_gather"


def test_side_spar_loss_completes(tmp_path):
    """G4a: KALAH sparring tetap menyelesaikan side quest spar (dialog berbeda)."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qmain", "kind": "main", "title": "M", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
        {"id": "qside", "kind": "side", "title": "Duel", "objective": {"kind": "spar", "npc": "n1"}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start", "can_spar": True,
              "combat": {"hp": 100, "attack": 50, "defense": 0}}])
    assert s.quest.start_side("qside") is True
    s.apply_action({"type": "spar", "npc": "n1"})
    assert s.state.pending_battle is not None
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert "qside" in s.state.completed_quests, "kalah sparring tetap selesai (G4a)"
    assert s.state.current_quest == "qmain"


def test_main_quest_spar_loss_completes_with_flag(tmp_path):
    """G4a: kalah sparring → quest spar utama selesai + flag `spar_kalah`."""
    reg, s = _session(tmp_path, quests=[
        {"id": "qspar", "kind": "main", "title": "Duel", "objective": {"kind": "spar", "npc": "n1"},
         "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "title": "T2", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[{"id": "n1", "name": "N", "location": "l_start", "can_spar": True,
              "combat": {"hp": 100, "attack": 50, "defense": 0}}],
        dialogs=[{"id": "dlg1", "npc": "n1", "start": "n1",
                  "nodes": {"n1": {"speaker": "npc:n1", "text": "Ayo duel.", "choices": []}}}])
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.pending_battle is not None
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.apply_action({"type": "battle_action", "action": "attack"})
        guard += 1
    assert "qspar" in s.state.completed_quests
    assert s.state.flags.get("spar_kalah") is True
    assert s.state.current_quest == "q2"


def test_upgrade_technique_flow(tmp_path):
    """C1: tingkatkan teknik di titik aman — gold turun & level naik; batas
    ranah (order+1); teknik tak dimiliki/tak dikenal ditolak."""
    reg, s = _session(tmp_path, quests=[
        {"id": "q1", "kind": "main", "title": "T", "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}},
    ], npcs=[], techniques=[{"id": "t1", "name": "T1", "kind": "attack", "power": 5,
                             "qi_cost": 3, "realm_required": "r1", "element": ""}])
    s.state.player.techniques.append("t1")
    s.state.player.gold = 100
    # ranah r1 order=1 → max level = order+1 = 2
    s.apply_action({"type": "upgrade_technique", "technique": "t1"})
    assert s.state.player.technique_levels.get("t1") == 2
    assert s.state.player.gold == 80  # biaya dasar 20 × level 1
    s.apply_action({"type": "upgrade_technique", "technique": "t1"})  # sudah maksimal
    assert s.state.player.technique_levels.get("t1") == 2
    assert "maksimal" in "\n".join(e["text"] for e in s.state.log)
    s.apply_action({"type": "upgrade_technique", "technique": "t_ghost"})
    assert "Teknik tidak dikenal" in "\n".join(e["text"] for e in s.state.log)


# ============================================================================
# Registri faksi (docs 05) — OPSIONAL, closed-set saat ada, view ekspos nama
# ============================================================================

FACTIONS = [{"id": "faction_tianxu_orthodox", "name": "Ortodoks Tianxu"},
            {"id": "faction_reformists", "name": "Reformis"}]


def test_faction_registry_optional_without_file(tmp_path):
    """Tanpa factions.json — tema tanpa sistem faksi tetap boot; reputasi
    dict bebas tetap jalan (kompatibel)."""
    reg, s = _session(tmp_path, quests=[{"id": "q1", "kind": "main", "title": "T",
                                         "objective": {"kind": "choose",
                                                        "options": [{"value": "a", "label": "A"}]}}])
    assert reg.factions == []
    s.apply_action({"type": "use_key_item", "item": "x"})  # tidak crash tanpa faksi
    assert s.view()["factions"] == []


def test_faction_registry_effect_and_condition(tmp_path):
    """factions.json ada → effect reputation + condition faction_min bekerja;
    view mengekspos nama faksi dari data."""
    reg, s = _session(tmp_path,
                      quests=[{"id": "q1", "kind": "main", "title": "T",
                               "objective": {"kind": "choose",
                                              "options": [{"value": "a", "label": "A",
                                                            "set": {"academy": "ac_1"}}]},
                               "on_complete": {"effects": [
                                   {"type": "reputation", "faksi": "faction_tianxu_orthodox", "value": 5}]}}],
                      factions=FACTIONS)
    assert reg.faction_by_id["faction_reformists"]["name"] == "Reformis"
    s.apply_action({"type": "choose", "option": "a"})
    v = s.view()
    assert v["factions"][0]["id"] == "faction_tianxu_orthodox"
    assert v["factions"][0]["score"] == 5
    assert v["factions"][0]["name"] == "Ortodoks Tianxu"


def test_faction_registry_unknown_rejected(tmp_path):
    """factions.json ada → typo id faksi di effect/condition ditolak validator
    (closed-set cross-reference, pola quest/item)."""
    d = build_data(tmp_path, quests=[{"id": "q1", "kind": "main", "title": "T",
                                      "objective": {"kind": "choose",
                                                     "options": [{"value": "a", "label": "A"}]},
                                      "on_complete": {"effects": [
                                          {"type": "reputation", "faksi": "faction_ghost", "value": 1}]}}],
                     factions=FACTIONS)
    with pytest.raises(DataContractError) as ei:
        DataRegistry(data_dir=d)
    assert "faksi tak dikenal: 'faction_ghost'" in str(ei.value)


# ============================================================================
# Kontrak fitur dikunci (E/C/H) — field wajib di data, bukan id/konten
# ============================================================================

def _quest_choose():
    return {"id": "q1", "kind": "main", "title": "T",
            "objective": {"kind": "choose",
                           "options": [{"value": "a", "label": "A"}]}}


def test_memory_contract_missing_title_or_text_rejected(tmp_path):
    """E1 (docs 06): memory tanpa title/text ditolak saat load — bukan
    softlock saat ditampilkan. Field wajib dikunci, isi teks tetap data."""
    d = build_data(tmp_path, quests=[_quest_choose()], memories=[{"id": "mem_x"}])
    with pytest.raises(DataContractError) as ei:
        DataRegistry(data_dir=d)
    assert "memory 'mem_x' — memory wajib punya 'title'" in str(ei.value)
    assert "memory 'mem_x' — memory wajib punya 'text'" in str(ei.value)


def test_memory_contract_valid_with_reliability(tmp_path):
    """E1 (docs 06): memory valid + reliability string diterima; unlock
    memakai reliability data; runtime tidak crash tanpa field opsional."""
    reg, s = _session(tmp_path, quests=[_quest_choose()],
                      memories=[{"id": "mem_1", "title": "J", "text": "X",
                                 "reliability": "RENDAH"}])
    s.apply_action({"type": "choose", "option": "a"})
    from src.engine import memory as mem_mod
    mem_mod.unlock(s.state, reg, "mem_1")
    assert s.state.memories[-1] == {"id": "mem_1", "reliability": "RENDAH"}
    v = s.view()
    assert v["memories"][0]["reliability"] == "RENDAH"


def test_memory_unlock_no_crash_on_odd_title(tmp_path):
    """E: unlock memory dengan title non-string tetap tidak crash (log pakai
    fallback id). Fitur unlock dikunci, bukan format title."""
    reg, s = _session(tmp_path, quests=[_quest_choose()],
                      memories=[{"id": "mem_1", "title": 123, "text": "X"}])
    from src.engine import memory as mem_mod
    mem_mod.unlock(s.state, reg, "mem_1")
    assert "mem_1" in [m["id"] for m in s.state.memories]


def test_companion_contract_missing_name_rejected(tmp_path):
    """C5 (docs 04): companion tanpa name ditolak saat load (name dipakai
    battle/view)."""
    d = build_data(tmp_path, quests=[_quest_choose()], companions=[{"id": "c1"}])
    with pytest.raises(DataContractError) as ei:
        DataRegistry(data_dir=d)
    assert "companion 'c1' — companion wajib punya 'name'" in str(ei.value)


def test_ending_contract_missing_id_or_title_rejected(tmp_path):
    """H1 (docs 11): ending wajib id + title — tanpa itu CLI/arc-summary
    merender baris kosong/absen diam-diam."""
    d = build_data(tmp_path, quests=[_quest_choose()],
                   config_extra={"arcs": [{"id": "arc1", "final_quest": "q1",
                                            "title": "A", "teaser": "t",
                                            "endings": [{"desc": "x"}]}]})
    with pytest.raises(DataContractError) as ei:
        DataRegistry(data_dir=d)
    assert "ending wajib punya 'id'" in str(ei.value)
    assert "ending wajib punya 'title'" in str(ei.value)
