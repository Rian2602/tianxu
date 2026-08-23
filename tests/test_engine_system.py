"""Test sistem engine pada data sintetis — putaran pengujian engine (Test Data Driven).

Memakai pembuat data programatik yang sama dengan test_adaptivity (satu sumber
pembangun, tidak menyalin fixture). Mencakup jalur yang belum teruji sebelumnya:

- battle: item/heal/defend (guard dikonsumsi per giliran)/stun/flee/KO
- dialog: rantai `next` + entry `once`
- quest: advance_time day_offset, reach time_window (main + side),
  defeat `enemies` filter (deterministik), gather report_to MENYERAHKAN item
- sesi: npc_state (location/available), jadwal NPC lintas malam, spar_require,
  equip → bonus attack, craft multi-bahan, bulan bergulir, search gagal
- hunt: pool malam (night_window) + mini_boss
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.engine.session import GameSession

# pembuat data — impor dari test_adaptivity agar satu sumber (bukan duplikat)
from tests.test_adaptivity import build_data


def _sess(tmp_path, **kw):
    d = build_data(tmp_path, **kw)
    reg = DataRegistry(data_dir=d)
    return reg, GameSession.new(reg)


CHOOSE = {"kind": "choose", "options": [{"value": "a", "label": "A"}]}
Q = lambda **kw: {"id": "q1", "kind": "main", "title": "T", "objective": CHOOSE, **kw}
DLG = {"id": "dlg1", "npc": "n1", "start": "n0",
       "nodes": {"n0": {"speaker": "npc:n1", "text": "hi", "choices": []}}}


# ============================================================================
# Battle — aksi pemain & hasil battle
# ============================================================================

def test_battle_item_heal_defend_stun_flee(tmp_path, monkeypatch):
    """Item/teknik heal/defend di battle; stun melewatkan aksi; flee mengakhiri.
    Musuh attack=0 → damage tepat 1/ronde (min-damage engine) sehingga angka
    deterministik: item +10 → musuh −1; heal +20 (cap) → musuh −1."""
    teks = [
        {"id": "t_heal", "name": "Pulih", "kind": "heal", "power": 20, "qi_cost": 3,
         "realm_required": "r1", "element": ""},
        {"id": "t_def", "name": "Tahan", "kind": "defend", "power": 30, "qi_cost": 2,
         "realm_required": "r1", "element": ""},
    ]
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[], techniques=teks,
                   items=[{"id": "i1", "name": "I1", "type": "consumable", "hp_restore": 10}],
                   enemies=[{"id": "e1", "name": "E1", "hp": 100, "attack": 0, "defense": 0}],
                   config_extra={"battle": {"statuses": {"stun1": {"name": "Pana", "kind": "stun", "duration": 2, "max_duration": 5}}}})
    s.state.player.techniques.extend(["t_heal", "t_def"])
    s.state.inventory["i1"] = 3
    s.state.player.hp = 30
    s.battle.start([dict(reg.enemies["e1"])], "hunt")

    s.battle.player_action({"action": "item", "item": "i1"})
    assert s.state.player.hp == 39 and s.state.inventory.get("i1") == 2  # +10, musuh −1

    s.battle.player_action({"action": "technique", "technique": "t_heal"})
    assert s.state.player.hp == 49  # 39+20=59 → cap 50, musuh −1

    # defend: guard diset, lalu DIKONSUMSI giliran musuh (reset False) — bukti via log
    s.battle.player_action({"action": "technique", "technique": "t_def"})
    assert s.state.pending_battle.get("player_guard") is False
    assert "dikurangi 30%" in "\n".join(e["text"] for e in s.state.log)

    # stun → aksi pemain di-skip (HP musuh tidak berubah giliran itu)
    s.state.pending_battle["player_statuses"] = {"stun1": 1}
    foe_hp = s.state.pending_battle["foes"][0]["hp"]
    s.battle.player_action({"action": "attack"})
    assert s.state.pending_battle["foes"][0]["hp"] == foe_hp
    assert "terpana" in "\n".join(e["text"] for e in s.state.log)

    # flee sukses (random dipaksa 0.0)
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod.random, "random", lambda: 0.0)
    s.state.pending_battle["player_statuses"] = {}
    s.battle.player_action({"action": "flee"})
    assert s.state.pending_battle is None, "flee mengakhiri battle"


def test_battle_ko_ends_and_resets(tmp_path):
    """Kalah (KO): battle berakhir, pemain respawn di titik aman dengan HP penuh."""
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   enemies=[{"id": "e1", "name": "E1", "hp": 100, "attack": 100, "defense": 0}])
    s.state.location = "l2"  # bukan titik aman — KO harus memindahkan pulang
    s.battle.start([dict(reg.enemies["e1"])], "hunt")
    s.battle.player_action({"action": "attack"})
    assert s.state.pending_battle is None, "KO menutup battle"
    assert s.state.location == "l_start", "respawn di titik aman (last_safe)"
    assert s.state.player.hp == s.state.max_hp(reg), "HP pulih penuh saat respawn"


# ============================================================================
# Dialog — rantai next & entry once
# ============================================================================

def test_dialog_next_chain_and_once(tmp_path):
    """Node ber-`next` diikuti; `advance()` auto-lanjut sampai akhir. Entry
    ber-`once`: pending sebelum dimainkan, selesai setelahnya."""
    dialogs = [
        {"id": "dlg1", "npc": "n1", "start": "n0",
         "nodes": {"n0": {"speaker": "npc:n1", "text": "A", "next": "n1"},
                   "n1": {"speaker": "npc:n1", "text": "B", "choices": []}}},
        {"id": "dlg_once", "npc": "n1", "start": "n0",
         "nodes": {"n0": {"speaker": "npc:n1", "text": "sekali", "once": True, "choices": []}}},
    ]
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
                   dialogs=dialogs)
    s.dialog.start("dlg1")
    assert s.dialog.node_id == "n0"
    s.dialog.advance()  # auto-lanjut: n0 → n1 → (tanpa next/choices) akhir
    assert s.dialog.current is None and not s.dialog.node_id, "dialog tuntas"

    assert s.dialog.has_pending_once_entry("dlg_once") is True
    s.dialog.start("dlg_once")
    s.dialog.advance()
    assert s.dialog.has_pending_once_entry("dlg_once") is False, "once dimainkan → selesai"


# ============================================================================
# Quest — varian objektif & penyerahan item
# ============================================================================

def test_advance_time_day_offset(tmp_path):
    """advance_time dengan day_offset: target waktu ABSOLUT (hari+jam)."""
    reg, s = _sess(tmp_path, quests=[Q(id="q1", objective={"kind": "advance_time", "hour": 10, "day_offset": 1})],
                   npcs=[])
    s.apply_action({"type": "advance_time", "hours": 2})  # day1 h10 — belum
    assert s.state.current_quest == "q1"
    s.apply_action({"type": "advance_time", "hours": 24})  # day2 h10 — tercapai
    assert s.state.current_quest is None and "q1" in s.state.completed_quests


def test_reach_time_window_main_and_side(tmp_path):
    """reach dengan time_window: side selesai di window-nya, main (lintas malam
    18–6) hanya bila jam dalam window."""
    qs = [Q(id="qmain", objective={"kind": "reach", "location": "l2",
                                   "time_window": {"hour_start": 18, "hour_end": 6}}),
          {"id": "qside", "kind": "side", "title": "S",
           "objective": {"kind": "reach", "location": "l2",
                         "time_window": {"hour_start": 8, "hour_end": 20}}}]
    reg, s = _sess(tmp_path, quests=qs, npcs=[])
    s.quest.start_side("qside")
    s.apply_action({"type": "move", "to": "l2"})  # jam 8: dalam window side
    assert "qside" in s.state.completed_quests
    assert s.state.current_quest == "qmain", "main di luar window belum selesai"
    s.apply_action({"type": "advance_time", "hours": 12})  # jam 20: dalam window main
    assert s.state.current_quest is None


def test_defeat_enemies_filtered(tmp_path, monkeypatch):
    """defeat dengan `enemies`: hanya musuh dalam daftar yang menambah progres —
    deterministik via random.choice dipaksa."""
    qs = [Q(id="qmain", objective={"kind": "defeat", "target": 1, "enemies": ["e1"]}),
          {"id": "qside", "kind": "side", "title": "S",
           "objective": {"kind": "defeat", "target": 1, "enemies": ["e2"]}}]
    reg, s = _sess(tmp_path, quests=qs, npcs=[],
                   enemies=[{"id": "e1", "name": "E1", "hp": 5, "attack": 0, "defense": 0},
                            {"id": "e2", "name": "E2", "hp": 5, "attack": 0, "defense": 0}],
                   config_extra={"world": {"hunts": [{"id": "h1", "location": "l2", "pool": ["e1", "e2"],
                                                      "mini_boss_chance": 0.0}]}})
    s.quest.start_side("qside")
    s.apply_action({"type": "move", "to": "l2"})
    import src.engine.session as sess_mod
    monkeypatch.setattr(sess_mod.random, "choice", lambda seq: "e1")
    s.apply_action({"type": "hunt"})
    guard = 0
    while s.state.pending_battle and guard < 30:
        s.battle.player_action({"action": "attack"})
        guard += 1
    assert "qmain" in s.state.completed_quests, "e1 memenuhi main (enemies [e1])"
    assert "qside" not in s.state.completed_quests, "e1 TIDAK memenuhi side (enemies [e2])"
    assert "qside" in s.state.active_side_quests


def test_gather_report_to_main_consumes_item(tmp_path):
    """gather report_to (MAIN): selesai saat lapor DAN item benar-benar diserahkan."""
    reg, s = _sess(tmp_path,
                   quests=[Q(id="q1", objective={"kind": "gather", "item": "i1", "target": 1, "report_to": "n1"})],
                   npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
                   dialogs=[DLG], items=[{"id": "i1", "name": "I1", "type": "consumable", "hp_restore": 1}])
    s.state.inventory["i1"] = 1
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "q1" in s.state.completed_quests
    assert "i1" not in s.state.inventory, "item harus diserahkan saat lapor"
    assert "Menyerahkan" in "\n".join(e["text"] for e in s.state.log)


def test_gather_report_to_side_consumes_item(tmp_path):
    """gather report_to (SIDE): selesai saat lapor + item diserahkan."""
    reg, s = _sess(tmp_path,
                   quests=[Q(), {"id": "qside", "kind": "side", "title": "S",
                                 "objective": {"kind": "gather", "item": "i1", "target": 1, "report_to": "n1"}}],
                   npcs=[{"id": "n1", "name": "N", "location": "l_start"}],
                   dialogs=[DLG], items=[{"id": "i1", "name": "I1", "type": "consumable", "hp_restore": 1}])
    assert s.quest.start_side("qside") is True
    s.state.inventory["i1"] = 1
    s.quest.notify_gather()
    assert "qside" not in s.state.completed_quests, "belum lapor → belum selesai"
    s.apply_action({"type": "talk", "npc": "n1"})
    s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert "qside" in s.state.completed_quests
    assert "i1" not in s.state.inventory, "item harus diserahkan saat lapor"


# ============================================================================
# Sesi — NPC, jadwal, spar, equip, craft, waktu, hunt
# ============================================================================

def test_npc_state_location_and_available(tmp_path):
    """npc_state: override location memungkinkan bicara; available=false menolak."""
    reg, s = _sess(tmp_path, quests=[Q()],
                   npcs=[{"id": "n1", "name": "N", "location": "l2"}],
                   dialogs=[DLG])
    s.apply_action({"type": "talk", "npc": "n1"})
    assert s.state.pending_dialog is None, "NPC di l2, pemain di l_start"
    from src.engine.effects import apply
    apply(s.state, reg, [{"type": "npc_state", "npc": "n1", "location": "l_start"}])
    assert s.npc_location(reg.npcs[0]) == "l_start"
    s.apply_action({"type": "talk", "npc": "n1"})
    assert s.state.pending_dialog is not None
    apply(s.state, reg, [{"type": "npc_state", "npc": "n1", "available": False}])
    s.state.pending_dialog = None
    s.apply_action({"type": "talk", "npc": "n1"})
    assert s.state.pending_dialog is None, "NPC unavailable tidak bisa diajak bicara"


def test_npc_schedule_window_crosses_midnight(tmp_path):
    """Jadwal NPC 19–6 (lintas malam): jam 8 tidak tersedia, jam 20 tersedia."""
    reg, s = _sess(tmp_path, quests=[Q()],
                   npcs=[{"id": "n1", "name": "N", "location": "l_start",
                          "schedule": [{"hour_start": 19, "hour_end": 6}]}],
                   dialogs=[DLG])
    assert s._is_npc_available(reg.npcs[0]) is False  # jam 8
    s.apply_action({"type": "talk", "npc": "n1"})
    assert s.state.pending_dialog is None
    s.apply_action({"type": "advance_time", "hours": 12})  # jam 20
    assert s._is_npc_available(reg.npcs[0]) is True
    s.apply_action({"type": "talk", "npc": "n1"})
    assert s.state.pending_dialog is not None


def test_spar_require_condition_gates_can_spar(tmp_path):
    """can_spar menghormati spar_require (kondisi dialog) — data-driven."""
    reg, s = _sess(tmp_path, quests=[Q()],
                   npcs=[{"id": "n1", "name": "N", "location": "l_start", "can_spar": True,
                          "combat": {"hp": 5, "attack": 1, "defense": 0},
                          "spar_require": {"flag": {"key": "dilatih", "value": True}}}])
    assert s.can_spar(reg.npcs[0]) is False
    s.state.flags["dilatih"] = True
    assert s.can_spar(reg.npcs[0]) is True


def test_equip_weapon_gives_attack_bonus(tmp_path):
    """Memasang senjata menambah attack (player_combat)."""
    from src.engine.battle import player_combat
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   items=[{"id": "w1", "name": "W1", "type": "weapon", "power": 7}])
    atk0 = player_combat(s.state, reg)["attack"]
    s.state.inventory["w1"] = 1
    s.apply_action({"type": "equip", "item": "w1"})
    assert player_combat(s.state, reg)["attack"] == atk0 + 7


def test_craft_multi_ingredient(tmp_path):
    """Craft multi-bahan: hasil sesuai count, bahan habis terpakai."""
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   items=[{"id": "a", "name": "A", "type": "consumable", "hp_restore": 1},
                          {"id": "b", "name": "B", "type": "consumable", "hp_restore": 1},
                          {"id": "c", "name": "C", "type": "consumable", "hp_restore": 5}],
                   recipes=[{"id": "r1", "result": "c", "count": 2,
                             "ingredients": [{"item": "a", "count": 2}, {"item": "b", "count": 1}]}])
    s.state.inventory["a"] = 2
    s.state.inventory["b"] = 1
    s.apply_action({"type": "craft", "recipe": "r1"})
    assert s.state.inventory.get("c") == 2
    assert "a" not in s.state.inventory and "b" not in s.state.inventory


def test_month_rollover_and_name(tmp_path):
    """Bulan bergulir sesuai month_length_days; month_name dari data."""
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   config_extra={"time": {"start_day": 1, "start_hour": 8, "month_length_days": 30,
                                          "month_names": ["Bulan Satu", "Bulan Dua"]}})
    assert s.state.month(reg) == 1 and s.state.month_name(reg) == "Bulan Satu"
    s.apply_action({"type": "advance_time", "hours": 30 * 24})
    assert s.state.month(reg) == 2 and s.state.month_name(reg) == "Bulan Dua"


def test_hunt_night_pool_and_mini_boss(tmp_path):
    """Hunt: night_window memilih night_pool di malam; mini_boss menggantikan pool."""
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   enemies=[{"id": "e_day", "name": "D", "hp": 5, "attack": 0, "defense": 0},
                            {"id": "e_night", "name": "N", "hp": 5, "attack": 0, "defense": 0},
                            {"id": "e_boss", "name": "B", "hp": 20, "attack": 0, "defense": 0}],
                   config_extra={"world": {"hunts": [{"id": "h1", "location": "l2", "pool": ["e_day"],
                                                      "night_window": {"hour_start": 19, "hour_end": 6},
                                                      "night_pool": ["e_night"], "mini_boss_chance": 0.0}]}})
    s.apply_action({"type": "move", "to": "l2"})
    s.apply_action({"type": "hunt"})  # jam 8 siang
    assert s.state.pending_battle["foes"][0]["id"] == "e_day"
    s.state.pending_battle = None
    s.apply_action({"type": "advance_time", "hours": 11})  # jam 19 malam
    s.apply_action({"type": "hunt"})
    assert s.state.pending_battle["foes"][0]["id"] == "e_night"

    # mini_boss terpisah: chance 1.0 → boss (bukan pool); build di subdir sendiri
    reg2, s2 = _sess(tmp_path / "boss", quests=[Q()], npcs=[],
                     enemies=[{"id": "e_day", "name": "D", "hp": 5, "attack": 0, "defense": 0},
                              {"id": "e_boss", "name": "B", "hp": 20, "attack": 0, "defense": 0}],
                     config_extra={"world": {"hunts": [{"id": "h1", "location": "l2", "pool": ["e_day"],
                                                        "mini_boss": "e_boss", "mini_boss_chance": 1.0}]}})
    s2.apply_action({"type": "move", "to": "l2"})
    s2.apply_action({"type": "hunt"})
    assert s2.state.pending_battle["foes"][0]["id"] == "e_boss"


# ============================================================================
# Fitur dokumen yang DIKUNCI dengan test (kunci fitur, bukan data)
# ============================================================================

def test_arc_summary_and_ending_pick_by_condition(tmp_path):
    """H3/H1 (docs 11): arc_summary muncul setelah final quest selesai; ending
    dipilih first-match berdasarkan kondisi (bukan hardcode urutan)."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q_final", "kind": "main", "title": "Final",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   dialogs=[{"id": "dlg_dummy_flags", "start": "n1", "nodes": {"n1": {
                       "text": "x",
                       "choices": [{"label": "set", "effects": [
                           {"type": "flag", "key": "flag_evil", "value": True},
                           {"type": "flag", "key": "flag_good", "value": True},
                       ]}]}}}],
                   config_extra={"arcs": [{
                       "id": "arc1", "title": "Arc Satu", "teaser": "t",
                       "final_quest": "q_final", "memories_total": 0,
                       "branches": {"flag_baik": "Jalan Baik"},
                       "endings": [
                           {"id": "end_evil", "title": "Jahat", "desc": "d",
                            "condition": {"flag": {"key": "flag_evil"}}},
                           {"id": "end_good", "title": "Baik", "desc": "d",
                            "condition": {"flag": {"key": "flag_good"}}},
                       ]}]})
    assert s.view()["arc_summary"] is None
    s.state.flags["flag_good"] = True
    s.apply_action({"type": "choose", "option": "a"})
    v = s.view()
    assert v["arc_summary"] is not None
    assert v["arc_summary"]["completed"] is True
    assert v["arc_summary"]["title"] == "Arc Satu"
    assert v["arc_summary"]["ending"]["id"] == "end_good"
    assert v["arc_summary"]["branch"] == "Tidak Diketahui"  # flag_baik tidak diset
    s.state.flags["flag_baik"] = True
    assert s.view()["arc_summary"]["branch"] == "Jalan Baik"


