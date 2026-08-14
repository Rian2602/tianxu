"""Test validator data — tiap aturan §14 menolak data yang sengaja dirusak.

Data "bagus" minimal di-_good() harus lolos semua aturan; tiap test mengorup
satu bagian agar error yang muncul persis menunjuk aturan yang diuji.
"""

from __future__ import annotations

import shutil

import tools.validate_data as vd

from tools.validate_data import Validator


def _good() -> dict:
    """Dataset minimal yang lolos seluruh 16 aturan §14."""
    q = {"id": "q1", "kind": "main", "objective": {"kind": "reach"}, "next": []}
    cfg = {
        "starting": {"current_quest": "q1"},
        "roots": {"tiers": [{"id": "t", "exp_multiplier": 1.0}], "default": "t"},
        "battle": {"crit_chance": 0.1, "turn_order": "fixed_alternate", "damage_formula": "percent"},
        "academies": [],
        "element_advantage": {},
        "arcs": [{"id": "arc1", "final_quest": "q1", "title": "T", "teaser": "t",
                   "memories_total": 1, "branches": {"b1": "B"}}],
    }
    return {
        "config.json": cfg,
        "quests/quests_akademi.json": {"quests": [q]},
        "quests/quests_side.json": {"quests": []},
        "dialogs/dialogs_akademi.json": {"dialogs": []},
        "npcs.json": {"npcs": []},
        "locations.json": {"locations": []},
        "memories.json": {"memories": []},
        "recipes.json": {"recipes": []},
        "companions.json": {"companions": []},
        "items.csv": [], "enemies.csv": [], "realms.csv": [], "techniques.csv": [],
    }


def make(data: dict) -> tuple[Validator, bool]:
    v = Validator()
    v.read_json = lambda rel: data.get(rel, {})
    v.read_csv_rows = lambda rel: data.get(rel, [])
    return v, v.validate()


def test_data_baik_lolos():
    v, ok = make(_good())
    assert ok, v.errors


def test_aturan14_ambience_harus_enum_terdaftar():
    """C4: field `ambience` lokasi (opsional) harus ∈ enum `world.ambiences`."""
    good = _good()
    good["config.json"]["world"] = {"ambiences": {"academy": "Kampus", "forest": "Hutan"}}
    good["locations.json"] = {"locations": [
        {"id": "l1", "name": "L1", "is_safe": True, "connections": [], "ambience": "academy"},
    ]}
    v, ok = make(good)
    assert ok, v.errors
    # ambience tak dikenal → ditolak
    good["locations.json"] = {"locations": [
        {"id": "l1", "name": "L1", "is_safe": True, "connections": [], "ambience": "gunung_salju"},
    ]}
    v, ok = make(good)
    assert not ok
    assert any("ambience" in e for e in v.errors)


def test_aturan4_talk_node_wajib_harus_ada_di_dialog():
    """A3: objective talk `node`/`start_node`/`nodes` harus ada di dialog default NPC."""
    good = _good()
    good["npcs.json"] = {"npcs": [{"id": "n1", "default_dialog": "dlg1"}]}
    good["dialogs/dialogs_akademi.json"] = {"dialogs": [{"id": "dlg1", "start": "node_a", "nodes": {"node_a": {}}}]}
    # valid: node & start_node ada di dialog
    good["quests/quests_akademi.json"] = {"quests": [{
        "id": "q1", "kind": "main", "next": [],
        "objective": {"kind": "talk", "npc": "n1", "node": "node_a", "start_node": "node_a"},
    }]}
    v, ok = make(good)
    assert ok, v.errors
    # invalid: node tidak ada di dialog
    good["quests/quests_akademi.json"] = {"quests": [{
        "id": "q1", "kind": "main", "next": [],
        "objective": {"kind": "talk", "npc": "n1", "node": "node_tidak_ada"},
    }]}
    v, ok = make(good)
    assert not ok
    assert any("node_tidak_ada" in e for e in v.errors)
    # invalid: start_node tidak ada di dialog
    good["quests/quests_akademi.json"] = {"quests": [{
        "id": "q1", "kind": "main", "next": [],
        "objective": {"kind": "talk", "npc": "n1", "start_node": "node_tidak_ada"},
    }]}
    v, ok = make(good)
    assert not ok
    assert any("node_tidak_ada" in e for e in v.errors)


# ---------- aturan 1: JSON/CSV well-formed ----------

