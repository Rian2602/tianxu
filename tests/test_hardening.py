"""Regression tests — hardening audit (2026-08-18).

Temuan audit lengkap: battle.py falsy-zero, session.py spar/scope/deref,
state.py max_hp/realm_level/serialization, effects.py KeyError/types.
"""

from __future__ import annotations

from tests.test_adaptivity import build_data
from src.loader import DataRegistry
from src.engine.session import GameSession


def _sess(tmp_path, *, quests, enemies=None, companions=None, realms=None,
          npcs=None, config_extra=None):
    kw = dict(quests=quests, npcs=npcs or [], enemies=enemies or [])
    if companions is not None:
        kw["companions"] = companions
    if realms is not None:
        kw["realms"] = realms
    if config_extra is not None:
        kw["config_extra"] = config_extra
    d = build_data(tmp_path, **kw)
    reg = DataRegistry(data_dir=d)
    return reg, GameSession.new(reg)


def _quest_choose():
    return {"id": "q1", "kind": "main", "title": "T",
            "objective": {"kind": "choose",
                          "options": [{"value": "a", "label": "A"}]}}


# --- Task 1: battle.py falsy-zero ---

def test_foe_hp_zero_stays_zero(tmp_path):
    """enemy hp=0 tidak boleh di-reset ke 10 karena `0 or 10` = 10."""
    reg, s = _sess(tmp_path, quests=[_quest_choose()])
    foe = {"id": "e1", "name": "E1", "hp": 0,
           "attack": 1, "defense": 0, "exp_reward": 1}
    s.battle.start([foe], "hunt")
    result = s.state.pending_battle["foes"][0]
    assert result["hp"] == 0, f"hp=0 harus tetap 0, dapat {result['hp']}"


def test_foe_hp_missing_gets_default(tmp_path):
    """enemy tanpa kolom hp mendapat default 10."""
    reg, s = _sess(tmp_path, quests=[_quest_choose()])
    foe = {"id": "e1", "name": "E1",
           "attack": 1, "defense": 0, "exp_reward": 1}
    s.battle.start([foe], "hunt")
    result = s.state.pending_battle["foes"][0]
    assert result["hp"] == 10, f"hp default harus 10, dapat {result['hp']}"