def test_arc_summary_branch_enum_string_value(tmp_path):
    """H3: branches dengan nilai flag string (enum) → branch = nilai humanized
    (docs 13: state_identity_stance, state_final_principle, dst)."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q_final", "kind": "main", "title": "Final",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   config_extra={"arcs": [{
                       "id": "arc1", "title": "Arc Satu", "teaser": "t",
                       "final_quest": "q_final", "memories_total": 0,
                       "branches": {"state_stance": "Sikap"}}]})
    s.state.flags["state_stance"] = "seek_truth"
    s.apply_action({"type": "choose", "option": "a"})
    assert s.view()["arc_summary"]["branch"] == "Seek Truth"


def test_arc_summary_branch_state_pavilion_academy(tmp_path):
    """H3/docs 13: `state_pavilion` = akademi pemain (player.academy) — branch
    arc_summary menampilkan nama paviliun yang dipilih, bukan flag biasa."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q_final", "kind": "main", "title": "Final",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   config_extra={
                       "academies": [{"id": "pav_x", "name": "Pavilion X (Hati X)"}],
                       "arcs": [{
                           "id": "arc1", "title": "Arc Satu", "teaser": "t",
                           "final_quest": "q_final", "memories_total": 0,
                           "branches": {"state_pavilion": "Paviliun"}}]})
    s.state.player.academy = "pav_x"
    s.apply_action({"type": "choose", "option": "a"})
    assert s.view()["arc_summary"]["branch"] == "Pavilion X (Hati X)"


