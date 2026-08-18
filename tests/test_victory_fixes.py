"""Regression test — bug audit Claude di battle.py.

1. `_victory` meng-sync HP/Qi SEBELUM grant exp — level-up (full-heal di
   cultivation._level_up) tidak boleh ditimpa snapshot pra-reward.
2. `companion_stats` — hp kompanion persis 0 (KO) harus tampil 0, bukan jatuh
   ke hp_max karena 0 falsy di Python (`c.get("hp") or hp_max`).
3. RED->GREEN script Claude (stub registry standalone) — invariant yang sama
   diuji unit-level via panggilan `_victory` langsung, tanpa data loader.

Data sintetis (pola test_adaptivity.build_data) — cepat, tidak menyentuh data/.
"""

from __future__ import annotations

import types

from tests.test_adaptivity import build_data
from src.loader import DataRegistry
from src.engine.session import GameSession


def _sess(tmp_path, *, quests, enemies, companions=None, realms=None):
    kw = dict(quests=quests, npcs=[], enemies=enemies)
    if companions is not None:
        kw["companions"] = companions
    if realms is not None:
        kw["realms"] = realms
    d = build_data(tmp_path, **kw)
    reg = DataRegistry(data_dir=d)
    return reg, GameSession.new(reg)


def _quest_choose():
    return {"id": "q1", "kind": "main", "title": "T",
            "objective": {"kind": "choose",
                          "options": [{"value": "a", "label": "A"}]}}


def test_victory_levelup_full_heal_survives(tmp_path):
    """Bug #1: menang battle yang memicu level-up → full-heal dari level-up
    TIDAK boleh hilang. Sebelum perbaikan, _sync_player(pc) setelah grant exp
    menimpa HP dengan snapshot pra-reward (HP sisa pertarungan)."""
    # levels=2 → level-up di ranah r1 bersih (tanpa breakthrough); exp_next lvl1
    # = round(10 × 1.2^0) = 10 → exp 9 + reward 10 cukup memicu level-up.
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()],
                   enemies=[{"id": "e1", "name": "E1", "hp": 5, "attack": 0,
                             "defense": 0, "exp_reward": 10}],
                   realms=realms)
    # pemain terluka & di ambang level-up
    s.state.player.hp = 10
    s.state.player.qi = 5
    s.state.player.exp = 9
    assert s.state.player.realm_level == 1

    s.battle.start([reg.enemy("e1")], "hunt")
    s.battle.player_action({"action": "attack"})  # satu serangan → menang

    assert s.state.pending_battle is None
    assert s.state.player.realm_level == 2, "reward exp harus memicu level-up"
    # full-heal level-up bertahan (bug lama: hp kembali 10)
    assert s.state.player.hp == s.state.max_hp(reg) == 55, \
        f"HP harus penuh setelah level-up, dapat {s.state.player.hp}"
    assert s.state.player.qi == s.state.max_qi(reg) == 33, \
        f"Qi harus penuh setelah level-up, dapat {s.state.player.qi}"


def test_victory_without_levelup_syncs_combat_hp(tmp_path):
    """Kontrol: tanpa level-up, HP hasil pertarungan tetap tersinkron (perilaku
    normal tidak berubah — sync tetap terjadi, hanya dipindah lebih awal)."""
    realms = [{"id": "r1", "name": "R1", "name_pinyin": "R1", "order": "1",
               "levels": "2", "base_hp": "50", "hp_per_level": "5",
               "base_qi": "30", "qi_per_level": "3"}]
    reg, s = _sess(tmp_path, quests=[_quest_choose()],
                   enemies=[{"id": "e1", "name": "E1", "hp": 5, "attack": 0,
                             "defense": 0, "exp_reward": 1}],
                   realms=realms)
    s.state.player.hp = 10
    s.state.player.exp = 0  # reward 1 → tidak level-up (butuh 10)

    s.battle.start([reg.enemy("e1")], "hunt")
    s.battle.player_action({"action": "attack"})

    assert s.state.player.realm_level == 1
    # musuh attack=0 → pemain hanya kena damage musuh (0) — HP tetap 10
    assert s.state.player.hp == 10
    assert s.state.player.exp == 1


