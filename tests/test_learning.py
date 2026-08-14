"""Test suite untuk Sistem Pembelajaran Teknik & Starter Kit Akademi (R1–R4).

Menguji 14 kasus uji:
 1. Konfigurasi curriculum dan starter_kit data pada 3 akademi
 2. Item baru (talisman_elemen, kontrak_roh) di items.csv
 3. Pemilihan Paviliun Elemen memberikan starter_kit (talisman_elemen)
 4. Pemilihan Paviliun Senjata memberikan starter_kit (pedang_bambu)
 5. Pemilihan Paviliun Summoning memberikan starter_kit (kontrak_roh) & kompanion
 6. Starter kit bertahan saat save/load tanpa duplikasi
 7. Alur quest DAG: q_akademi_04 -> q_akademi_04b -> q_akademi_05
 8. Dialog Gu Canghai mengajarkan teknik dasar Elemen (tek_elemen_bola_api)
 9. Dialog Gu Canghai mengajarkan teknik dasar Senjata (tek_senjata_tebasan_angin)
10. Dialog Gu Canghai mengajarkan teknik dasar Summoning (tek_summoning_roh_api)
11. Pembelajaran berbiaya 0 emas dan hanya via dialog naratif
12. Restriksi pertempuran: hanya teknik di player.techniques yang bisa dipakai
13. Helper DataRegistry.academy_curriculum mengembalikan urutan teknik yang tepat
14. Web context curriculum status: progression (learned, available, locked)
"""

import pytest
from src.engine.session import GameSession
from src.loader import DataRegistry
from tests.conftest import finish_dialog, move_path


# 1. Konfigurasi curriculum & starter_kit data
def test_config_curriculum_and_starter_kit_data(session):
    reg = session.reg
    academies = reg.config.get("academies", [])
    acad_map = {a["id"]: a for a in academies}

    assert "akademi_elemen" in acad_map
    assert "akademi_senjata" in acad_map
    assert "akademi_summoning" in acad_map

    for aid, a in acad_map.items():
        curr = a.get("curriculum")
        assert isinstance(curr, list) and len(curr) == 3, f"{aid} harus punya 3 teknik kurikulum"
        for tid in curr:
            assert reg.technique(tid) is not None, f"teknik {tid} di {aid} harus ada di techniques.csv"

        sk = a.get("starter_kit")
        assert isinstance(sk, list) and len(sk) >= 1, f"{aid} harus punya starter_kit"
        for item_entry in sk:
            iid = item_entry.get("id") if isinstance(item_entry, dict) else item_entry
            assert reg.item(iid) is not None, f"item {iid} di {aid} harus ada di items.csv"


# 2. Item baru di items.csv
def test_items_csv_new_items(session):
    reg = session.reg
    talisman = reg.item("talisman_elemen")
    assert talisman is not None
    assert talisman["type"] == "weapon"
    assert int(talisman["power"]) > 0

    kontrak = reg.item("kontrak_roh")
    assert kontrak is not None
    assert kontrak["type"] == "weapon"
    assert int(kontrak["power"]) > 0

    pedang = reg.item("pedang_bambu")
    assert pedang is not None
    assert pedang["type"] == "weapon"


# 3. Pilih Elemen -> dapat talisman_elemen
def test_choose_elemen_grants_starter_kit(session):
    s = session
    s.state.current_quest = "q_akademi_04"
    res =    s.apply_action({"type": "choose", "option": "akademi_elemen"})
    assert s.state.player.academy == "akademi_elemen"
    assert s.state.inventory.get("talisman_elemen", 0) == 1
    assert any("talisman_elemen" in e["text"] or "Talisman" in e["text"] for e in s.state.log)
    # G2-T1: weapon starter terpasang otomatis ke slot weapon
    assert s.state.player.equipment["weapon"] == "talisman_elemen"