def test_arc_summary_ending_none_without_condition_match(tmp_path):
    """H1: kondisi ending tidak cocok → ending None (bukan crash / salah pilih)."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q_final", "kind": "main", "title": "Final",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   dialogs=[{"id": "dlg_dummy_flags", "start": "n1", "nodes": {"n1": {
                       "text": "x",
                       "choices": [{"label": "set", "effects": [
                           {"type": "flag", "key": "flag_never", "value": True},
                       ]}]}}}],
                   config_extra={"arcs": [{
                       "id": "arc1", "title": "Arc Satu", "teaser": "t",
                       "final_quest": "q_final", "memories_total": 0,
                       "endings": [{"id": "end_x", "title": "X", "desc": "d",
                                     "condition": {"flag": {"key": "flag_never"}}}]}]})
    s.apply_action({"type": "choose", "option": "a"})
    assert s.view()["arc_summary"]["ending"] is None


def test_faction_condition_gates_dialog_choice(tmp_path):
    """D2 (docs 05): kondisi faction_min di opsi dialog menyembunyikan opsi
    saat reputasi rendah, menampilkan saat cukup. Fitur ambang faksi dikunci."""
    dlg = {"id": "dlg_f", "npc": "n1", "start": "n0", "nodes": {"n0": {
        "speaker": "npc:n1", "text": "hi",
        "choices": [
            {"label": "Rahasia", "next": "n0",
             "condition": {"faction_min": {"faksi": "faction_orth", "value": 3}}},
            {"label": "Biasa", "next": "n0"},
        ]}}}
    npcs = [{"id": "n1", "name": "N", "location": "l_start",
             "dialog_routes": {"general": "dlg_f"}}]
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q1", "kind": "main", "title": "T",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   npcs=npcs, dialogs=[dlg],
                   factions=[{"id": "faction_orth", "name": "Ortodoks"}])
    s.state.factions["faction_orth"] = 2  # di bawah ambang
    s.apply_action({"type": "talk", "npc": "n1"})
    v = s.view()
    labels = [c["label"] for c in v["dialog"]["choices"]]
    assert "Rahasia" not in labels and "Biasa" in labels
    s.state.factions["faction_orth"] = 3  # cukup
    s.apply_action({"type": "dialog_choice", "choice_index": 0})  # re-open? no-op
    s.state.pending_dialog = None
    s.apply_action({"type": "talk", "npc": "n1"})
    labels = [c["label"] for c in s.view()["dialog"]["choices"]]
    assert "Rahasia" in labels


def test_memory_unlock_via_quest_completion(tmp_path):
    """E3 (docs 06): quest on_complete.memory_unlock membuka ingatan + memakai
    reliability dari data memory (bukan default yang menimpa)."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q1", "kind": "main", "title": "T",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]},
                            "on_complete": {"memory_unlock": "mem_1"}}],
                   memories=[{"id": "mem_1", "title": "M", "text": "T",
                              "reliability": "TINGGI"}])
    s.apply_action({"type": "choose", "option": "a"})
    assert [m["id"] for m in s.state.memories] == ["mem_1"]
    assert s.state.memories[0]["reliability"] == "TINGGI"


