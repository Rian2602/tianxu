"""Test keamanan kondisi dialog — F1.3 (ENGINE_ADAPTATION_PLAN).

Perilaku baru: kunci kondisi TAK DIKENAL → log peringatan sistem + False
(fail-safe, tolak akses) — bukan `True` (perilaku lama: typo = gerbang bocor),
bukan raise. Kombinasi multi-kunci tetap AND; kondisi kosong tetap True.
"""

from __future__ import annotations

import pytest

from src.engine.dialog import CONDITION_KEYS, DialogEngine


def _eval(session, cond):
    return DialogEngine._eval_condition(session.state, cond, session.reg)


# ---------- kunci tak dikenal ----------

def test_unknown_key_returns_false_with_warning(registry, session):
    """Typo `moralty_min` (bukan morality_min) → False + peringatan di log."""
    ok = _eval(session, {"moralty_min": 50})
    assert ok is False
    msgs = [e["text"] for e in session.state.log]
    assert any("moralty_min" in m and "tak dikenal" in m for m in msgs)


def test_unknown_key_with_valid_key_is_false(registry, session):
    """Kunci tak dikenal + kunci valid → tetap False (bukan True karena valid)."""
    session.state.flags["sudah_kenal"] = True
    ok = _eval(session, {"flag": {"key": "sudah_kenal", "value": True}, "moralty_min": 50})
    assert ok is False


def test_multiple_unknown_keys_reported(registry, session):
    ok = _eval(session, {"typo_a": 1, "typo_b": 2})
    assert ok is False
    msgs = "\n".join(e["text"] for e in session.state.log)
    assert "typo_a" in msgs and "typo_b" in msgs


# ---------- perilaku kunci valid tidak berubah ----------

def test_empty_condition_is_true(registry, session):
    assert _eval(session, {}) is True


def test_flag_condition(registry, session):
    session.state.flags["sudah_kenal"] = True
    assert _eval(session, {"flag": {"key": "sudah_kenal", "value": True}}) is True
    assert _eval(session, {"flag": {"key": "belum", "value": True}}) is False


def test_multiple_conditions_and(registry, session):
    """Kombinasi multi-kunci = AND — semua harus benar."""
    session.state.player.morality = 60
    session.state.inventory["pil_qi"] = 3
    cond = {"morality_min": 50, "has_item": "pil_qi"}
    assert _eval(session, cond) is True
    # satu gagal → keseluruhan False
    cond2 = {"morality_min": 70, "has_item": "pil_qi"}
    assert _eval(session, cond2) is False


def test_has_items_nested_dict(registry, session):
    """has_items: {item, value} — nested, bukan kunci top-level (tidak dianggap typo)."""
    session.state.inventory["pil_qi"] = 3
    assert _eval(session, {"has_items": {"item": "pil_qi", "value": 2}}) is True
    assert _eval(session, {"has_items": {"item": "pil_qi", "value": 5}}) is False


def test_relation_condition(registry, session):
    session.state.relations["npc_guru"] = 10
    assert _eval(session, {"relation_min": {"npc": "npc_guru", "value": 10}}) is True
    assert _eval(session, {"relation_min": {"npc": "npc_guru", "value": 11}}) is False


def test_memory_condition(registry, session):
    session.state.memories.append("mem_1")
    assert _eval(session, {"memory": "mem_1"}) is True
    assert _eval(session, {"memory": "mem_2"}) is False


def test_realm_min_condition(registry, session):
    # pemain di realm_awal (order 1); butuh realm_awal → True; butuh lebih tinggi → False
    assert _eval(session, {"realm_min": "realm_awal"}) is True


def test_quest_active_condition(registry, session):
    assert _eval(session, {"quest_active": "q_min_intro"}) is True
    assert _eval(session, {"quest_active": "q_ghost"}) is False


# ---------- integrasi: dialog dengan choice ber-kondisi ----------

def test_dialog_choice_condition_hides_option(registry, session):
    """Baseline dataset: choice ber-condition flag belum diset → tidak tampil."""
    session.dialog.start("dlg_side_offer")
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert "Terima tugas" in labels          # tanpa condition → tampil
    assert not any("Tolak" in l for l in labels)  # condition flag false → tersembunyi


def test_dialog_choice_condition_shows_after_flag(registry, session):
    """Set flag → choice ber-kondisi muncul (jalur valid runtime)."""
    session.state.flags["sudah_kenal"] = True
    session.dialog.start("dlg_side_offer")
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert any("Tolak" in l for l in labels)


def test_condition_keys_exposed_for_validator(registry):
    """CONDITION_KEYS harus 19 kunci — satu sumber kebenaran F1.1 & F1.3 + faction
    + flags (multi-flag AND) + flag_not (negasi) — docs 11 Hidden Resolution."""
    assert CONDITION_KEYS == {
        "flag", "flags", "flag_not", "morality_min", "morality_max", "has_item",
        "has_items", "defeated_min", "realm_min", "academy", "quest_active",
        "quest_not_active", "month_min", "month_max", "relation_min",
        "relation_max", "memory", "faction_min", "faction_max",
    }