# 4. Pilih Senjata -> dapat pedang_bambu
def test_choose_senjata_grants_starter_kit(session):
    s = session
    s.state.current_quest = "q_akademi_04"
    res = s.apply_action({"type": "choose", "option": "akademi_senjata"})
    assert s.state.player.academy == "akademi_senjata"
    assert s.state.inventory.get("pedang_bambu", 0) == 1
    # G2-T1: weapon starter terpasang otomatis
    assert s.state.player.equipment["weapon"] == "pedang_bambu"


# 5. Pilih Summoning -> dapat kontrak_roh & kompanion
def test_choose_summoning_grants_starter_kit_and_companion(session):
    s = session
    s.state.current_quest = "q_akademi_04"
    res = s.apply_action({"type": "choose", "option": "akademi_summoning"})
    assert s.state.player.academy == "akademi_summoning"
    assert s.state.inventory.get("kontrak_roh", 0) == 1
    assert s.state.companion is not None
    assert s.state.companion["id"] == "komp_roh_awan"
    assert s.state.companion["active"] is True
    # G2-T1: weapon starter terpasang otomatis
    assert s.state.player.equipment["weapon"] == "kontrak_roh"


# 5b. (G2-T1) Auto-equip tidak menimpa slot yang sudah terisi & non-weapon tidak ter-equip
def test_auto_equip_tidak_menimpa_slot_terisi(session):
    s = session
    s.state.current_quest = "q_akademi_04"
    s.state.player.equipment["weapon"] = "pedang_bambu"  # slot sudah terisi
    s.apply_action({"type": "choose", "option": "akademi_elemen"})
    assert s.state.player.equipment["weapon"] == "pedang_bambu", "auto-equip tidak menimpa slot terisi"
    assert s.state.inventory.get("talisman_elemen", 0) == 1  # tetap masuk inventori


def test_auto_equip_non_weapon_tidak_dipasang(session):
    """Starter kit non-weapon (data arc lain) tidak boleh terpasang ke slot weapon."""
    s = session
    s.state.current_quest = "q_akademi_04"
    # starter kit sintetis non-weapon (mutasi data config, bukan kode)
    for a in s.reg.config["academies"]:
        if a["id"] == "akademi_elemen":
            a["starter_kit"] = [{"id": "pil_qi", "count": 1}]
    s.apply_action({"type": "choose", "option": "akademi_elemen"})
    assert s.state.player.equipment["weapon"] is None, "non-weapon tidak dipasang ke slot"
    assert s.state.inventory.get("pil_qi", 0) >= 1


# 6. Starter kit bertahan saat save/load tanpa duplikasi
def test_starter_kit_save_load_no_duplication(session, tmp_path):
    s = session
    s.state.current_quest = "q_akademi_04"
    s.apply_action({"type": "choose", "option": "akademi_elemen"})
    assert s.state.inventory.get("talisman_elemen") == 1

    # Save & reload
    save_data = s.state.to_dict()
    s2 = GameSession(s.reg, s.state.from_dict(save_data))
    assert s2.state.inventory.get("talisman_elemen") == 1
    assert s2.state.player.academy == "akademi_elemen"
    assert "q_akademi_04" in s2.state.completed_quests


# 7. Alur quest DAG: q04 -> q04b -> q05
def test_quest_dag_04_to_04b_to_05(session):
    s = session
    q04 = s.reg.quest("q_akademi_04")
    assert q04["next"][0]["quest"] == "q_akademi_04b"

    q04b = s.reg.quest("q_akademi_04b")
    assert q04b is not None
    assert q04b["title"] == "Pelajaran Pertama"
    assert q04b["objective"]["kind"] == "talk"
    assert q04b["objective"]["npc"] == "npc_gucanghai"
    assert q04b["next"][0]["quest"] == "q_akademi_05"