def test_side_quest_relation_gate_offer(tmp_path):
    """B5 (docs 04): side quest dengan available_from.relation_min hanya
    ditawarkan bila relation >= ambang."""
    npcs = [{"id": "n1", "name": "N", "location": "l_start"}]
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q1", "kind": "main", "title": "T",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}},
                           {"id": "q_side", "kind": "side", "title": "S",
                            "objective": {"kind": "talk", "npc": "n1"},
                            "available_from": {"day": 1, "hour": 0,
                                                "relation_min": {"npc": "n1", "value": 5}}}],
                   npcs=npcs)
    assert s.quest.is_offerable("q_side") is False
    s.state.relations["n1"] = 5
    assert s.quest.is_offerable("q_side") is True
    assert s.quest.start_side("q_side") is True


def test_location_ambience_in_view(tmp_path):
    """G1 (docs 08): ambience lokasi data-driven diteruskan ke view (atmosfer
    visual web); default aman bila kolom hilang."""
    locs = [{"id": "l_start", "name": "Start", "is_safe": True,
             "connections": ["l2"], "ambience": "forest"},
            {"id": "l2", "name": "L2", "is_safe": False, "connections": ["l_start"]}]
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q1", "kind": "main", "title": "T",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   locations=locs)
    assert s.view()["location"]["ambience"] == "forest"
    s.apply_action({"type": "move", "to": "l2"})
    assert s.view()["location"]["ambience"] == "academy"  # default aman