def test_aturan1_json_rusak(tmp_path, monkeypatch):
    # salin data nyata → jalur parsing asli (read_json) yang benar-benar diuji
    clean = tmp_path / "data"
    shutil.copytree(vd.ROOT / "data", clean)
    monkeypatch.setattr(vd, "DATA", clean)

    assert vd.Validator().validate()  # sanity: data bersih lolos

    broken = clean / "npcs.json"
    broken.write_text('{"npcs": [', encoding="utf-8")
    v = vd.Validator()
    assert not v.validate()
    assert any("npcs.json" in e and "JSON rusak" in e for e in v.errors)


# ---------- aturan 2: referensi valid ----------

def test_aturan2_referensi_npc_tidak_ada():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "talk", "npc": "npc_hantu"}, "next": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("objective.npc" in e for e in v.errors)


# ---------- aturan 7: config.world.hunt referensi valid (A2) ----------

def test_aturan7_world_hunt_referensi_tidak_ada():
    d = _good()
    d["config.json"]["world"] = {
        "hunt": {"pool": ["eno_hantu"], "mini_boss": "eno_hantu2", "location": "loc_hantu",
                 "search_item": "item_hantu", "mini_boss_chance": 0.5}
    }
    v, ok = make(d)
    assert not ok
    assert any("world.hunt.pool" in e for e in v.errors)
    assert any("world.hunt.mini_boss" in e for e in v.errors)
    assert any("world.hunt.location" in e for e in v.errors)
    assert any("world.hunt.search_item" in e for e in v.errors)


def test_aturan7_world_hunt_chance_invalid():
    d = _good()
    d["config.json"]["world"] = {"hunt": {"pool": [], "mini_boss_chance": 2.0}}
    v, ok = make(d)
    assert not ok
    assert any("mini_boss_chance" in e for e in v.errors)


def test_aturan7_night_pool_referensi_tidak_ada():
    d = _good()
    d["config.json"]["world"] = {"hunt": {"pool": [], "night_pool": ["eno_hantu_malam"]}}
    v, ok = make(d)
    assert not ok
    assert any("night_pool" in e for e in v.errors)