# 8. Dialog Gu Canghai mengajarkan teknik Elemen
def test_gucanghai_teaches_elemen_technique(session):
    s = session
    s.state.player.academy = "akademi_elemen"
    s.state.current_quest = "q_akademi_04b"
    s.state.location = "loc_aula_ujian"
    s.state.player.techniques = []

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert s.dialog.node_id == "node_pelajaran_elemen"
    finish_dialog(s, [0])

    assert "tek_elemen_bola_api" in s.state.player.techniques
    assert s.state.current_quest == "q_akademi_05"


# 9. Dialog Gu Canghai mengajarkan teknik Senjata
def test_gucanghai_teaches_senjata_technique(session):
    s = session
    s.state.player.academy = "akademi_senjata"
    s.state.current_quest = "q_akademi_04b"
    s.state.location = "loc_aula_ujian"
    s.state.player.techniques = []

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert s.dialog.node_id == "node_pelajaran_senjata"
    finish_dialog(s, [0])

    assert "tek_senjata_tebasan_angin" in s.state.player.techniques
    assert s.state.current_quest == "q_akademi_05"


# 10. Dialog Gu Canghai mengajarkan teknik Summoning
def test_gucanghai_teaches_summoning_technique(session):
    s = session
    s.state.player.academy = "akademi_summoning"
    s.state.current_quest = "q_akademi_04b"
    s.state.location = "loc_aula_ujian"
    s.state.player.techniques = []

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert s.dialog.node_id == "node_pelajaran_summoning"
    finish_dialog(s, [0])

    assert "tek_summoning_roh_api" in s.state.player.techniques
    assert s.state.current_quest == "q_akademi_05"


# 11. Pembelajaran berbiaya 0 emas & hanya via interaksi cerita
def test_learning_costs_zero_gold_and_story_only(session):
    s = session
    s.state.player.academy = "akademi_elemen"
    s.state.current_quest = "q_akademi_04b"
    s.state.location = "loc_aula_ujian"
    s.state.player.gold = 50
    s.state.player.techniques = []

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(s, [0])

    assert s.state.player.gold == 50
    assert "tek_elemen_bola_api" in s.state.player.techniques


# 12. Restriksi pertempuran: hanya teknik yang dikuasai
def test_combat_restraint_only_learned_techniques(session):
    s = session
    s.state.player.academy = "akademi_elemen"
    s.state.player.techniques = []  # Belum belajar teknik apapun
    foe = {"id": "eno_x", "name": "Musuh", "hp": 500, "qi": 0, "attack": 0, "defense": 0, "speed": 1}

    s.battle.start([foe], "hunt")
    qi_before = s.state.player.qi
    # Coba gunakan teknik kurikulum yang belum dipelajari
    s.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_bola_api"})
    assert s.state.pending_battle is not None
    assert s.state.player.qi == qi_before
    assert any("belum menguasai" in e["text"] for e in s.state.log)

    # Pelajari teknik
    s.state.player.techniques.append("tek_elemen_bola_api")
    s.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_bola_api"})
    assert s.state.player.qi < qi_before  # Qi terpotong dan teknik berhasil
    assert any("Bola Api" in e["text"] for e in s.state.log)

    # Teknik lain yang belum dipelajari tetap ditolak
    log_len = len(s.state.log)
    s.apply_action({"type": "battle_action", "action": "technique", "technique": "tek_elemen_perisai_tanah"})
    assert any("belum menguasai" in e["text"] for e in s.state.log[log_len:])
    assert not any("Perisai Tanah" in e["text"] for e in s.state.log[log_len:])
    s.state.pending_battle = None


