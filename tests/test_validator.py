"""Test validator data — tiap aturan §14 menolak data yang sengaja dirusak.

Data "bagus" minimal di-_good() harus lolos semua aturan; tiap test mengorup
satu bagian agar error yang muncul persis menunjuk aturan yang diuji.
"""

from __future__ import annotations

import json

import pytest

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


# ---------- aturan 1: JSON/CSV well-formed ----------

def test_aturan1_json_rusak():
    v = Validator()

    def bad_read_json(rel: str):
        try:
            raise json.JSONDecodeError("rusak", "doc", 0)
        except json.JSONDecodeError as e:
            v.error(f"{rel}: JSON rusak — {e}")
        return None

    v.read_json = bad_read_json
    v.read_csv_rows = lambda rel: []
    ok = v.validate()
    assert not ok
    assert any("JSON rusak" in e for e in v.errors)


# ---------- aturan 2: referensi valid ----------

def test_aturan2_referensi_npc_tidak_ada():
    d = _good()
    d["quests/quests_akademi.json"] = {"quests": [
        {"id": "q1", "kind": "main", "objective": {"kind": "talk", "npc": "npc_hantu"}, "next": []},
    ]}
    v, ok = make(d)
    assert not ok
    assert any("objective.npc" in e for e in v.errors)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
