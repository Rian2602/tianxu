"""Test battle engine — formula, elemen, regen, kritikal, KO, kemenangan."""

from __future__ import annotations

from src.engine.battle import BattleEngine, _calc_damage


def test_damage_calculation(mock_god_mode):
    # Base formula: attack * (100 / (100+defense))
    attack = 10
    defense = 100  # modifier 100/200 = 0.5
    # Hitung damage tanpa elemen (elemen netral)
    damage, _ = _calc_damage(attack, defense, "tanah", "tanah")
    # Base damage harusnya 5. Karena god_mode (no RNG var), expect tepat 5
    assert damage == 5


def test_element_advantage(mock_god_mode):
    # Air vs Api = 1.5x (karena Air mematikan Api dalam wuxing config)
    attack = 10
    defense = 100
    damage, _ = _calc_damage(attack, defense, "air", "api")
    assert damage == 8  # 5 * 1.5 = 7.5, round(7.5) = 8



def test_damage_formula_persen(monkeypatch):
    from src.loader import DataRegistry

    # deterministik: variasi 1.0 (tengah), tanpa kritikal
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)

    b = BattleEngine.__new__(BattleEngine)
    b.reg = DataRegistry()
    # attack 10 vs defense 90 → 10 * 100/190 ≈ 5.26 → 5
    dmg, crit = b._calc_damage(10, 90, None, None)
    assert dmg == round(10 * 100 / 190)
    assert crit is False


def test_damage_variasi_dan_krit_dalam_batas(monkeypatch):
    """Variasi ±20% & krit ×1.5 tetap dalam batas yang masuk akal (non-flaky)."""
    from src.loader import DataRegistry

    b = BattleEngine.__new__(BattleEngine)
    b.reg = DataRegistry()
    base = 10 * 100 / 190  # ≈ 5.26
    seen = []
    for _ in range(200):
        dmg, crit = b._calc_damage(10, 90, None, None)
        lo = base * 0.8 * (1.5 if crit else 1.0)
        hi = base * 1.2 * (1.5 if crit else 1.0)
        assert lo - 1 <= dmg <= hi + 1  # toleransi pembulatan
        seen.append(dmg)
    assert min(seen) >= 3 and max(seen) <= 10  # tanpa krit: [4,7]; dengan krit: ≤ 10


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


def test_teknik_lintas_akademi_ditolak(session):
    """Bug playtest: teknik akademi lain tidak boleh dipakai (skill_pool §5.6)."""
    # tanpa god_mode: musuh lemah, serangannya minimal — battle tetap berlanjut
    session.state.player.academy = "akademi_elemen"
    teks_senjata = session.reg.player_techniques("akademi_senjata")
    assert teks_senjata, "akademi senjata harus punya teknik"
    foe = {"id": "eno_x", "name": "X", "hp": 9999, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    qi_before = session.state.player.qi
    session.apply_action({"type": "battle_action", "action": "technique", "technique": teks_senjata[0]["id"]})
    assert session.state.pending_battle  # battle belum selesai — teknik ditolak
    assert session.state.player.qi == qi_before  # Qi tidak terpotong
    assert any("belum menguasai" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


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
