"""Test efek engine — dispatch efek morality, relation, reputation, flag, item, gold, start_quest, dan error handling."""

from __future__ import annotations

from src.engine.effects import apply
from src.engine.events import add_log, log_delta
from src.engine.memory import unlock


def test_apply_none_and_empty(dummy_session, registry):
    state = dummy_session.state
    # None dan list kosong adalah no-op: tidak error, tidak menulis log error
    apply(state, registry, None)
    apply(state, registry, [])
    assert not any("Efek tak dikenal" in e["text"] for e in state.log)


def test_apply_morality(dummy_session, registry):
    state = dummy_session.state
    state.player.morality = 0
    apply(state, registry, [{"type": "morality", "value": 25}])
    assert state.player.morality == 25
    apply(state, registry, [{"type": "morality", "value": -40}])
    assert state.player.morality == -15


def test_apply_relation(dummy_session, registry):
    state = dummy_session.state
    state.relations.clear()
    # dengan NPC
    apply(state, registry, [{"type": "relation", "npc": "npc_suqing", "value": 10}])
    assert state.relations["npc_suqing"] == 10
    apply(state, registry, [{"type": "relation", "npc": "npc_suqing", "value": -5}])
    assert state.relations["npc_suqing"] == 5

    # tanpa NPC (diabaikan secara aman)
    apply(state, registry, [{"type": "relation", "value": 10}])
    assert len(state.relations) == 1


def test_apply_reputation(dummy_session, registry):
    state = dummy_session.state
    # dengan faksi
    apply(state, registry, [{"type": "reputation", "faksi": "changfeng", "value": 15}])
    assert state.flags["rep_changfeng"] == 15

    # tanpa faksi (default "?")
    apply(state, registry, [{"type": "reputation", "value": 5}])
    assert state.flags["rep_?"] == 5


def test_apply_flag(dummy_session, registry):
    state = dummy_session.state
    # flag dengan value eksplisit
    apply(state, registry, [{"type": "flag", "key": "met_elder", "value": True}])
    assert state.flags["met_elder"] is True

    # flag dengan default value (True)
    apply(state, registry, [{"type": "flag", "key": "visited_cave"}])
    assert state.flags["visited_cave"] is True

    # flag dengan custom value
    apply(state, registry, [{"type": "flag", "key": "custom_counter", "value": 42}])
    assert state.flags["custom_counter"] == 42


def test_apply_item(dummy_session, registry):
    state = dummy_session.state
    state.inventory.clear()

    # Tambah item dengan jumlah default (1)
    apply(state, registry, [{"type": "item", "id": "pil_qi"}])
    assert state.inventory["pil_qi"] == 1

    # Tambah item dengan jumlah eksplisit (3)
    apply(state, registry, [{"type": "item", "id": "pil_qi", "count": 3}])
    assert state.inventory["pil_qi"] == 4

    # Kurangi item (masih > 0)
    apply(state, registry, [{"type": "item", "id": "pil_qi", "count": -2}])
    assert state.inventory["pil_qi"] == 2

    # Kurangi item hingga <= 0 (dihapus dari dict)
    apply(state, registry, [{"type": "item", "id": "pil_qi", "count": -5}])
    assert "pil_qi" not in state.inventory

    # Item tanpa id (diabaikan secara aman)
    apply(state, registry, [{"type": "item", "count": 2}])


def test_apply_gold(dummy_session, registry):
    state = dummy_session.state
    state.player.gold = 50

    # Tambah gold
    apply(state, registry, [{"type": "gold", "value": 30}])
    assert state.player.gold == 80

    # Kurang gold (masih positif)
    apply(state, registry, [{"type": "gold", "value": -30}])
    assert state.player.gold == 50

    # Kurang gold melebihi saldo (clamp ke 0)
    apply(state, registry, [{"type": "gold", "value": -100}])
    assert state.player.gold == 0


def test_apply_start_quest(dummy_session, registry):
    state = dummy_session.state
    # start_quest adalah no-op di effects.py (ditangani dialog/session)
    apply(state, registry, [{"type": "start_quest", "quest": "q_side_suqing"}])
    assert "q_side_suqing" not in state.active_side_quests
    assert state.current_quest == "q_akademi_01"  # tidak berubah
    assert not any("Efek tak dikenal" in e["text"] for e in state.log)


def test_apply_unknown_type(dummy_session, registry):
    state = dummy_session.state
    apply(state, registry, [{"type": "efek_gaib_tidak_dikenal"}])
    assert any("Efek tak dikenal" in e["text"] for e in state.log)


def test_add_log_invalid_type_falls_back_to_narration(dummy_session):
    state = dummy_session.state
    add_log(state, "bukan_tipe_valid", "teks aneh")
    entry = state.log[-1]
    assert entry["type"] == "narration"
    assert entry["text"] == "teks aneh"


def test_log_delta_returns_entries_from_index(dummy_session):
    state = dummy_session.state
    before = len(state.log)
    add_log(state, "system", "pertama")
    add_log(state, "npc", "kedua")
    delta = log_delta(state, before)
    assert [e["text"] for e in delta] == ["pertama", "kedua"]


def test_unlock_skips_already_unlocked(dummy_session, registry):
    state = dummy_session.state
    unlock(state, registry, "mem_01")
    unlock(state, registry, "mem_01")
    assert state.memories.count("mem_01") == 1


def test_unlock_ignores_unknown_id(dummy_session, registry):
    state = dummy_session.state
    unlock(state, registry, "mem_999")
    assert state.memories == []
    assert any("Ingatan baru terbuka" in e["text"] for e in state.log) is False