def test_companion_stats_hp_zero_not_full(tmp_path):
    """Bug #2: hp kompanion 0 (KO) → companion_stats menampilkan 0, bukan
    hp_max (0 or hp_max jatuh ke hp_max karena 0 falsy di Python)."""
    reg, s = _sess(tmp_path, quests=[_quest_choose()],
                   enemies=[{"id": "e1", "name": "E1", "hp": 5, "attack": 0,
                             "defense": 0, "exp_reward": 1}],
                   companions=[{"id": "c1", "name": "Komp", "base_hp": 20,
                                "base_attack": 3, "base_defense": 1,
                                "base_speed": 5}])
    from src.engine.battle import companion_stats
    s.state.companion = {"id": "c1", "active": True, "hp": 0}
    st = companion_stats(s.state, reg)
    assert st is not None
    assert st["hp"] == 0, f"KO harus tampil 0 HP, dapat {st['hp']}"

    # hp parsial tetap dihormati; None (save lama) → hp_max
    s.state.companion["hp"] = 7
    assert companion_stats(s.state, reg)["hp"] == 7
    s.state.companion["hp"] = None
    st = companion_stats(s.state, reg)
    assert st["hp"] == st["hp_max"] == 32, "None → default hp_max (20 + 1×12)"


def test_victory_levelup_heal_standalone_stub():
    """RED->GREEN script Claude, diadaptasi jadi test permanen: modul engine
    ASLI (src.engine.*) + stub registry minimal (duck-typed, tanpa data
    JSON/CSV) + panggilan `_victory` langsung — invariant urutan sync-vs-exp
    diuji unit-level. Stub menyediakan `roots_tier` (tanpa itu engine saat ini
    crash AttributeError di exp_multiplier — temuan verifikasi)."""
    from src.engine.state import GameState, PlayerState
    from src.engine.battle import BattleEngine, player_combat

    class StubRegistry:
        """Stub sengaja minimal — hanya atribut yang benar-benar dipakai jalur ini."""
        def __init__(self, config, realms):
            self.config = config
            self.realms = realms
            self.roots_tier = {}          # dipakai state.exp_multiplier()
            self.element_advantage = {}
            self.companions = []

        def item(self, iid):
            return None

        def realm_by_id(self, rid):
            return self.realms.get(rid)

    config = {
        "cultivation": {"exp_per_level_base": 10, "exp_growth_per_level": 1.0,
                        "daily_grind_exp_cap": 0},
        "battle": {"crit_chance": 0.0, "turn_order": "fixed"},
    }
    realms = {
        "realm_awal": {"order": 1, "levels": 2, "base_hp": 50, "hp_per_level": 10,
                       "base_qi": 20, "qi_per_level": 5, "name_pinyin": "Awal"},
    }
    # exp=9, exp_next lvl1 = round(10 × 1.0^0) = 10 → reward 1 cukup level-up
    player = PlayerState(name="Tester", hp=5, qi=2, realm="realm_awal", realm_level=1,
                         gold=0, roots="akar_mid", exp=9)
    state = GameState(player=player, location="loc1", day=1, hour=6, current_quest=None)
    reg = StubRegistry(config, realms)
    be = BattleEngine(reg, state,
                      quest_engine=types.SimpleNamespace(notify_battle_won=lambda *a: None))

    foe = {"id": "musuh1", "name": "Musuh", "hp": 1, "hp_max": 1, "attack": 0,
           "defense": 0, "speed": 0, "exp_reward": 1, "drop_chance": 0}
    be.start([foe], context="hunt")

    pc_before = player_combat(state, reg)
    assert state.player.hp == 5, "sanity: hp sisa pertarungan sebelum menang tetap 5"
    # unit-level: panggil _victory langsung (bukan player_action) — persis skenario Claude
    be._victory(state.pending_battle, pc_before)

    assert state.player.realm_level == 2, "reward exp harus memicu level-up"
    assert state.player.hp == state.max_hp(reg) == 60, (
        f"BUG: HP harus penuh ({state.max_hp(reg)}) setelah level-up saat menang, "
        f"tapi malah {state.player.hp} (HP sisa pertarungan sebelum reward).")