# 13. DataRegistry.academy_curriculum
def test_loader_academy_curriculum_api(session):
    reg = session.reg
    curr_elemen = reg.academy_curriculum("akademi_elemen")
    assert len(curr_elemen) == 3
    assert [t["id"] for t in curr_elemen] == [
        "tek_elemen_bola_api",
        "tek_elemen_perisai_tanah",
        "tek_elemen_embun_air",
    ]

    curr_senjata = reg.academy_curriculum("akademi_senjata")
    assert [t["id"] for t in curr_senjata] == [
        "tek_senjata_tebasan_angin",
        "tek_senjata_serangan_ganda",
        "tek_senjata_kuda_kokoh",
    ]

    curr_summoning = reg.academy_curriculum("akademi_summoning")
    assert [t["id"] for t in curr_summoning] == [
        "tek_summoning_roh_api",
        "tek_summoning_roh_perisai",
        "tek_summoning_roh_penyembuh",
    ]

    assert reg.academy_curriculum("akademi_palsu") == []
    assert reg.academy_curriculum("") == []


# 14. Web context curriculum status: progression (learned, available, locked)
def test_web_context_curriculum_status_progression(session):
    import web.app as web_app
    web_app.session = session
    web_app.registry = session.reg

    s = session
    # 0. Sebelum memilih akademi -> kurikulum kosong
    s.state.player.academy = None
    ctx = web_app._context()
    assert ctx["curriculum"] == []

    # 1. Pilih paviliun elemen, belum belajar skill
    s.state.player.academy = "akademi_elemen"
    s.state.player.techniques = []
    ctx = web_app._context()
    curr = ctx["curriculum"]
    assert len(curr) == 3
    assert curr[0]["id"] == "tek_elemen_bola_api"
    assert curr[0]["status"] == "available"
    assert curr[1]["id"] == "tek_elemen_perisai_tanah"
    assert curr[1]["status"] == "locked"
    assert curr[2]["id"] == "tek_elemen_embun_air"
    assert curr[2]["status"] == "locked"

    # 2. Setelah mempelajari teknik pertama
    s.state.player.techniques = ["tek_elemen_bola_api"]
    ctx = web_app._context()
    curr = ctx["curriculum"]
    assert curr[0]["status"] == "learned"
    assert curr[1]["status"] == "available"
    assert curr[2]["status"] == "locked"

    # 3. Setelah mempelajari teknik kedua
    s.state.player.techniques = ["tek_elemen_bola_api", "tek_elemen_perisai_tanah"]
    ctx = web_app._context()
    curr = ctx["curriculum"]
    assert curr[0]["status"] == "learned"
    assert curr[1]["status"] == "learned"
    assert curr[2]["status"] == "available"

    # 4. Setelah mempelajari semua teknik
    s.state.player.techniques = ["tek_elemen_bola_api", "tek_elemen_perisai_tanah", "tek_elemen_embun_air"]
    ctx = web_app._context()
    curr = ctx["curriculum"]
    assert all(t["status"] == "learned" for t in curr)

    # 5. Jika ranah tidak mencukupi untuk skill berikutnya -> locked
    s.state.player.techniques = ["tek_elemen_bola_api"]
    # Dummy technique with higher realm requirement in curriculum
    fake_tek = {"id": "tek_elemen_perisai_tanah", "realm_required": "realm_pembangun_fondasi"}
    orig_tek = session.reg.techniques["tek_elemen_perisai_tanah"]
    session.reg.techniques["tek_elemen_perisai_tanah"] = {**orig_tek, **fake_tek}
    try:
        ctx = web_app._context()
        curr = ctx["curriculum"]
        assert curr[0]["status"] == "learned"
        assert curr[1]["status"] == "locked"  # locked karena ranah belum cukup
    finally:
        session.reg.techniques["tek_elemen_perisai_tanah"] = orig_tek


# 15. Kasus batas: Tetap belajar teknik saat kalah spar di q03 (spar_kalah = True)
def test_gucanghai_teaches_technique_when_spar_lost(session):
    s = session
    s.state.flags["spar_kalah"] = True
    s.state.player.academy = "akademi_elemen"
    s.state.current_quest = "q_akademi_04b"
    s.state.location = "loc_aula_ujian"
    s.state.player.techniques = []

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert s.dialog.node_id == "node_pelajaran_elemen"
    finish_dialog(s, [0])

    assert "tek_elemen_bola_api" in s.state.player.techniques
    assert s.state.current_quest == "q_akademi_05"


