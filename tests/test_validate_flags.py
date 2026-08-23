"""TDD tests for _validate_flag_consistency in src/validate.py.

[A] flag checked but never set → error
[B] flag checked with value never assigned → error
Clean data → no errors
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.validate import _validate_flag_consistency, _add


def _make_reg(*, quests=None, dialogs=None, config=None, locations=None):
    """Build a minimal DataRegistry-like object for flag-consistency testing."""
    return SimpleNamespace(
        quests=quests or [],
        dialogs=dialogs or [],
        config=config or {},
        locations=locations or [],
    )


class TestFlagA:
    """[A] flag checked but never set → violation."""

    def test_never_set_in_dialog_condition(self, capsys):
        reg = _make_reg(
            dialogs=[{
                "id": "dlg_test",
                "nodes": {
                    "n1": {
                        "text": "hello",
                        "choices": [{
                            "label": "go",
                            "condition": {"flag": {"key": "ghost_flag", "value": True}},
                        }],
                    }
                },
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("ghost_flag" in e and "[A]" in e for e in errors)

    def test_never_set_in_quest_condition(self, capsys):
        reg = _make_reg(
            quests=[{
                "id": "q_test",
                "kind": "main",
                "objective": {"kind": "talk", "npc": "x", "target": 1},
                "condition": {"flag": {"key": "phantom_gate", "value": True}},
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("phantom_gate" in e and "[A]" in e for e in errors)

    def test_never_set_in_ending_condition(self, capsys):
        reg = _make_reg(
            config={"arcs": [{"id": "a1", "endings": [
                {"id": "e1", "title": "Bad",
                 "condition": {"flag": {"key": "never_happened", "value": True}}}
            ]}]},
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("never_happened" in e and "[A]" in e for e in errors)

    def test_never_set_in_connection_gates(self, capsys):
        reg = _make_reg(
            locations=[{
                "id": "loc_x",
                "connections": [],
                "connection_gates": {"loc_y": "gate_flag_xyz"},
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("gate_flag_xyz" in e and "[A]" in e for e in errors)


class TestFlagB:
    """[B] flag checked with value never assigned → violation."""

    def test_value_never_assigned(self, capsys):
        reg = _make_reg(
            dialogs=[{
                "id": "dlg_b",
                "nodes": {
                    "n1": {
                        "text": "x",
                        "choices": [{
                            "label": "A",
                            "condition": {"flag": {"key": "stance", "value": "seek_truth"}},
                        }],
                    }
                },
            }],
            quests=[{
                "id": "q_set",
                "kind": "main",
                "objective": {"kind": "talk", "npc": "x", "target": 1},
                "on_complete": {
                    "effects": [{"type": "flag", "key": "stance", "value": "defend_only"}],
                },
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("stance" in e and "[B]" in e and "seek_truth" in e for e in errors)


class TestFlagBPasses:
    """When the assigned value matches the checked value, no [B] error."""

    def test_value_matches(self, capsys):
        reg = _make_reg(
            dialogs=[{
                "id": "dlg_ok",
                "nodes": {
                    "n1": {
                        "text": "x",
                        "choices": [{
                            "label": "A",
                            "condition": {"flag": {"key": "stance", "value": "seek_truth"}},
                        }],
                    }
                },
            }],
            quests=[{
                "id": "q_set",
                "kind": "main",
                "objective": {"kind": "talk", "npc": "x", "target": 1},
                "on_complete": {
                    "effects": [{"type": "flag", "key": "stance", "value": "seek_truth"}],
                },
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert not any("[B]" in e and "stance" in e for e in errors)


class TestFlagClean:
    """Clean data: no [A] or [B] errors."""

    def test_no_violations(self, capsys):
        reg = _make_reg(
            quests=[{
                "id": "q1",
                "kind": "main",
                "objective": {"kind": "talk", "npc": "x", "target": 1},
                "on_complete": {
                    "effects": [{"type": "flag", "key": "quest_done", "value": True}],
                },
            }],
            dialogs=[{
                "id": "d1",
                "nodes": {
                    "n1": {
                        "text": "x",
                        "choices": [{
                            "label": "go",
                            "condition": {"flag": {"key": "quest_done", "value": True}},
                        }],
                    }
                },
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert not any("[A]" in e or "[B]" in e for e in errors)

    def test_flag_not_list也被捕获(self, capsys):
        """flag_not with unassigned value → [B]."""
        reg = _make_reg(
            dialogs=[{
                "id": "d_fn",
                "nodes": {
                    "n1": {
                        "text": "x",
                        "choices": [{
                            "label": "A",
                            "condition": {"flag_not": [{"key": "mood", "value": "angry"}]},
                        }],
                    }
                },
            }],
            quests=[{
                "id": "q_fn",
                "kind": "main",
                "objective": {"kind": "talk", "npc": "x", "target": 1},
                "on_complete": {
                    "effects": [{"type": "flag", "key": "mood", "value": "calm"}],
                },
            }],
        )
        errors = []
        _validate_flag_consistency(reg, errors)
        assert any("mood" in e and "[B]" in e for e in errors)