def test_companion_fights_in_battle(tmp_path):
    """C5 (docs 04): kompanion aktif ikut bertarung tiap giliran — damage
    kompanion berkurang dari HP musuh."""
    reg, s = _sess(tmp_path,
                   quests=[{"id": "q1", "kind": "main", "title": "T",
                            "objective": {"kind": "choose",
                                           "options": [{"value": "a", "label": "A"}]}}],
                   enemies=[{"id": "e1", "name": "E1", "hp": 100, "attack": 0,
                             "defense": 0, "exp_reward": 1}],
                   companions=[{"id": "c1", "name": "Komp", "base_hp": 20,
                                "base_attack": 7, "base_defense": 2, "base_speed": 5}],
                   config_extra={"world": {"hunts": []}})
    s.state.companion = {"id": "c1", "active": True, "hp": 20}
    s.state.companions = [{"id": "c1", "active": True, "hp": 20}]
    s.state.active_companion = "c1"
    s.battle.start([reg.enemy("e1")], "hunt")
    b = s.state.pending_battle
    foes_before = b["foes"][0]["hp"]
    s.apply_action({"type": "battle_action", "action": "attack"})
    b = s.state.pending_battle
    assert b["foes"][0]["hp"] < foes_before  # damage dari pemain ATAU kompanion
    assert "Komp" in "\n".join(e["text"] for e in s.state.log)


