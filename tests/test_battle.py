"""Test battle engine — formula, elemen, regen, kritikal, KO, kemenangan."""

from __future__ import annotations

import pytest

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


def test_teknik_ranah_tinggi_ditolak(session, monkeypatch):
    """H4: teknik dengan realm_required lebih tinggi dari ranah pemain ditolak (ranah belum cukup)."""
    session.state.player.academy = "akademi_elemen"
    fake = {"id": "tek_elemen_palsu_tinggi", "name": "Teknik Tinggi", "academy": "elemen",
            "element": None, "realm_required": "realm_pembangun_fondasi", "qi_cost": 5,
            "power": 99, "kind": "attack", "description": "Dummy ranah tinggi."}
    monkeypatch.setattr(session.reg, "technique", lambda tid: fake if tid == fake["id"] else None)
    monkeypatch.setattr(session.reg, "player_techniques", lambda acad, realm=None: [fake])
    foe = {"id": "eno_x", "name": "X", "hp": 9999, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    qi_before = session.state.player.qi
    session.apply_action({"type": "battle_action", "action": "technique", "technique": fake["id"]})
    assert session.state.pending_battle  # battle berlanjut seperti aksi invalid lain
    assert session.state.player.qi == qi_before  # Qi tidak terpotong
    assert any("Ranahmu belum cukup" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


def test_player_techniques_filter_ranah(session):
    """H4: player_techniques menyaring teknik dengan realm_required > ranah pemain."""
    reg = session.reg
    fake = {"id": "tek_elemen_palsu_tinggi", "name": "X", "academy": "elemen",
            "realm_required": "realm_pembangun_fondasi", "qi_cost": 1, "power": 1, "kind": "attack"}
    reg.techniques[fake["id"]] = fake
    ids_pengumpul = [t["id"] for t in reg.player_techniques("akademi_elemen", "realm_pengumpul_qi")]
    assert fake["id"] not in ids_pengumpul  # order 2 > order 1 → disembunyikan
    ids_fondasi = [t["id"] for t in reg.player_techniques("akademi_elemen", "realm_pembangun_fondasi")]
    assert fake["id"] in ids_fondasi  # order 2 <= order 2 → tampil


def test_regen_qi_per_giliran(session, monkeypatch):
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    session.state.player.qi = 10
    foe = {"id": "eno_x", "name": "X", "hp": 9999, "qi": 10, "qi_max": 100, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    session.apply_action({"type": "battle_action", "action": "guard"})
    # setelah 1 giliran: regen 5% qi max (pemain & musuh)
    qi_max = session.state.max_qi(session.reg)
    assert session.state.player.qi == min(qi_max, 10 + round(qi_max * 0.05))
    assert session.state.pending_battle["foes"][0]["qi"] == 15


def test_teknik_defend(session, monkeypatch):
    """Teknik jenis 'defend' mengurangi damage masuk sesuai power teknik (60%)."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # no crit
    session.state.player.academy = "akademi_elemen"
    session.state.player.hp = 80
    session.state.player.qi = 40

    foe = {"id": "eno_test", "name": "Musuh", "hp": 500, "qi": 0, "attack": 20, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")

    session.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_perisai_tanah"})
    # Musuh serang: attack 20 vs def 3 -> base 19, defend power 60 -> int(19 * 0.4) = 7
    assert session.state.player.hp == 73
    assert any("Perisai Tanah" in e["text"] for e in session.state.log)
    assert session.state.pending_battle is not None
    session.state.pending_battle = None


def test_teknik_heal_clamped_and_unclamped(session, monkeypatch):
    """Teknik jenis 'heal' memulihkan HP dan terbatasi ke hp_max (clamped)."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    session.state.player.academy = "akademi_elemen"
    hp_max = session.state.max_hp(session.reg)

    # Kasus A: Clamped ke hp_max (hanya kurang 5 HP, heal power 20, musuh balas dealt 1 min dmg)
    session.state.player.hp = hp_max - 5
    session.state.player.qi = 40
    foe = {"id": "eno_dummy", "name": "Dummy", "hp": 500, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")

    session.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_embun_air"})
    # Healed to hp_max, then foe attacks for min 1 damage -> hp_max - 1
    assert session.state.player.hp == hp_max - 1
    assert any("memulihkan 5 HP" in e["text"] for e in session.state.log)
    session.state.pending_battle = None

    # Kasus B: Unclamped (kurang 40 HP, heal power 20, musuh balas dealt 1 min dmg)
    session.state.player.hp = hp_max - 40
    session.state.player.qi = 40
    session.battle.start([foe], "hunt")
    session.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_embun_air"})
    # Healed 20 (hp was hp_max - 40 -> hp_max - 20), foe deals 1 dmg -> hp_max - 21
    assert session.state.player.hp == hp_max - 21
    assert any("memulihkan 20 HP" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


def test_battle_item_usage(session, monkeypatch):
    """Penggunaan item di battle: item tidak ada, non-consumable, dan consumable."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    foe = {"id": "eno_dummy", "name": "Dummy", "hp": 500, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}

    # 1. Item tidak dimiliki
    session.battle.start([foe], "hunt")
    session.state.inventory.clear()
    session.apply_action({"type": "battle_action", "action": "item", "item": "pil_qi"})
    assert any("Item tidak tersedia" in e["text"] for e in session.state.log)
    session.state.pending_battle = None

    # 2. Item bukan consumable (misalnya pedang_angin)
    session.battle.start([foe], "hunt")
    session.state.inventory["pedang_angin"] = 1
    session.apply_action({"type": "battle_action", "action": "item", "item": "pedang_angin"})
    assert any("Item itu tidak bisa dipakai di battle" in e["text"] for e in session.state.log)
    session.state.pending_battle = None

    # 3. Item consumable (pil_qi)
    session.battle.start([foe], "hunt")
    session.state.player.qi = 5
    session.state.inventory["pil_qi"] = 1
    session.apply_action({"type": "battle_action", "action": "item", "item": "pil_qi"})
    assert "pil_qi" not in session.state.inventory
    assert session.state.player.qi > 5
    assert any("Memakai Pil Qi" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


def test_battle_flee_failed_and_success(session, monkeypatch):
    """Percobaan kabur: gagal (RNG tinggi) vs berhasil (RNG rendah)."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    foe = {"id": "eno_fast", "name": "Monster Cepat", "hp": 500, "qi": 0, "attack": 0, "defense": 0,
           "speed": 99, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}

    # Gagal kabur (random.random() = 0.99 >= chance)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 0.99)
    session.battle.start([foe], "hunt")
    v = session.apply_action({"type": "battle_action", "action": "flee"})
    assert any("Kau gagal kabur!" in e["text"] for e in session.state.log)
    assert session.state.pending_battle is not None
    assert v["mode"] == "battle"
    session.state.pending_battle = None

    # Berhasil kabur (random.random() = 0.0 < chance)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 0.0)
    session.battle.start([foe], "hunt")
    v = session.apply_action({"type": "battle_action", "action": "flee"})
    assert any("Kau berhasil kabur" in e["text"] for e in session.state.log)
    assert session.state.pending_battle is None
    assert v["mode"] == "explore"


def test_battle_spar_loss_exp(session):
    """Saat kalah (KO) di pertandingan spar, pemain mendapat spar_loss_exp."""
    session.state.player.exp = 0
    foe = {"id": "eno_spar", "name": "Han Xiu", "hp": 500, "qi": 0, "attack": 999, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "spar")
    session.state.pending_battle["spar_npc"] = "npc_hanxiu"

    session.apply_action({"type": "battle_action", "action": "attack"})  # Musuh balas dengan attack 999 -> KO
    assert session.state.pending_battle is None
    assert session.state.location == "loc_asrama"  # respawn di safe zone
    assert session.state.player.hp == session.state.max_hp(session.reg)
    # Exp bertambah karena spar_loss_exp
    loss_exp = session.reg.config["cultivation"]["spar_loss_exp"]
    assert session.state.player.exp == loss_exp


def test_battle_unknown_technique_and_low_qi(session):
    session.state.player.academy = "akademi_elemen"
    foe = {"id": "eno_x", "name": "X", "hp": 500, "qi": 0, "attack": 0, "defense": 0, "speed": 1}
    session.battle.start([foe], "hunt")

    # Teknik tidak dikenal
    session.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_ngawur"})
    assert any("Teknik tidak dikenal" in e["text"] for e in session.state.log)

    # Qi tidak cukup
    session.state.player.qi = 0
    session.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_bola_api"})
    assert any("Qi tidak cukup" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


def test_companion_in_battle_attack_and_ko(session, monkeypatch):
    from src.engine.battle import companion_stats

    # companion_stats when companion is None or inactive
    session.state.companion = None
    assert companion_stats(session.state, session.reg) is None
    session.state.companion = {"id": "comp_unknown", "active": True, "hp": 50}
    assert companion_stats(session.state, session.reg) is None

    # Valid companion (komp_roh_awan)
    session.state.companion = {"id": "komp_roh_awan", "active": True, "hp": 20}
    c_stats = companion_stats(session.state, session.reg)
    assert c_stats is not None
    assert c_stats["name"] == "Roh Awan"

    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    # Musuh serang target companion (random.random() < 0.5)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 0.1)

    foe = {"id": "eno_strong", "name": "Serigala", "hp": 100, "qi": 0, "attack": 100, "defense": 0, "speed": 1}
    session.battle.start([foe], "hunt")

    # Giliran guard -> companion menyerang musuh, lalu musuh menyerang kompanion hingga KO
    session.apply_action({"type": "battle_action", "action": "guard"})
    assert session.state.companion["active"] is False
    assert session.state.companion["hp"] == 0
    assert any("KO" in e["text"] for e in session.state.log)
    session.state.pending_battle = None

    # Kasus: Companion diserang tapi tidak sampai KO
    session.state.companion = {"id": "komp_roh_awan", "active": True, "hp": 50}
    foe_weak = {"id": "eno_weak", "name": "Kelinci", "hp": 100, "qi": 0, "attack": 2, "defense": 0, "speed": 1}
    session.battle.start([foe_weak], "hunt")
    session.apply_action({"type": "battle_action", "action": "guard"})
    assert session.state.companion["active"] is True
    assert session.state.companion["hp"] < 50 and session.state.companion["hp"] > 0
    assert any("menyerang Roh Awan" in e["text"] for e in session.state.log)
    session.state.pending_battle = None


def test_battle_spar_win_exp(session):
    """Menang pertarungan spar memberikan spar_win_exp dan memanggil notify_spar_won."""
    foe = {"id": "eno_spar", "name": "Han Xiu", "hp": 5, "qi": 0, "attack": 0, "defense": 0,
           "speed": 1, "element": None, "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "spar")
    session.state.pending_battle["spar_npc"] = "npc_hanxiu"
    exp_before = session.state.player.exp

    session.apply_action({"type": "battle_action", "action": "attack"})
    assert session.state.pending_battle is None
    win_exp = session.reg.config["cultivation"]["spar_win_exp"]
    assert session.state.player.exp >= exp_before + win_exp


def test_battle_view_no_battle(session):
    session.state.pending_battle = None
    assert session.battle.view() == {"mode": "explore"}
    # player_action saat battle None
    assert session.battle.player_action({"action": "attack"}) == {"mode": "explore"}


def test_battle_item_decrement_not_deleted(session, monkeypatch):
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    foe = {"id": "eno_dummy", "name": "Dummy", "hp": 500, "qi": 0, "attack": 0, "defense": 0, "speed": 1}
    session.battle.start([foe], "hunt")
    session.state.inventory["pil_qi"] = 2
    session.apply_action({"type": "battle_action", "action": "item", "item": "pil_qi"})
    assert session.state.inventory.get("pil_qi") == 1
    session.state.pending_battle = None


def test_battle_multiple_foes_with_dead_foe(session, monkeypatch):
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    foes = [
        {"id": "eno_dead", "name": "Mati", "hp": 0, "qi": 0, "attack": 10, "defense": 0, "speed": 1},
        {"id": "eno_alive", "name": "Hidup", "hp": 100, "qi": 0, "attack": 5, "defense": 0, "speed": 1}
    ]
    session.battle.start(foes, "hunt")
    # Serang musuh pertama
    session.apply_action({"type": "battle_action", "action": "guard"})
    assert session.state.pending_battle is not None
    session.state.pending_battle = None


@pytest.mark.parametrize("akademi, teknik_id, nama_teknik", [
    ("akademi_elemen", "tek_elemen_bola_api", "Bola Api"),
    ("akademi_senjata", "tek_senjata_tebasan_angin", "Tebasan Angin"),
    ("akademi_summoning", "tek_summoning_roh_api", "Roh Api"),
])
def test_teknik_akademi_dipakai_di_battle(session, monkeypatch, akademi, teknik_id, nama_teknik):
    """A1: teknik khas tiap akademi (elemen/senjata/summoning) bisa dieksekusi di battle."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # no crit
    session.state.player.academy = akademi
    session.state.player.qi = 50  # cukup untuk biaya teknik apa pun
    session.state.location = "loc_wilayah_berburu"
    session.state.last_hunt_time = None
    session.apply_action({"type": "hunt"})
    assert session.state.pending_battle is not None
    session.apply_action({"type": "battle_action", "action": "technique", "technique": teknik_id})
    assert any(nama_teknik in e["text"] for e in session.state.log), \
        f"teknik {teknik_id} tidak tereksekusi untuk {akademi}"
    session.state.pending_battle = None


def test_speed_order_musuh_lebih_cepat_menyerang_dulu(session, monkeypatch):
    """A2 (keputusan §17): turn_order "speed" — musuh lebih cepat bertindak dulu;
    guard pemain tidak menahan serangan yang datang lebih awal (damage penuh)."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # no crit
    foe = {"id": "eno_cepat", "name": "Cepat", "hp": 999, "qi": 0,
           "attack": 10, "defense": 0, "speed": 20, "element": None,
           "exp_reward": 0, "drop_item": None, "drop_chance": 0}
    session.battle.start([foe], "hunt")
    hp_before = session.state.player.hp
    session.apply_action({"type": "battle_action", "action": "guard"})
    lost = hp_before - session.state.player.hp
    # damage penuh (guard tidak sempat aktif karena musuh duluan) — bukan setengah
    assert lost >= 8, f"musuh cepat harus menyerang duluan dengan damage penuh, lost={lost}"
    session.state.pending_battle = None


def test_cap_exp_grind_harian(session, god_mode):
    """A2 (keputusan §17): exp berburu dibatasi cap harian (daily_grind_exp_cap)."""
    cap = int(session.reg.config["cultivation"]["daily_grind_exp_cap"])
    assert cap > 0
    session.state.exp_grind_today = cap - 5  # sisa 5
    session.state.location = "loc_wilayah_berburu"
    session.state.last_hunt_time = None
    session.apply_action({"type": "hunt"})  # serigala exp 15
    exp_before = session.state.player.exp
    session.apply_action({"type": "battle_action", "action": "attack"})
    gained = session.state.player.exp - exp_before
    assert gained == 5, f"exp harus dipotong jadi 5, dapat {gained}"
    assert session.state.exp_grind_today == cap
    session.state.pending_battle = None


def test_companion_turn_no_alive_foe_is_noop(session):
    """Guard: tidak ada musuh hidup → _companion_turn tidak melakukan apa-apa."""
    session.state.companion = {"id": "komp_roh_awan", "hp": 10, "active": True}
    session.battle.start([{"id": "eno_test", "name": "Musuh", "hp": 0, "qi": 0, "qi_max": 0,
                           "attack": 1, "defense": 0, "speed": 1, "element": None,
                           "exp_reward": 0, "drop_item": None, "drop_chance": 0}], "hunt")
    session.battle._companion_turn(session.state.pending_battle)
    assert session.state.pending_battle["foes"][0]["hp"] == 0