def test_aturan2_report_to_npc_tidak_ada():
    """A2: objective.report_to harus merujuk npc yang ada (aturan 2)."""
    d = _good()
    d["quests/quests_side.json"] = {"quests": [{
        "id": "sq_report", "kind": "side", "repeatable": True, "cooldown": 2,
        "available_from": {"day": 1, "hour": 8},
        "objective": {"kind": "defeat", "enemies": [], "target": 1, "report_to": "npc_tidak_ada"},
        "next": [], "on_complete": {"rewards": {"exp": 1}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("report_to" in e for e in v.errors)


def test_aturan7_arcs_final_quest_tidak_ada():
    """B1: config.arcs — final_quest harus merujuk quest yang ada (aturan 7)."""
    d = _good()
    d["config.json"]["arcs"] = [{
        "id": "sekte", "final_quest": "q_tidak_ada", "title": "ARC",
        "teaser": "t", "memories_total": 4, "branches": {"b": "B"},
    }]
    v, ok = make(d)
    assert not ok
    assert any("final_quest" in e for e in v.errors)


def test_aturan7_arcs_memories_total_tidak_valid():
    """B1: config.arcs — memories_total harus int > 0 (aturan 7)."""
    d = _good()
    d["config.json"]["arcs"] = [{
        "id": "akademi", "final_quest": "q1", "title": "ARC",
        "teaser": "t", "memories_total": 0, "branches": {"b": "B"},
    }]
    v, ok = make(d)
    assert not ok
    assert any("memories_total" in e for e in v.errors)


def test_aturan7_safe_fallback_location_bukan_aman():
    """B2: config.world.safe_fallback_location harus lokasi yang ada dan is_safe (aturan 7)."""
    d = _good()
    d["config.json"]["world"] = {"safe_fallback_location": "loc_tidak_ada"}
    v, ok = make(d)
    assert not ok
    assert any("safe_fallback_location" in e for e in v.errors)


def test_aturan13_efek_technique_tidak_dikenal():
    """C1: efek technique harus merujuk teknik yang ada di techniques.csv (aturan 13)."""
    d = _good()
    d["techniques.csv"] = [{"id": "t1", "academy": "elemen", "kind": "attack"}]
    d["quests/quests_akademi.json"] = {"quests": [{
        "id": "q1", "kind": "main",
        "objective": {"kind": "reach"},
        "next": [],
        "on_complete": {"effects": [{"type": "technique", "id": "tek_tidak_ada"}]},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("technique" in e for e in v.errors)


def test_aturan7_teknik_upgrade_config_tidak_valid():
    """C1: config.cultivation.technique_upgrade_cost_base harus > 0 (aturan 7)."""
    d = _good()
    d["config.json"]["cultivation"] = {"technique_upgrade_cost_base": 0}
    v, ok = make(d)
    assert not ok
    assert any("technique_upgrade_cost_base" in e for e in v.errors)


def test_aturan7_month_length_dan_month_names_tidak_valid():
    """C2: config.time.month_length_days ≤ 0 / month_names ≠ 12 ditolak (aturan 7)."""
    d = _good()
    d["config.json"]["time"] = {"month_length_days": 0}
    v, ok = make(d)
    assert not ok
    assert any("month_length_days" in e for e in v.errors)

    d = _good()
    d["config.json"]["time"] = {"month_length_days": 30, "month_names": ["Satu", "Dua"]}
    v, ok = make(d)
    assert not ok
    assert any("month_names" in e for e in v.errors)


def test_aturan7_kondisi_month_dialog_tidak_valid():
    """C2: kondisi dialog month_min/max di luar 1..12 ditolak (aturan 7)."""
    d = _good()
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_m", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x",
                         "condition": {"month_max": 13}, "end": True}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("month_max" in e for e in v.errors)

    # bulan valid (1..12) diterima
    d = _good()
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_m", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x",
                         "condition": {"month_min": 3, "month_max": 5}, "end": True}},
    }]}
    v, ok = make(d)
    assert ok


def test_aturan7_ending_arc_tidak_valid():
    """C3: config.arcs[].endings — ending tanpa title / condition kunci tak dikenal ditolak (aturan 7)."""
    d = _good()
    d["config.json"]["arcs"][0]["endings"] = [{"id": "e1", "desc": "d", "condition": {}}]
    v, ok = make(d)
    assert not ok
    assert any("title" in e for e in v.errors)

    d = _good()
    d["config.json"]["arcs"][0]["endings"] = [{
        "id": "e1", "title": "T", "desc": "d",
        "condition": {"mood_min": 10},  # kunci kondisi tak dikenal
    }]
    v, ok = make(d)
    assert not ok
    assert any("mood_min" in e for e in v.errors)

    # ending valid (kondisi moralitas + flag, pola kondisi dialog) diterima
    d = _good()
    d["config.json"]["arcs"][0]["endings"] = [{
        "id": "e1", "title": "T", "desc": "d",
        "condition": {"morality_min": 30, "flag": {"key": "kunci_x", "value": True}},
    }]
    v, ok = make(d)
    assert ok


def test_aturan13_unlock_arc_tidak_dikenal():
    """B4: techniques.csv unlock_arc harus merujuk config.arcs[].id (aturan 13)."""
    d = _good()
    d["config.json"]["arcs"] = [{
        "id": "akademi", "final_quest": "q1", "title": "ARC",
        "teaser": "t", "memories_total": 4, "branches": {"b": "B"},
    }]
    d["techniques.csv"] = [{"id": "t1", "academy": "elemen", "kind": "attack", "unlock_arc": "arc_tidak_ada"}]
    v, ok = make(d)
    assert not ok
    assert any("unlock_arc" in e for e in v.errors)


def test_aturan14_wajib_minimal_satu_lokasi_aman():
    """B2-fix: lokasi harus punya minimal 1 is_safe: true (respawn KO butuh titik aman)."""
    d = _good()
    d["locations.json"] = {"locations": [
        {"id": "loc_x", "name": "X", "description": "", "is_safe": False, "connections": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("is_safe" in e and "minimal" in e for e in v.errors)


def test_aturan7_night_window_tidak_valid():
    d = _good()
    d["config.json"]["world"] = {"hunt": {"pool": [], "night_window": {"hour_start": 30, "hour_end": 6}}}
    v, ok = make(d)
    assert not ok
    assert any("night_window.hour_start" in e for e in v.errors)


# ---------- aturan 3: graf quest acyclic ----------

def test_aturan3_siklus_dag():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "reach"}, "next": [{"quest": "q2"}]},
        {"id": "q2", "kind": "main", "objective": {"kind": "reach"}, "next": [{"quest": "q1"}]},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("siklus" in e for e in v.errors)


# ---------- aturan 4: >1 sisi wajib choice_id ----------

def test_aturan4_sisi_banyak_tanpa_choice_id():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "reach"},
         "next": [{"quest": "q2"}, {"quest": "q3"}]},
        {"id": "q2", "kind": "main", "objective": {"kind": "reach"}, "next": []},
        {"id": "q3", "kind": "main", "objective": {"kind": "reach"}, "next": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("tanpa choice_id" in e for e in v.errors)


# ---------- aturan 5 & 10: konflik NPC/lokasi antar quest ----------

def test_aturan5_10_konflik_npc_side_vs_main():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "talk", "npc": "npc_x"}, "next": []},
    ]}
    d["quests/quests_side.json"] = {"quests": [
        {"id": "qs", "kind": "side", "objective": {"kind": "talk", "npc": "npc_x"},
         "next": [], "available_from": {"day": 1, "hour": 8}, "repeatable": True},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("menuntut" in e for e in v.errors)


# ---------- aturan 6: ID unik ----------

def test_aturan6_duplikat_id():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "reach"}, "next": []},
        {"id": "q1", "kind": "main", "objective": {"kind": "reach"}, "next": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("duplikat id" in e for e in v.errors)


# ---------- aturan 7: config valid ----------

def test_aturan7_current_quest_tidak_ada():
    d = _good()
    d["config.json"]["starting"]["current_quest"] = "q_hantu"
    v, ok = make(d)
    assert not ok
    assert any("current_quest" in e for e in v.errors)


def test_aturan7_element_advantage_tidak_valid():
    d = _good()
    d["config.json"]["element_advantage"] = {"logam": "naga"}
    v, ok = make(d)
    assert not ok
    assert any("element_advantage" in e for e in v.errors)


# ---------- aturan 8: side quest available_from/cooldown konsisten ----------

def test_aturan8_side_tanpa_available_from():
    d = _good()
    d["quests/quests_side.json"] = {"quests": [
        {"id": "qs", "kind": "side", "objective": {"kind": "reach"}, "next": [], "repeatable": True},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("available_from" in e for e in v.errors)


def test_aturan8_cooldown_tidak_valid():
    d = _good()
    d["quests/quests_side.json"] = {"quests": [
        {"id": "qs", "kind": "side", "objective": {"kind": "reach"}, "next": [],
         "available_from": {"day": 1, "hour": 8}, "cooldown": 0},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("cooldown" in e for e in v.errors)


# ---------- aturan 9: repeatable hanya side ----------

def test_aturan9_repeatable_pada_main():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "reach"}, "next": [], "repeatable": True},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("repeatable" in e for e in v.errors)


# ---------- aturan 11: resep alkimia valid ----------

def test_aturan11_resep_hasil_tidak_ada():
    d = _good()
    d["recipes.json"] = {"recipes": [
        {"id": "rc1", "result": "x", "ingredients": [{"item": "y", "count": 1}]},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("hasil" in e for e in v.errors)


# ---------- aturan 12: toko NPC valid ----------

def test_aturan12_shop_item_tidak_ada():
    d = _good()
    d["npcs.json"] = {"npcs": [
        {"id": "n1", "shop": {"buy": [{"item": "x"}]}},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("shop" in e for e in v.errors)


def test_aturan12_spar_require_kondisi_tak_dikenal():
    """spar_require harus format kondisi dialog; kunci tak dikenal ditolak."""
    d = _good()
    d["npcs.json"] = {"npcs": [
        {"id": "n1", "can_spar": True, "spar_require": {"mood_min": 5}},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("spar_require" in e for e in v.errors)


def test_aturan12_spar_require_tanpa_can_spar():
    d = _good()
    d["npcs.json"] = {"npcs": [
        {"id": "n1", "spar_require": {"realm_min": "realm_pembangun_fondasi"}},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("tanpa can_spar" in e for e in v.errors)


def test_aturan12_spar_require_valid():
    d = _good()
    d["npcs.json"] = {"npcs": [
        {"id": "n1", "can_spar": True, "spar_require": {"realm_min": "realm_pembangun_fondasi"}},
    ]}
    v, ok = make(d)
    assert ok


# ---------- aturan 13: weapon punya power; roots valid ----------

def test_aturan13_weapon_tanpa_power():
    d = _good()
    d["items.csv"] = [{"id": "w1", "type": "weapon", "price": "10", "hp_restore": "0", "qi_restore": "0", "power": ""}]
    v, ok = make(d)
    assert not ok
    assert any("tanpa power" in e for e in v.errors)


def test_aturan13_roots_default_tidak_ada():
    d = _good()
    d["config.json"]["roots"]["default"] = "x"
    v, ok = make(d)
    assert not ok
    assert any("default" in e for e in v.errors)


# ---------- aturan 14: lokasi valid ----------

def test_aturan14_is_safe_bukan_bool():
    d = _good()
    d["locations.json"] = {"locations": [
        {"id": "l1", "is_safe": "ya", "connections": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("is_safe harus bool" in e for e in v.errors)


# ---------- aturan 15: kompanion valid ----------

def test_aturan15_kompanion_elemen_tidak_valid():
    d = _good()
    d["companions.json"] = {"companions": [
        {"id": "c1", "element": "naga", "base_hp": 1, "base_attack": 1, "base_defense": 1, "base_speed": 1},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("elemen tidak valid" in e for e in v.errors)


# ---------- aturan 16: config.battle valid ----------

def test_aturan16_crit_chance_di_luar_rentang():
    d = _good()
    d["config.json"]["battle"]["crit_chance"] = 2
    v, ok = make(d)
    assert not ok
    assert any("crit_chance" in e for e in v.errors)


# ---------- validasi efek & kondisi baru (Phase 1.5) ----------

def test_aturan2_efek_relation_npc_tidak_ada():
    """Efek relation harus merujuk NPC yang valid."""
    d = _good()
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_rel", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "choices": [{"label": "A", "effects": [{"type": "relation", "npc": "npc_fiktif", "value": 5}]}]}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("efek relation npc 'npc_fiktif' tidak ada" in e for e in v.errors)


def test_aturan2_efek_relation_value_bukan_angka():
    """Efek relation value harus bertipe angka."""
    d = _good()
    d["npcs.json"] = {"npcs": [{"id": "n1"}]}
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_rel", "npc": "n1", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "choices": [{"label": "A", "effects": [{"type": "relation", "npc": "n1", "value": "lima"}]}]}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("efek relation value harus angka" in e for e in v.errors)


def test_aturan7_kondisi_memory_tidak_ada():
    """Kondisi memory pada dialog harus merujuk ingatan di memories.json."""
    d = _good()
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_mem", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "condition": {"memory": "mem_tidak_ada"}}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("kondisi memory 'mem_tidak_ada' tidak ada" in e for e in v.errors)


def test_aturan7_kondisi_relation_npc_tidak_ada():
    """Kondisi relation_min/relation_max harus merujuk NPC yang terdaftar."""
    d = _good()
    d["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_rel_cond", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "condition": {"relation_min": {"npc": "npc_alien", "value": 10}}}},
    }]}
    v, ok = make(d)
    assert not ok
    assert any("kondisi relation_min npc 'npc_alien' tidak ada" in e for e in v.errors)


def test_aturan2_efek_morality_gold_reputation_validation():
    """Efek morality, gold, dan reputation harus tervalidasi tipe & nilainya."""
    # morality non-numeric value
    d1 = _good()
    d1["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_mor", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "choices": [{"label": "A", "effects": [{"type": "morality", "value": "tinggi"}]}]}},
    }]}
    v1, ok1 = make(d1)
    assert not ok1
    assert any("efek morality value harus angka" in e for e in v1.errors)

    # gold non-numeric value
    d2 = _good()
    d2["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_gld", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "choices": [{"label": "A", "effects": [{"type": "gold", "value": "banyak"}]}]}},
    }]}
    v2, ok2 = make(d2)
    assert not ok2
    assert any("efek gold value harus angka" in e for e in v2.errors)

    # reputation missing faksi
    d3 = _good()
    d3["dialogs/dialogs_akademi.json"] = {"dialogs": [{
        "id": "dlg_rep", "npc": "", "start": "n0",
        "nodes": {"n0": {"speaker": "narration", "text": "x", "end": True,
                         "choices": [{"label": "A", "effects": [{"type": "reputation", "value": 5}]}]}},
    }]}
    v3, ok3 = make(d3)
    assert not ok3
    assert any("efek reputation butuh faksi string" in e for e in v3.errors)