def test_search_failure_adds_nothing(tmp_path, monkeypatch):
    """Search gagal (random ≥ 0.6): item tidak bertambah."""
    import src.engine.session as sess_mod
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[],
                   items=[{"id": "i1", "name": "I1", "type": "consumable", "hp_restore": 1}],
                   config_extra={"world": {"hunts": [{"id": "h1", "location": "l_start", "pool": ["e1"],
                                                      "search_item": "i1"}]}})
    monkeypatch.setattr(sess_mod.random, "random", lambda: 0.9)
    s.apply_action({"type": "search"})
    assert "i1" not in s.state.inventory


def test_learn_technique_fallback_without_location_field(registry):
    """Belajar teknik: akademi tanpa field 'location' (data lama/fixture) →
    sah di titik aman mana pun; ditolak di lokasi tak aman."""
    s = GameSession.new(registry)
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    s.state.player.academy = "akademi_bambu"
    s.state.location = "loc_gerbang"  # is_safe — fallback lolos meski bukan paviliun
    s.apply_action({"type": "learn_technique", "technique": "teknik_dasar"})
    assert "teknik_dasar" in s.state.player.techniques

    s2 = GameSession.new(registry)
    while s2.state.pending_dialog:
        s2.apply_action({"type": "dialog_choice", "choice_index": -1})
    s2.state.player.academy = "akademi_bambu"
    s2.state.location = "loc_hutan"  # tidak aman → fallback menolak
    v = s2.apply_action({"type": "learn_technique", "technique": "teknik_dasar"})
    assert v.get("error")
    assert "teknik_dasar" not in s2.state.player.techniques


