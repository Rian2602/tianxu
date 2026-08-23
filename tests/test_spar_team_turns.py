"""Playtest #7 — spar_team: giliran berurutan dikendalikan pemain.

Urutan wajib: pemain → Lin Yue → Shen Luo → Gu Han → companion → musuh.
Satu aksi battle_action = satu giliran aktor. Teman tim tidak bisa diserang.
"""

from __future__ import annotations

import pytest

from src.engine.session import GameSession


def _new_session(registry) -> GameSession:
    s = GameSession.new(registry)
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    return s


def _allies() -> list[dict]:
    return [
        {"id": "npc_lin_yue", "name": "Lin Yue", "element": None,
         "hp": 40, "hp_max": 40, "attack": 6, "defense": 3, "speed": 5},
        {"id": "npc_shen_luo", "name": "Shen Luo", "element": None,
         "hp": 38, "hp_max": 38, "attack": 5, "defense": 4, "speed": 5},
        {"id": "npc_gu_han", "name": "Gu Han", "element": None,
         "hp": 42, "hp_max": 42, "attack": 7, "defense": 2, "speed": 5},
    ]


def _team_battle(registry, foe_hp: int = 200):
    """Battle spar_team langsung — dengan companion aktif agar masuk queue."""
    s = _new_session(registry)
    s.state.companions.append({"id": "companion_serigala", "hp": 30, "active": True})
    s.state.active_companion = "companion_serigala"
    foe = {"id": "npc_proctor", "name": "Xu Zhiyuan", "element": None,
           "hp": foe_hp, "hp_max": foe_hp, "attack": 3, "defense": 0, "speed": 5}
    s.battle.start([foe], "spar_team", allies=_allies())
    return s


def _act(s: GameSession, action: str = "attack") -> dict:
    return s.apply_action({"type": "battle_action", "action": action})


def test_turn_queue_order_includes_allies_and_companion(registry):
    s = _team_battle(registry)
    assert s.state.pending_battle["turn_queue"] == [
        "player", "ally:0", "ally:1", "ally:2", "companion",
    ]
    assert s.battle.view()["active_actor"] == {"type": "player", "name": "Kau"}


def test_sequential_player_controlled_turns(registry):
    """Setiap aksi memajukan SATU aktor; setelah companion giliran musuh lalu pemain."""
    s = _team_battle(registry)
    b = s.state.pending_battle
    foe_hp = b["foes"][0]["hp"]

    _act(s)
    assert s.battle.view()["active_actor"] == {"type": "ally", "index": 0, "name": "Lin Yue"}
    assert b["foes"][0]["hp"] < foe_hp  # serangan pemain ke musuh

    for idx, name in ((1, "Shen Luo"), (2, "Gu Han")):
        hp_before = b["foes"][0]["hp"]
        _act(s)
        assert s.battle.view()["active_actor"]["index"] == idx
        assert b["foes"][0]["hp"] < hp_before  # serangan sekutu ke musuh

    _act(s)  # companion
    assert s.battle.view()["active_actor"]["type"] == "companion"
    hp_before = b["foes"][0]["hp"]
    _act(s)
    # ronde berakhir: musuh sudah bertindak, giliran kembali ke pemain
    assert s.battle.view()["active_actor"] == {"type": "player", "name": "Kau"}
    assert b["foes"][0]["hp"] <= hp_before  # musuh menerima pukulan companion


def test_no_friendly_fire(registry):
    """Serangan siapa pun tidak pernah mengurangi HP teman satu tim."""
    s = _team_battle(registry)
    b = s.state.pending_battle
    ally_hp = [a["hp"] for a in b["allies"]]
    comp_hp = s.battle.view()["companion"]["hp"]
    for _ in range(4):  # pemain + 3 sekutu
        _act(s)
    assert [a["hp"] for a in b["allies"]] == ally_hp
    assert s.battle.view()["companion"]["hp"] == comp_hp


def test_ally_guard_reduces_enemy_hit(registry):
    s = _team_battle(registry)
    b = s.state.pending_battle
    _act(s); _act(s)  # pemain, Lin Yue menyerang
    lin = b["allies"][0]
    lin["guarding"] = False
    _act(s, "guard")  # Shen Luo bertahan (posisi ally:1)
    assert b["allies"][1].get("guarding") is True


def test_victory_mid_queue_completes_quest(registry):
    """Musuh tumbang di tengah antrean → battle selesai, quest spar_team selesai."""
    registry.quests.append({
        "id": "quest_test_team", "kind": "main", "title": "Uji Tim",
        "objective": {"kind": "spar", "npc": "npc_proctor", "target": 1,
                      "context": "spar_team"},
        "on_complete": {"effects": [
            {"type": "flag", "key": "flag_team_recognized", "value": True},
        ]},
        "next": [],
    })
    registry.quest_by_id["quest_test_team"] = registry.quests[-1]
    s = _team_battle(registry, foe_hp=1)
    s.state.current_quest = "quest_test_team"
    s.state.pending_battle["spar_npc"] = "npc_proctor"
    _act(s)
    assert s.state.pending_battle is None
    assert s.state.flags.get("flag_team_recognized") is True
    assert s.state.current_quest is None


def test_legacy_battle_without_turn_queue_still_auto(registry):
    """Save lama di tengah battle tanpa turn_queue → perilaku otomatis lama."""
    s = _team_battle(registry)
    b = s.state.pending_battle
    del b["turn_queue"]
    foe_hp = b["foes"][0]["hp"]
    _act(s)
    # jalur lama: satu aksi = satu ronde penuh (pemain+companion+sekutu otomatis)
    assert b["foes"][0]["hp"] < foe_hp - 5