# 16. Kasus batas: Starter kit weapons dapat dipasang & memberi bonus serangan di pertempuran
@pytest.mark.parametrize("acad,item_id", [
    ("akademi_elemen", "talisman_elemen"),
    ("akademi_senjata", "pedang_bambu"),
    ("akademi_summoning", "kontrak_roh"),
])
def test_starter_kit_weapons_equip_and_combat_bonus(session, monkeypatch, acad, item_id):
    s = session
    s.state.current_quest = "q_akademi_04"
    s.apply_action({"type": "choose", "option": acad})
    assert s.state.inventory.get(item_id) == 1
    # G2-T1: senjata starter terpasang OTOMATIS (tidak perlu equip manual)
    assert s.state.player.equipment["weapon"] == item_id

    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # no crit

    # Serangan DENGAN senjata (attack 10): 10 damage (+3 peningkatan)
    foe1 = {"id": "eno_dummy1", "name": "Musuh Uji 1", "hp": 100, "hp_max": 100, "attack": 0, "defense": 0, "speed": 1}
    s.battle.start([foe1], "hunt")
    s.apply_action({"type": "battle_action", "action": "attack"})
    dmg_armed = 100 - s.state.pending_battle["foes"][0]["hp"]
    s.state.pending_battle = None

    # Lepas senjata → attack 7 (tanpa bonus)
    s.state.player.equipment["weapon"] = None
    foe2 = {"id": "eno_dummy2", "name": "Musuh Uji 2", "hp": 100, "hp_max": 100, "attack": 0, "defense": 0, "speed": 1}
    s.battle.start([foe2], "hunt")
    s.apply_action({"type": "battle_action", "action": "attack"})
    dmg_unarmed = 100 - s.state.pending_battle["foes"][0]["hp"]
    s.state.pending_battle = None

    assert dmg_armed - dmg_unarmed == 3  # tepat +3 bonus power dari starter weapon


# 17. Kasus batas: Meningkatkan teknik yang belum dikuasai ditolak
def test_unlearned_technique_upgrade_rejected(session):
    s = session
    s.state.location = "loc_asrama"  # safe point
    s.state.player.academy = "akademi_elemen"
    s.state.player.techniques = []
    s.state.player.gold = 100

    res = s.apply_action({"type": "upgrade_technique", "technique": "tek_elemen_bola_api"})
    assert s.state.player.gold == 100
    assert any("belum menguasai" in e["text"] for e in s.state.log)


# 18. Kasus batas: Validator data menolak kurikulum atau starter kit yang cacat
def test_validator_rejects_corrupted_curriculum_and_starter_kit():
    from tests.test_validator import _good, make

    # Kurikulum berisi teknik yang tidak terdaftar
    d1 = _good()
    d1["config.json"]["academies"] = [{
        "id": "akademi_test",
        "name": "Paviliun Test",
        "curriculum": ["tek_fiktif_tidak_ada"],
        "starter_kit": [],
    }]
    v1, ok1 = make(d1)
    assert not ok1
    assert any("curriculum teknik 'tek_fiktif_tidak_ada' tidak ada" in e for e in v1.errors)

    # Starter kit berisi item yang tidak terdaftar
    d2 = _good()
    d2["config.json"]["academies"] = [{
        "id": "akademi_test",
        "name": "Paviliun Test",
        "curriculum": [],
        "starter_kit": [{"id": "item_fiktif_tidak_ada"}],
    }]
    v2, ok2 = make(d2)
    assert not ok2
    assert any("starter_kit item 'item_fiktif_tidak_ada' tidak ada" in e for e in v2.errors)


