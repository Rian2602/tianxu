"""Regression tests — hardening audit (2026-08-18).

Temuan audit lengkap: battle.py falsy-zero, session.py spar/scope/deref,
state.py max_hp/realm_level/serialization, effects.py KeyError/types.
"""

from __future__ import annotations

from tests.test_adaptivity import build_data
from src.loader import DataRegistry
from src.engine.session import GameSession


def _sess(tmp_path, *, quests, enemies=None, companions=None, realms=None,
          npcs=None, items=None, config_extra=None):
    kw = dict(quests=quests, npcs=npcs or [], enemies=enemies or [])
    if companions is not None:
        kw["companions"] = companions
    if realms is not None:
        kw["realms"] = realms
    if items is not None:
        kw["items"] = items
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


# --- Task 2: state.py max_hp fallback + realm_level ---

def test_max_hp_unknown_realm_returns_base(tmp_path):
    """max_hp fallback untuk ranah tak dikenal harus return base_hp default,
    bukan current HP (yang bikin rest jadi no-op)."""
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    # simulasikan realm corrupt
    s.state.player.realm = "realm_corrupt"
    s.state.player.hp = 10
    # fallback harus return default 50, bukan current HP (10)
    assert s.state.max_hp(reg) == 50, f"fallback max_hp harus 50, dapat {s.state.max_hp(reg)}"


def test_max_hp_realm_level_zero_no_negative(tmp_path):
    """realm_level=0 (corrupt save) tidak boleh menghasilkan max_hp negatif."""
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    s.state.player.realm_level = 0
    # level 0 → guard clamps to 1 → base + 0*per = base
    assert s.state.max_hp(reg) == 50, f"max_hp realm_level=0 harus 50, dapat {s.state.max_hp(reg)}"
    assert s.state.max_qi(reg) == 30, f"max_qi realm_level=0 harus 30, dapat {s.state.max_qi(reg)}"


# --- Task 3: state.py pending_dialog serialization ---

def test_pending_dialog_roundtrip(tmp_path):
    """pending_dialog harus survive save/load — dialog tidak boleh hilang."""
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    s.state.pending_dialog = "dlg_test_123"
    d = s.state.to_dict()
    assert d.get("pending_dialog") == "dlg_test_123", \
        f"to_dict harus include pending_dialog, dapat {d.get('pending_dialog')}"
    from src.engine.state import GameState
    loaded = GameState.from_dict(d)
    assert loaded.pending_dialog == "dlg_test_123", \
        f"from_dict harus restore pending_dialog, dapat {loaded.pending_dialog}"


# --- Task 4: effects.py KeyError + type coercion ---

def test_flag_effect_missing_key_no_crash(tmp_path):
    """flag effect tanpa field 'key' tidak boleh KeyError — defense-in-depth."""
    from src.engine.effects import apply as apply_effects
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    # flag effect tanpa 'key' — tidak boleh crash
    apply_effects(s.state, reg, [{"type": "flag", "value": True}])
    # state tetap utuh
    assert isinstance(s.state.flags, dict)


def test_morality_effect_string_value_no_crash(tmp_path):
    """morality effect dengan value string tidak boleh TypeError."""
    from src.engine.effects import apply as apply_effects
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    before = s.state.player.morality
    apply_effects(s.state, reg, [{"type": "morality", "value": "5"}])
    assert s.state.player.morality == before + 5


def test_item_effect_float_count_becomes_int(tmp_path):
    """item effect dengan count float harus di-cast ke int."""
    from src.engine.effects import apply as apply_effects
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], realms=realms)
    apply_effects(s.state, reg, [{"type": "item", "id": "i1", "count": 2.0}])
    assert s.state.inventory.get("i1") == 2
    assert isinstance(s.state.inventory.get("i1"), int)


# --- Task 5: session.py spar/scope/deref ---

def test_spar_quest_no_combat_npc_logs_error(tmp_path):
    """spar quest dengan NPC tanpa data combat harus log error, bukan diam-diam pecah."""
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    npc_spar = {"id": "npc_spar", "name": "Spar NPC", "location": "l_start",
                "can_spar": False, "dialog_routes": {}}
    q_spar = {"id": "q_spar", "kind": "main", "title": "Spar Quest",
              "objective": {"kind": "spar", "npc": "npc_spar"}}
    reg, s = _sess(tmp_path, quests=[q_spar], npcs=[npc_spar], realms=realms)
    s.state.current_quest = "q_spar"
    s.state.flags["q_spar_started"] = True
    s.dialog.last_npc = "npc_spar"
    s.quest.notify_dialog_ended("npc_spar", None)
    assert s.state.pending_battle is None


def test_shop_buy_item_not_in_registry_no_crash(tmp_path):
    """shop_buy dengan item ID yang tidak ada di registry tidak boleh crash."""
    from unittest.mock import patch
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    npc_shop = {"id": "npc_merchant", "name": "Merchant", "location": "l_start",
                "shop": {"buy": [{"item": "i_missing", "price": 10}]},
                "dialog_routes": {}}
    dummy_item = [{"id": "i_missing", "name": "Missing", "type": "consumable"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()], npcs=[npc_shop], realms=realms,
                   items=dummy_item)
    s.state.player.gold = 100
    orig_item = reg.item
    def _no_item(iid):
        return None
    with patch.object(reg, "item", _no_item):
        result = s.apply_action({"type": "shop_buy", "item": "i_missing"})
    assert result is not None
