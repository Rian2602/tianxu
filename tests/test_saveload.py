"""Test serialization GameState and save/load path traversal security."""

from __future__ import annotations

import json
import pytest

from src.engine.session import GameSession, SaveError
from src.engine.state import GameState, PlayerState


def test_gamestate_to_dict_from_dict_roundtrip(dummy_session):
    state = dummy_session.state
    # Modify state fields with non-default data
    state.player.hp = 75
    state.player.qi = 30
    state.player.realm = "realm_qi_refining"
    state.player.realm_level = 3
    state.player.gold = 250
    state.player.roots = "akar_top"
    state.player.academy = "akademi_elemen"
    state.player.equipment = {"weapon": "pedang_bambu"}
    state.player.exp = 120
    state.player.morality = 15

    state.location = "loc_asrama"
    state.day = 5
    state.hour = 14
    state.current_quest = "q_akademi_02"
    state.completed_quests = ["q_akademi_01"]
    state.active_side_quests = {"q_side_suqing": {"step": 1}}
    state.inventory = {"pil_qi": 5, "material_herba": 2}
    state.flags = {"met_penjaga": True, "jalur_3b": False}
    state.relations = {"npc_suqing": 10}
    state.memories = ["mem_01"]
    state.last_safe_location = "loc_asrama"
    state.grounding_hours_today = 4
    state.branch_pending = None
    state.pending_dialog = None
    state.pending_battle = {"active": True, "turn": 2}
    state.companion = {"id": "comp_kucing", "hp": 50, "active": True}

    # Serialize
    d = state.to_dict()

    # Ensure JSON serializable
    json_str = json.dumps(d)
    assert isinstance(json_str, str)

    # Reconstitute
    restored = GameState.from_dict(d)

    # Verify identical dict representation
    assert restored.to_dict() == state.to_dict()

    # Independence check: mutating restored shouldn't affect original
    restored.inventory["pil_qi"] = 999
    assert state.inventory["pil_qi"] == 5

    restored.player.equipment["weapon"] = "pedang_kayu"
    assert state.player.equipment["weapon"] == "pedang_bambu"


def test_save_load_path_format(dummy_session, tmp_path, monkeypatch, registry):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)

    # Move to safe location to allow saving
    dummy_session.state.location = "loc_asrama"
    res = dummy_session.apply_action({"type": "save", "save_name": "slot_test"})

    assert res.get("error") is None
    expected_file = tmp_path / "slot_test.json"
    assert expected_file.exists()

    with open(expected_file, encoding="utf-8") as f:
        file_data = json.load(f)
    assert file_data == dummy_session.state.to_dict()

    # Load back
    loaded_session = GameSession.load(registry, "slot_test")
    assert loaded_session.state.to_dict() == dummy_session.state.to_dict()


def test_save_path_traversal_rejected(dummy_session, tmp_path, monkeypatch):
    from src.engine import session as session_mod

    saves_dir = tmp_path / "saves"
    saves_dir.mkdir()
    monkeypatch.setattr(session_mod, "SAVES_DIR", saves_dir)

    dummy_session.state.location = "loc_asrama"

    # Attempt path traversal save
    res = dummy_session.apply_action({"type": "save", "save_name": "../secret"})

    assert res.get("error") is not None
    assert not (tmp_path / "secret.json").exists()


def test_load_path_traversal_rejected(tmp_path, monkeypatch, registry):
    from src.engine import session as session_mod

    saves_dir = tmp_path / "saves"
    saves_dir.mkdir()
    monkeypatch.setattr(session_mod, "SAVES_DIR", saves_dir)

    # Create secret file outside saves_dir with valid state content
    secret_file = tmp_path / "secret.json"
    valid_state_dict = GameSession.new(registry).state.to_dict()
    secret_file.write_text(json.dumps(valid_state_dict), encoding="utf-8")

    with pytest.raises(SaveError, match="nama save tidak valid"):
        GameSession.load(registry, "../secret")


def test_save_null_byte_rejected(dummy_session):
    dummy_session.state.location = "loc_asrama"
    res = dummy_session.apply_action({"type": "save", "save_name": "test\x00slot"})
    assert res.get("error") is not None