# 19. Kasus batas: Starter kit dengan format string dan tipe invalid
def test_starter_kit_string_and_invalid_entry_formats(session):
    s = session
    fake_academies = [{
        "id": "akademi_format_test",
        "name": "Format Test",
        "starter_kit": ["pedang_bambu", {"id": "talisman_elemen", "count": 2}, 999, None],
    }]
    orig_academies = s.reg.config["academies"]
    s.reg.config["academies"] = fake_academies
    try:
        s.quest._grant_starter_kit("akademi_format_test")
        assert s.state.inventory.get("pedang_bambu") == 1
        assert s.state.inventory.get("talisman_elemen") == 2
    finally:
        s.reg.config["academies"] = orig_academies


# 20. Kasus batas: Pilihan opsi tidak valid pada choose action
def test_choose_invalid_option_rejected(session):
    s = session
    s.state.current_quest = "q_akademi_04"
    inv_before = dict(s.state.inventory)
    res = s.apply_action({"type": "choose", "option": "opsi_fiktif_tidak_ada"})
    assert s.state.player.academy is None
    assert s.state.current_quest == "q_akademi_04"
    assert s.state.inventory == inv_before
    assert any("Pilihan tidak valid" in e["text"] for e in s.state.log)


# 21. Kasus batas: player_techniques mendukung teknik lintas-arc yang terbuka (unlock_arc)
def test_player_techniques_unlock_arc_cross_academy(session):
    reg = session.reg
    # Tanpa completed final_quest arc akademi
    teks_before = reg.player_techniques("akademi_elemen", completed_quests=frozenset())
    assert all(not t.get("unlock_arc") for t in teks_before)

    # Tambahkan teknik dummy dengan unlock_arc
    dummy_arc_tek = {
        "id": "tek_arc_khusus",
        "name": "Teknik Arc Khusus",
        "academy": "senjata",
        "element": "logam",
        "realm_required": "realm_pengumpul_qi",
        "qi_cost": "10",
        "power": "25",
        "kind": "attack",
        "unlock_arc": "akademi",
    }
    reg.techniques["tek_arc_khusus"] = dummy_arc_tek
    try:
        # Saat arc akademi belum selesai (q_akademi_07 belum selesai) -> teknik belum terbuka
        teks_locked = reg.player_techniques("akademi_elemen", completed_quests=frozenset(["q_akademi_01"]))
        assert not any(t["id"] == "tek_arc_khusus" for t in teks_locked)

        # Saat arc akademi selesai (q_akademi_07 selesai) -> teknik lintas-arc otomatis terbuka
        teks_unlocked = reg.player_techniques("akademi_elemen", completed_quests=frozenset(["q_akademi_07"]))
        assert any(t["id"] == "tek_arc_khusus" for t in teks_unlocked)
    finally:
        reg.techniques.pop("tek_arc_khusus", None)


# 22. Kasus batas: Setelah q_akademi_04b selesai, dialog Gu Canghai tidak mengajarkan ulang
def test_dialog_gucanghai_after_q04b_does_not_reteach(session):
    s = session
    s.state.player.academy = "akademi_elemen"
    s.state.current_quest = "q_akademi_05"  # Quest berikutnya
    s.state.flags["ujian_akar_selesai"] = True
    s.state.location = "loc_aula_ujian"
    s.state.player.techniques = ["tek_elemen_bola_api"]

    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert s.dialog.node_id != "node_pelajaran_elemen"
    assert s.dialog.node_id in ("node_umum", "node_kalah", "node_akui_latihan")


