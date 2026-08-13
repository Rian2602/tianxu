"""Test battle engine — formula, elemen, regen, kritikal, KO, kemenangan."""

from __future__ import annotations

from src.engine.battle import BattleEngine


def test_damage_formula_persen():
    from src.loader import DataRegistry

    b = BattleEngine.__new__(BattleEngine)
    b.reg = DataRegistry()
    # attack 10 vs defense 90 → 10 * 100/190 ≈ 5
    dmg, crit = b._calc_damage(10, 90, None, None)
    assert 3 <= dmg <= 7  # ±20% dari 5.26


def test_damage_minimal_satu():
    from src.loader import DataRegistry

    b = BattleEngine.__new__(BattleEngine)
    b.reg = DataRegistry()
    dmg, _ = b._calc_damage(1, 99999, None, None)
    assert dmg >= 1


def test_elemen_keuntungan(monkeypatch):
    from src.loader import DataRegistry
    from src.engine.battle import BattleEngine

    reg = DataRegistry()
    b = BattleEngine.__new__(BattleEngine)
    b.reg = reg
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # tanpa krit
    # api menyerang logam → api克logam = 1.5×
    dmg_adv, _ = b._calc_damage(10, 0, "api", "logam")
    dmg_neutral, _ = b._calc_damage(10, 0, "api", "api")
    assert dmg_adv == round(10 * 1.5)
    assert dmg_neutral == 10


def test_elemen_kerugian(monkeypatch):
    from src.loader import DataRegistry
    from src.engine.battle import BattleEngine

    reg = DataRegistry()
    b = BattleEngine.__new__(BattleEngine)
    b.reg = reg
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    # api vs air → air克api → 0.67× (siklus: air→api)
    dmg, _ = b._calc_damage(10, 0, "api", "air")
    assert dmg == round(10 * 0.67)
    # api vs tanah → netral 1.0×
    dmg2, _ = b._calc_damage(10, 0, "api", "tanah")
    assert dmg2 == 10


def test_kemenangan_beri_exp_dan_drop(session, god_mode, monkeypatch):
    # kalahkan serigala (hunt) → exp + kemungkinan drop tulang
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 0.0)  # drop selalu terjadi
    session.apply_action({"type": "move", "to": "loc_gerbang_akademi"})
    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    exp_before = session.state.player.exp
    session.apply_action({"type": "battle_action", "action": "attack"})
    assert session.state.pending_battle is None
    assert session.state.player.exp > exp_before  # exp reward serigala
    # random 0.0 < drop_chance → tulang pasti didapat
    assert session.state.inventory.get("material_tulang", 0) >= 1


def test_ko_respawn_dan_penalti_exp(session):
    # kekalahan: musuh sangat kuat → player KO
    foe = {"id": "eno_boss_test", "name": "Bos Uji", "hp": 9999, "qi": 0,
           "attack": 999, "defense": 999, "speed": 1, "element": None,
           "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    exp_before = session.state.player.exp
    session.apply_action({"type": "battle_action", "action": "attack"})  # musuh balas → KO
    assert session.state.pending_battle is None
    assert session.state.player.hp == session.state.max_hp(session.reg)  # respawn pulih
    assert session.state.location == "loc_asrama"  # titik aman default
    assert session.state.player.exp <= exp_before  # penalti exp (0 → tetap 0)


def test_teknik_serang_di_battle(session, god_mode):
    session.state.player.academy = "akademi_elemen"
    teks = session.reg.player_techniques("akademi_elemen")
    assert teks, "akademi elemen harus punya teknik"
    foe = {"id": "eno_x", "name": "X", "hp": 999, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    session.apply_action({"type": "battle_action", "action": "technique", "technique": teks[0]["id"]})
    assert session.state.pending_battle is None  # god mode: 1 teknik menang
    assert session.state.player.qi < session.state.max_qi(session.reg)  # qi_cost terpotong


def test_regen_qi_per_giliran(session, monkeypatch):
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    session.state.player.qi = 10
    foe = {"id": "eno_x", "name": "X", "hp": 9999, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    session.apply_action({"type": "battle_action", "action": "guard"})
    # setelah 1 giliran: regen 5% qi max
    qi_max = session.state.max_qi(session.reg)
    assert session.state.player.qi == min(qi_max, 10 + round(qi_max * 0.05))