def test_carry_technique_level_caps_at_realm_max(tmp_path):
    """_carry_technique_level: level di-cap di realm max, floor mengangkat.
    Shared helper untuk _unlock_technique dan _fuse_technique — satu
    implementasi, satu sumber kebenaran untuk kalkulasi level teknik."""
    reg, s = _sess(tmp_path, quests=[Q()], npcs=[])
    # realm r1 (default fixture) order=1 → max_lvl = 1+1 = 2
    assert s._carry_technique_level(5) == 2       # cap di atas
    assert s._carry_technique_level(1) == 1       # floor default 1
    assert s._carry_technique_level(0, floor=2) == 2  # floor 2 naik ke 2


def test_foe_status_unknown_kind_logged_not_silent(tmp_path):
    """Fix audit v3 §1.5 (sisi musuh): kind tak dikenal dilaporkan lalu
    dihapus — bukan lenyap senyap seperti 'sembuh'.

    Simulasi: config loaded valid, lalu kind berubah (drift dari
    STATUS_KINDS) — ini skenario real di mana validator tidak jalan."""
    reg, s = _sess(
        tmp_path, quests=[Q()], npcs=[],
        enemies=[{"id": "e1", "name": "E1", "hp": 50, "attack": 0, "defense": 0}],
        config_extra={"battle": {"statuses": {
            "aneh": {"name": "Aneh", "kind": "dot", "duration": 2, "max_duration": 5}}}},
    )
    # Simulasi drift: setelah load, kind diubah jadi tidak valid
    reg.config["battle"]["statuses"]["aneh"]["kind"] = "misteri"
    s.battle.start([dict(reg.enemies["e1"])], "hunt")
    b = s.state.pending_battle
    b["foe_statuses"] = {"aneh": 2}
    foe = b["foes"][0]
    s.battle._apply_foe_statuses(foe, b)
    assert "aneh" not in b["foe_statuses"], "status invalid dihapus"
    assert "tak dikenal" in "\n".join(e["text"] for e in s.state.log), "harus ada log"