# 23. Whole-system stress & integration test: alur lengkap q01-q05 + combat + save/load + upgrade di 3 akademi
@pytest.mark.parametrize("acad,item_id,tech_id,has_comp", [
    ("akademi_elemen", "talisman_elemen", "tek_elemen_bola_api", False),
    ("akademi_senjata", "pedang_bambu", "tek_senjata_tebasan_angin", False),
    ("akademi_summoning", "kontrak_roh", "tek_summoning_roh_api", True),
])
def test_comprehensive_3_academies_end_to_end_flow(tmp_path, monkeypatch, acad, item_id, tech_id, has_comp):
    from src.engine import session as session_mod
    from src.engine.battle import BattleEngine
    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, b: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)  # no crit

    reg = DataRegistry()
    s = GameSession.new(reg)

    # q01: Gerbang Akademi -> Penjaga
    s.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(s, [0])
    assert s.state.current_quest == "q_akademi_02"

    # q02: Aula Ujian -> Gu Canghai
    move_path(s, ["loc_aula_ujian"])
    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(s, [0])
    assert s.state.current_quest == "q_akademi_03"

    # q03: Arena -> Han Xiu (sparring)
    move_path(s, ["loc_arena"])
    s.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    finish_dialog(s, [])
    # Menangkan spar ujian
    if s.state.pending_battle:
        s.state.pending_battle["foes"][0]["hp"] = 0
        s.apply_action({"type": "battle_action", "action": "attack"})
    assert s.state.current_quest == "q_akademi_04"

    # q04: Pilih Akademi
    s.apply_action({"type": "choose", "option": acad})
    assert s.state.player.academy == acad
    assert s.state.inventory.get(item_id) == 1
    if has_comp:
        assert s.state.companion is not None
        assert s.state.companion["active"] is True
    assert s.state.current_quest == "q_akademi_04b"

    # Pasang senjata starter kit
    s.apply_action({"type": "equip", "item": item_id})
    assert s.state.player.equipment["weapon"] == item_id

    # q04b: Pelajaran Pertama -> Gu Canghai
    move_path(s, ["loc_aula_ujian"])
    s.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(s, [0])
    assert tech_id in s.state.player.techniques
    assert s.state.current_quest == "q_akademi_05"

    # Battle test dengan teknik baru di Lv.1
    foe1 = {"id": "eno_test1", "name": "Musuh Uji", "hp": 500, "hp_max": 500, "attack": 0, "defense": 0, "speed": 1}
    s.battle.start([foe1], "hunt")
    qi_before = s.state.player.qi
    s.apply_action({"type": "battle_action", "action": "technique", "technique": tech_id})
    dmg_lv1 = 500 - s.state.pending_battle["foes"][0]["hp"]
    assert s.state.player.qi < qi_before
    s.state.pending_battle = None

    # Simpan permainan di titik aman (loc_asrama)
    move_path(s, ["loc_asrama"])
    save_res = s.apply_action({"type": "save", "save_name": f"save_{acad}"})
    assert save_res.get("error") is None
    assert (tmp_path / f"save_{acad}.json").exists()

    # Load session dari file
    loaded = GameSession.load(reg, f"save_{acad}")
    assert loaded.state.player.academy == acad
    assert tech_id in loaded.state.player.techniques
    assert loaded.state.player.equipment["weapon"] == item_id
    assert loaded.state.inventory.get(item_id) == 1
    assert loaded.state.current_quest == "q_akademi_05"

    # Tingkatkan level teknik (Lv.1 -> Lv.2) di titik aman
    loaded.state.player.gold = 50
    upgrade_res = loaded.apply_action({"type": "upgrade_technique", "technique": tech_id})
    assert loaded.state.player.technique_levels.get(tech_id) == 2
    assert loaded.state.player.gold == 30  # 50 - 20

    # Battle test dengan teknik di Lv.2 -> damage harus lebih tinggi daripada Lv.1
    foe2 = {"id": "eno_test2", "name": "Musuh Uji 2", "hp": 500, "hp_max": 500, "attack": 0, "defense": 0, "speed": 1}
    loaded.battle.start([foe2], "hunt")
    loaded.apply_action({"type": "battle_action", "action": "technique", "technique": tech_id})
    dmg_lv2 = 500 - loaded.state.pending_battle["foes"][0]["hp"]
    loaded.state.pending_battle = None
    assert dmg_lv2 > dmg_lv1




