"""Test dialog engine — entri kondisional, efek, pilihan cabang, gating side quest."""

from __future__ import annotations

from tests.conftest import finish_dialog, move_path
from src.engine.dialog import DialogEngine


def test_dialog_condition_morality(dummy_session):
    dummy_session.state.player.morality = -50
    condition = {"morality_min": 10}
    result = DialogEngine._eval_condition(dummy_session.state, condition)
    assert result is False


def test_penjaga_dialog_flow(session):
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v = session.dialog.view()
    assert v["speaker"] == "npc:npc_penjaga"
    assert len(v["choices"]) == 2
    finish_dialog(session, [0])
    assert session.state.current_quest == "q_akademi_02"
    assert session.state.flags.get("met_penjaga") is True


def test_penjaga_dialog_kedua_berbeda(session):
    """Dialog ulang Penjaga berbeda dari perkenalan — entri kondisional `met_penjaga`:
    klik 1 = node_greet (perkenalan), klik 2 = node_ulang (menu topik)."""
    # klik 1 — perkenalan
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    assert session.dialog.view()["node_id"] == "node_greet"
    finish_dialog(session, [0])
    assert session.state.flags.get("met_penjaga") is True
    # klik 2 — menu ulang, bukan perkenalan lagi
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v = session.dialog.view()
    assert v["node_id"] == "node_ulang"
    labels = [c["label"] for c in v["choices"]]
    assert any("Akademi Changfeng" in l for l in labels)
    assert any("kabar" in l for l in labels)
    # tanya kabar → SEBELUM insiden: kabar umum, tanpa spoiler Lonceng
    session.apply_action({"type": "dialog_choice", "choice_index": 1})
    v = session.dialog.view()
    assert v["node_id"] == "node_ulang_kabar"
    assert "Lonceng" not in v["text"]
    session.apply_action({"type": "dialog_choice", "choice_index": -1})  # lanjut (node tanpa pilihan)
    assert session.dialog.view()["node_id"] == "node_ulang"
    # pergi → node penutup → advance → dialog selesai
    session.apply_action({"type": "dialog_choice", "choice_index": 2})
    assert session.dialog.view()["node_id"] == "node_ulang_pergi"
    session.apply_action({"type": "dialog_choice", "choice_index": -1})  # lanjut (end: true)
    assert session.state.pending_dialog is None


def test_penjaga_kabar_lonceng_setelah_insiden(session):
    """SETELAH insiden (flag lihat_moyun_malam) kabar Penjaga bicara Lonceng hilang."""
    session.state.flags["met_penjaga"] = True
    session.state.flags["lihat_moyun_malam"] = True  # q6 selesai → insiden terjadi
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v = session.dialog.view()
    assert v["node_id"] == "node_ulang"
    session.apply_action({"type": "dialog_choice", "choice_index": 1})
    v = session.dialog.view()
    assert v["node_id"] == "node_ulang_kabar_lonceng"
    assert "Lonceng Angin Panjang" in v["text"]
    session.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert session.dialog.view()["node_id"] == "node_ulang"
    session.apply_action({"type": "dialog_choice", "choice_index": 2})  # pergi
    session.apply_action({"type": "dialog_choice", "choice_index": -1})  # end
    assert session.state.pending_dialog is None


def test_konfrontasi_pilihan_efek_beda(session, god_mode):
    """J3#6: opsi 'menuntut' (0) memberi morality +1; opsi 'diam' (1) tidak — hilangkan choice illusion."""
    from tests.conftest import play_to_incident
    from src.engine.session import GameSession

    def morality_delta(idx):
        s = GameSession.new(session.reg)
        play_to_incident(s)
        finish_dialog(s, [0, 0])  # opt_3aa
        move_path(s, ["loc_perpustakaan", "loc_paviliun"])
        # bicara pertama: branch_3aa belum set → node_umum (selesaikan q_akademi_3aa)
        s.apply_action({"type": "talk", "npc": "npc_penatua"})
        finish_dialog(s, [])
        # bicara kedua: branch_3aa sudah set → node_konfrontasi
        s.apply_action({"type": "talk", "npc": "npc_penatua"})
        m0 = s.state.player.morality
        s.apply_action({"type": "dialog_choice", "choice_index": idx})
        return s.state.player.morality - m0

    assert morality_delta(0) == 1  # menuntut jawaban → moralitas naik
    assert morality_delta(1) == 0  # menahan amarah → netral


def test_reaksi_3ab(session, god_mode):
    """G4c: cabang 3ab mendapat reaksi khusus (Su Qing hangat, Han Xiu respect, Zhou Yan bersyukur)."""
    from tests.conftest import play_to_incident
    from src.engine.session import GameSession

    s = GameSession.new(session.reg)
    play_to_incident(s)
    finish_dialog(s, [0, 1])  # opt_3ab
    move_path(s, ["loc_perpustakaan"])
    s.apply_action({"type": "talk", "npc": "npc_moyun"})  # selesaikan q_akademi_3ab
    finish_dialog(s, [])
    s.apply_action({"type": "talk", "npc": "npc_moyun"})  # q07 — kebenaran
    finish_dialog(s, [])
    assert "q_akademi_07" in s.state.completed_quests
    assert s.state.flags.get("zhouyan_status") == "bebas"

    # Su Qing (paviliun) → hangat 3ab
    s.apply_action({"type": "move", "to": "loc_paviliun"})
    s.apply_action({"type": "talk", "npc": "npc_suqing"})
    assert "tanpa membuat gaduh" in s.dialog.view()["text"]
    finish_dialog(s, [])
    # Han Xiu (arena) → respect 3ab
    s.apply_action({"type": "move", "to": "loc_aula_ujian"})
    s.apply_action({"type": "move", "to": "loc_arena"})
    s.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    assert "kepala dingin" in s.dialog.view()["text"]
    finish_dialog(s, [])
    # Zhou Yan (aula ujian) → bersyukur 3ab
    s.apply_action({"type": "move", "to": "loc_aula_ujian"})
    s.apply_action({"type": "talk", "npc": "npc_zhouyan"})
    assert "diam-diam" in s.dialog.view()["text"]


def test_entri_kondisional_suqing(session, god_mode):
    # sebelum hari pertama selesai → entri intro (gerbang → aula → paviliun)
    move_path(session, ["loc_aula_ujian", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    assert "Su Qing" in session.dialog.view()["text"] or "teman sekelas" in session.dialog.view()["text"]

    # selesaikan sampai cabang 3b → Su Qing kecewa
    from tests.conftest import play_to_incident
    from src.engine.session import GameSession

    s = GameSession.new(session.reg)
    play_to_incident(s)
    finish_dialog(s, [1])  # ambil keuntungan
    # ruang_lonceng → perpustakaan → paviliun → aula ujian
    move_path(s, ["loc_perpustakaan", "loc_paviliun", "loc_aula_ujian"])
    s.apply_action({"type": "talk", "npc": "npc_zhouyan"})
    finish_dialog(s, [0])
    # pindah ke paviliun & bicara Su Qing → entri kecewa
    s.apply_action({"type": "move", "to": "loc_paviliun"})
    s.apply_action({"type": "talk", "npc": "npc_suqing"})
    text = s.dialog.view()["text"]
    assert "berbeda" in text or "kecewa" in text


def test_efek_pilihan_dialog(session):
    # q1: pilihan "Diam saja" (index 1) — tetap lanjut, quest selesai
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(session, [1])
    assert session.state.current_quest == "q_akademi_02"


def test_branch_option_dipilih(session, god_mode):
    from tests.conftest import play_to_incident

    play_to_incident(session)
    finish_dialog(session, [1])  # manfaatkan situasi → opt_3b
    assert session.state.current_quest == "q_akademi_3b"
    assert session.state.flags.get("jalur_3b") is True


def test_start_quest_hanya_jika_bisa_ditawarkan(session, god_mode):
    from tests.conftest import play_to_incident

    play_to_incident(session)
    # side quest tersedia sejak hari 1 (available_from day 1 hour 8) → opsi muncul
    finish_dialog(session, [1])
    # ruang_lonceng → perpustakaan → paviliun
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert any("ramuan" in l for l in labels), f"opsi side quest tidak muncul: {labels}"
    # terima tawaran → side quest aktif → tidak ditawarkan lagi
    session.apply_action({"type": "dialog_choice", "choice_index": 0})
    assert "q_side_suqing" in session.state.active_side_quests
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert not any("ramuan" in l for l in labels), f"side quest ditawarkan lagi: {labels}"


def test_side_quest_dimulai_dan_selesai(session, god_mode):
    """Efek start_quest benar-benar mengaktifkan side quest; lalu bisa selesai & diulang."""
    from tests.conftest import move_path, play_to_incident

    play_to_incident(session)
    finish_dialog(session, [1])  # tutup dialog insiden (cabang 3b)
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    finish_dialog(session, [0])  # "Aku bantu kumpulkan ramuannya." → start_quest
    assert "q_side_suqing" in session.state.active_side_quests, "side quest tidak aktif"

    # kumpulkan 3 herba → BELUM selesai (report_to: harus lapor ke Su Qing)
    session.state.inventory["material_herba"] = 3
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert "q_side_suqing" in session.state.active_side_quests, "kumpul saja belum menyelesaikan (report_to)"

    # bicara ke Su Qing → node lapor → serah → quest selesai + herba diambil
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    v = session.dialog.view()
    assert v["node_id"] == "node_lapor_suqing"
    finish_dialog(session, [0])  # "Ini, tiga ikat Herba Awan."
    assert "q_side_suqing" not in session.state.active_side_quests
    assert "q_side_suqing" in session.state.completed_quests
    assert session.state.inventory.get("material_herba", 0) == 0  # herba diambil
    assert session.state.player.gold >= 30  # reward +10

    # repeatable: tidak bisa ditawarkan sebelum cooldown
    assert session.quest.is_offerable("q_side_suqing") is False

    # repeatable: bisa ditawarkan lagi setelah selesai (cooldown 2 jam)
    session.apply_action({"type": "advance_time", "hours": 2})
    assert session.quest.is_offerable("q_side_suqing") is True


def test_dialog_tidak_dikenal(session):
    s = session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    # Gu Canghai ada di aula, bukan gerbang → tidak bisa bicara dari sini
    assert s["mode"] == "explore"


def test_eval_condition_flag(dummy_session):
    state = dummy_session.state
    # flag belum diset (default False)
    assert DialogEngine._eval_condition(state, {"flag": {"key": "sudah_kenal", "value": True}}) is False
    assert DialogEngine._eval_condition(state, {"flag": {"key": "sudah_kenal", "value": False}}) is True
    # flag diset True
    state.flags["sudah_kenal"] = True
    assert DialogEngine._eval_condition(state, {"flag": {"key": "sudah_kenal", "value": True}}) is True
    assert DialogEngine._eval_condition(state, {"flag": {"key": "sudah_kenal", "value": False}}) is False
    # flag tanpa spesifikasi value eksplisit (default True)
    assert DialogEngine._eval_condition(state, {"flag": {"key": "sudah_kenal"}}) is True


def test_eval_condition_morality_max(dummy_session):
    state = dummy_session.state
    state.player.morality = 20
    assert DialogEngine._eval_condition(state, {"morality_max": 10}) is False
    assert DialogEngine._eval_condition(state, {"morality_max": 20}) is True
    assert DialogEngine._eval_condition(state, {"morality_max": 30}) is True


def test_eval_condition_has_item(dummy_session):
    state = dummy_session.state
    state.inventory.clear()
    assert DialogEngine._eval_condition(state, {"has_item": "pil_qi"}) is False
    state.inventory["pil_qi"] = 0
    assert DialogEngine._eval_condition(state, {"has_item": "pil_qi"}) is False
    state.inventory["pil_qi"] = 2
    assert DialogEngine._eval_condition(state, {"has_item": "pil_qi"}) is True


def test_eval_condition_realm_min(dummy_session, registry):
    state = dummy_session.state
    # tanpa registry -> False
    assert DialogEngine._eval_condition(state, {"realm_min": "realm_pembangun_fondasi"}, None) is False

    # dengan registry
    state.player.realm = "realm_pengumpul_qi"  # order 1
    assert DialogEngine._eval_condition(state, {"realm_min": "realm_pembangun_fondasi"}, registry) is False
    assert DialogEngine._eval_condition(state, {"realm_min": "realm_pengumpul_qi"}, registry) is True

    state.player.realm = "realm_pembentuk_inti"  # order 3
    assert DialogEngine._eval_condition(state, {"realm_min": "realm_pembangun_fondasi"}, registry) is True


def test_eval_condition_academy(dummy_session):
    state = dummy_session.state
    state.player.academy = "akademi_elemen"
    assert DialogEngine._eval_condition(state, {"academy": "akademi_senjata"}) is False
    assert DialogEngine._eval_condition(state, {"academy": "akademi_elemen"}) is True


def test_eval_condition_quest_active(dummy_session):
    state = dummy_session.state
    state.current_quest = "q_akademi_01"
    state.active_side_quests = {"q_side_suqing": {}}

    # quest utama aktif -> True
    assert DialogEngine._eval_condition(state, {"quest_active": "q_akademi_01"}) is True
    # side quest aktif -> True
    assert DialogEngine._eval_condition(state, {"quest_active": "q_side_suqing"}) is True
    # quest lain tidak aktif -> False
    assert DialogEngine._eval_condition(state, {"quest_active": "q_akademi_02"}) is False


def test_eval_condition_quest_not_active(dummy_session):
    state = dummy_session.state
    state.current_quest = "q_akademi_01"
    state.active_side_quests = {"q_side_suqing": {}}

    # quest utama aktif -> False
    assert DialogEngine._eval_condition(state, {"quest_not_active": "q_akademi_01"}) is False
    # side quest aktif -> False
    assert DialogEngine._eval_condition(state, {"quest_not_active": "q_side_suqing"}) is False
    # quest lain tidak aktif -> True
    assert DialogEngine._eval_condition(state, {"quest_not_active": "q_akademi_02"}) is True


def test_dialog_engine_start_invalid(session):
    # dialog tidak ada di registry
    res = session.dialog.start("dialog_ngawur_tidak_ada")
    assert res is None


def test_dialog_engine_choose_edge_cases(session):
    # choose saat dialog belum start
    session.dialog.current = None
    session.dialog.node_id = None
    assert session.dialog.choose(0) is None

    # start dialog valid
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v = session.dialog.view()
    assert v is not None

    # index negatif atau di luar range choices -> mengembalikan view tanpa error
    assert session.dialog.choose(-1) is not None
    assert session.dialog.choose(99) is not None


def test_dialog_engine_advance_edge_cases(session):
    # advance saat belum start
    session.dialog.current = None
    session.dialog.node_id = None
    assert session.dialog.advance() is None

    # start dialog yang punya choices di node awal -> advance mengembalikan view
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v_before = session.dialog.view()
    v_adv = session.dialog.advance()
    assert v_adv["node_id"] == v_before["node_id"]

    # buat mock dialog node tanpa choices
    session.dialog.current = {
        "id": "dlg_mock",
        "nodes": {
            "node_1": {"speaker": "narrator", "text": "Langkah 1", "next": "node_2"},
            "node_2": {"speaker": "narrator", "text": "Langkah 2"},
        }
    }
    session.dialog.node_id = "node_1"
    v2 = session.dialog.advance()
    assert v2["node_id"] == "node_2"

    # node_2 tidak punya next -> advance mengakhiri dialog
    res = session.dialog.advance()
    assert res == {"ended": True}
    assert session.dialog.current is None
    assert session.dialog.node_id is None


def test_dialog_engine_visible_choices_conditions(session):
    session.dialog.current = {
        "id": "dlg_mock_choices",
        "nodes": {
            "start": {
                "speaker": "narrator",
                "text": "Pilih jalanmu",
                "choices": [
                    {"label": "Opsi Moral Tinggi", "condition": {"morality_min": 50}},
                    {"label": "Opsi Selalu Ada"},
                    {"label": "Opsi Quest Tidak Offerable", "effects": [{"type": "start_quest", "quest": "q_side_suqing"}]},
                ]
            }
        }
    }
    session.dialog.node_id = "start"
    session.state.player.morality = 0
    # buat quest tidak offerable dengan memasukkannya ke active_side_quests
    session.state.active_side_quests["q_side_suqing"] = {}
    v = session.dialog.view()
    # Opsi moral tinggi dan quest tidak offerable disembunyikan
    assert len(v["choices"]) == 1
    assert v["choices"][0]["label"] == "Opsi Selalu Ada"

    # Setelah moral naik dan quest offerable (dihapus dari active), semua muncul
    session.state.player.morality = 60
    del session.state.active_side_quests["q_side_suqing"]
    v2 = session.dialog.view()
    assert len(v2["choices"]) == 3


def test_eval_condition_relation(dummy_session):
    """P1-2: kondisi relation_min/relation_max dibaca dari state.relations."""
    state = dummy_session.state
    # relations kosong (default 0)
    assert DialogEngine._eval_condition(state, {"relation_min": {"npc": "npc_hanxiu", "value": 10}}) is False
    assert DialogEngine._eval_condition(state, {"relation_max": {"npc": "npc_hanxiu", "value": 10}}) is True
    # npc lain (0) tidak terpengaruh skor npc target
    state.relations["npc_hanxiu"] = 25
    assert DialogEngine._eval_condition(state, {"relation_min": {"npc": "npc_hanxiu", "value": 20}}) is True
    assert DialogEngine._eval_condition(state, {"relation_min": {"npc": "npc_hanxiu", "value": 25}}) is True
    assert DialogEngine._eval_condition(state, {"relation_min": {"npc": "npc_hanxiu", "value": 26}}) is False
    assert DialogEngine._eval_condition(state, {"relation_max": {"npc": "npc_hanxiu", "value": 20}}) is False
    assert DialogEngine._eval_condition(state, {"relation_min": {"npc": "npc_suqing", "value": 1}}) is False


def test_pilihan_gated_relation(session):
    """P1-2: choice ber-condition relation_min tersembunyi lalu tampil setelah relation naik."""
    session.dialog.current = {
        "id": "dlg_mock_rel",
        "nodes": {
            "start": {
                "speaker": "narrator",
                "text": "Han Xiu menatapmu.",
                "choices": [
                    {"label": "Tip Sparring Rahasia", "condition": {"relation_min": {"npc": "npc_hanxiu", "value": 20}}},
                    {"label": "Basa-basi"},
                ]
            }
        }
    }
    session.dialog.node_id = "start"
    # relation 0 → opsi gated tersembunyi
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert labels == ["Basa-basi"]
    # spar menang berulang → relation naik → opsi muncul
    session.state.relations["npc_hanxiu"] = 20
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert "Tip Sparring Rahasia" in labels


def test_spar_menang_menaikkan_relation(session, monkeypatch):
    """P1-2: kemenangan spar menyuntikkan relation ke NPC lawan (cultivation.spar_win_relation)."""
    # serangan pemain 1-hit menang; serangan musuh (Han Xiu speed 11 > pemain) 0 damage
    from src.engine.battle import BattleEngine as BE
    monkeypatch.setattr(BE, "_calc_damage", lambda self, a, d, ea, ed: ((0, False) if ed is None else (99999, False)))
    session.state.location = "loc_arena"
    session.state.flags["spar_ujian_selesai"] = True  # syarat spar manual Han Xiu
    session.apply_action({"type": "spar", "npc": "npc_hanxiu"})
    assert session.state.pending_battle is not None
    rel_before = session.state.relations.get("npc_hanxiu", 0)
    # selesaikan battle — serang sampai menang
    for _ in range(20):
        session.apply_action({"type": "battle_action", "action": "attack"})
        if session.state.pending_battle is None:
            break
    assert session.state.pending_battle is None
    rel_after = session.state.relations.get("npc_hanxiu", 0)
    assert rel_after >= rel_before + 1, f"relation tidak naik: {rel_before} → {rel_after}"


def test_hanxiu_tip_spar_saat_relation_tinggi(session, god_mode):
    """P1-2: hubungan tinggi dengan Han Xiu (sparring berulang) membuka node tip spar."""
    from tests.conftest import move_path

    session.state.flags["spar_ujian_selesai"] = True
    move_path(session, ["loc_aula_ujian", "loc_arena"])
    # relation rendah → tetap node banter biasa
    session.state.relations["npc_hanxiu"] = 5
    session.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    assert "Masih hidup" in session.dialog.view()["text"]
    finish_dialog(session, [])
    # relation tinggi (sparring berulang) → node tip spar
    session.state.relations["npc_hanxiu"] = 20
    session.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    assert "ritme" in session.dialog.view()["text"]


def test_gucanghai_akui_latihan_saat_relation_tinggi(session, god_mode):
    """P1-2: hubungan tinggi dengan Gu Canghai membuka node pengakuan ketekunan."""
    from tests.conftest import move_path

    session.state.flags["ujian_akar_selesai"] = True
    move_path(session, ["loc_aula_ujian"])
    # relation rendah → nasihat biasa tetap tersedia
    session.state.relations["npc_gucanghai"] = 0
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert "Kultivasi itu seperti laut" in session.dialog.view()["text"]
    finish_dialog(session, [0])
    # relation tinggi (sering sparring) → node pengakuan ketekunan
    session.state.relations["npc_gucanghai"] = 20
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert "Ketekunan" in session.dialog.view()["text"]


def test_eval_condition_memory(dummy_session):
    """P1-1: kondisi memory true hanya setelah id ingatan ada di state.memories."""
    state = dummy_session.state
    assert DialogEngine._eval_condition(state, {"memory": "mem_01"}) is False
    state.memories.append("mem_01")
    assert DialogEngine._eval_condition(state, {"memory": "mem_01"}) is True
    assert DialogEngine._eval_condition(state, {"memory": "mem_02"}) is False


def test_pilihan_gated_memory(session):
    """P1-1: choice ber-condition memory tersembunyi sebelum ingatan pulih."""
    session.dialog.current = {
        "id": "dlg_mock_mem",
        "nodes": {
            "start": {
                "speaker": "narrator",
                "text": "Sesuatu berdenyut di dadamu.",
                "choices": [
                    {"label": "Pengembara itu...", "condition": {"memory": "mem_02"}, "next": "node_dalam"},
                    {"label": "Lanjut"},
                ]
            },
            "node_dalam": {"speaker": "narrator", "text": "Kau ingat jubah yang kau berikan."},
        }
    }
    session.dialog.node_id = "start"
    # ingatan belum pulih → hanya "Lanjut"
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert labels == ["Lanjut"]
    # ingatan pulih → pilihan mendalam muncul
    session.state.memories.append("mem_02")
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert "Pengembara itu..." in labels


def test_moyun_pilihan_ingatan_muncul_saat_q07(session, god_mode):
    """P1-1: di q07, pilihan terkait mem_02 muncul di node_penutup setelah ingatan pulih (3aa)."""
    from tests.conftest import play_to_incident
    from src.engine.session import GameSession

    s = GameSession.new(session.reg)
    play_to_incident(s)
    finish_dialog(s, [0, 0])  # opt_3aa
    move_path(s, ["loc_perpustakaan", "loc_paviliun"])
    s.apply_action({"type": "talk", "npc": "npc_penatua"})  # selesaikan q_akademi_3aa (mem_02 terbuka)
    finish_dialog(s, [])
    assert "mem_02" in s.state.memories
    # q07: bicara Mo Yun → truth → penutup
    s.apply_action({"type": "move", "to": "loc_perpustakaan"})
    s.apply_action({"type": "talk", "npc": "npc_moyun"})  # node_truth_3aa (tanpa pilihan)
    s.apply_action({"type": "dialog_choice", "choice_index": -1})  # lanjut → node_penutup
    # penutup kini punya pilihan terkait ingatan (mem_02 sudah pulih)
    labels = [c["label"] for c in s.dialog.view()["choices"]]
    assert any("pengembara" in l for l in labels), f"opsi ingatan tidak muncul: {labels}"
    # pilih opsi ingatan → node_moyun_memori
    s.apply_action({"type": "dialog_choice", "choice_index": 0})
    assert "pengembara" in s.dialog.view()["text"]
    finish_dialog(s, [])


def test_gucanghai_pilihan_ingatan_muncul(session, god_mode):
    """P1-1: node_umum Gu Canghai menampilkan pilihan duka tua hanya setelah mem_01 pulih."""
    from tests.conftest import move_path

    move_path(session, ["loc_aula_ujian"])
    # tanpa mem_01 → hanya 2 pilihan nasihat
    session.state.flags["ujian_akar_selesai"] = True
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert len(labels) == 2
    finish_dialog(session, [0])
    # mem_01 pulih → pilihan ketiga muncul
    session.state.memories.append("mem_01")
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    labels = [c["label"] for c in session.dialog.view()["choices"]]
    assert len(labels) == 3


def test_eval_condition_flag_tidak_mengabaikan_kondisi_lain(session):
    """C3: kombinasi `flag` + kondisi lain harus AND — flag TIDAK boleh early-return
    (bug laten yang diekspos ending: morality_min + flag hanya cek flag)."""
    from src.engine.dialog import DialogEngine
    s = session.state
    cond = {"morality_min": 30, "flag": {"key": "kunci_x", "value": True}}
    # kasus 1: flag benar tapi moralitas rendah → harus False (AND)
    s.player.morality = -50
    s.flags["kunci_x"] = True
    assert DialogEngine._eval_condition(s, cond, session.reg) is False
    # kasus 2: moralitas cukup tapi flag salah → harus False (AND)
    s.player.morality = 50
    s.flags["kunci_x"] = False
    assert DialogEngine._eval_condition(s, cond, session.reg) is False
    # kasus 3: keduanya terpenuhi → True
    s.player.morality = 50
    s.flags["kunci_x"] = True
    assert DialogEngine._eval_condition(s, cond, session.reg) is True


def test_eval_condition_month_min_max(session):
    """C2: kondisi dialog month_min/max menyaring opsi berdasarkan bulan (derived)."""
    from src.engine.dialog import DialogEngine
    s = session.state
    s.day = 40  # month_length 30 → Bulan 2
    # di dalam rentang → True; di luar → False
    assert DialogEngine._eval_condition(s, {"month_min": 2, "month_max": 3}, session.reg) is True
    assert DialogEngine._eval_condition(s, {"month_min": 3}, session.reg) is False
    assert DialogEngine._eval_condition(s, {"month_max": 1}, session.reg) is False
    # kombinasi AND dengan kondisi lain
    s.player.morality = 50
    assert DialogEngine._eval_condition(s, {"month_min": 2, "morality_min": 40}, session.reg) is True
    assert DialogEngine._eval_condition(s, {"month_min": 2, "morality_min": 60}, session.reg) is False


def test_dialog_engine_choose_no_next_ends(session):
    session.dialog.current = {
        "id": "dlg_mock_end",
        "nodes": {
            "start": {
                "speaker": "narrator",
                "text": "Pilihan Terakhir",
                "choices": [
                    {"label": "Selesai", "option": "opt_selesai"},
                ]
            }
        }
    }
    session.dialog.node_id = "start"
    res = session.dialog.choose(0)
    assert res == {"ended": True}
    assert session.dialog.current is None
    assert session.dialog.chosen_option == "opt_selesai"


def test_dialog_start_node_dipaksa(session):
    """A3: `start(forced_node)` memaksa dialog mulai dari node itu (bukan `start`)."""
    dlg = session.dialog.start("dlg_penatua", forced_node="node_konfrontasi")
    assert dlg["node_id"] == "node_konfrontasi"
    assert dlg["speaker"] == "npc:npc_penatua"
    # tanpa forced → node default (start)
    dlg2 = session.dialog.start("dlg_penatua")
    assert dlg2["node_id"] == "node_umum"
    # forced node yang tidak ada → fallback start (tidak crash)
    dlg3 = session.dialog.start("dlg_penatua", forced_node="node_tidak_ada")
    assert dlg3["node_id"] == "node_umum"
    session.state.pending_dialog = None


def test_quest_talk_node_wajib(session, monkeypatch):
    """A3: objective talk dengan `node` wajib — quest selesai HANYA bila node
    wajib dimainkan; node lain → belum selesai."""
    qe = session.quest
    state = session.state
    state.current_quest = "q_synth_talk_node"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_talk_node", "title": "Talk Node Synth", "kind": "main",
            "objective": {"kind": "talk", "npc": "npc_penatua", "node": "node_konfrontasi", "target": 1},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    # node salah (node_umum) → quest TIDAK selesai
    qe.notify_dialog_ended("npc_penatua", "node_umum")
    assert state.current_quest == "q_synth_talk_node"
    # node benar (node_konfrontasi) → quest selesai
    qe.notify_dialog_ended("npc_penatua", "node_konfrontasi")
    assert "q_synth_talk_node" in state.completed_quests


def test_quest_talk_tanpa_node_perilaku_lama(session, monkeypatch):
    """A3: objective talk TANPA `node` — perilaku lama (asalkan NPC benar), non-breaking."""
    qe = session.quest
    state = session.state
    state.current_quest = "q_synth_talk_lama"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_talk_lama", "title": "Talk Lama", "kind": "main",
            "objective": {"kind": "talk", "npc": "npc_penatua", "target": 1},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    qe.notify_dialog_ended("npc_penatua", "node_umum")
    assert "q_synth_talk_lama" in state.completed_quests


def test_3aa_konfrontasi_saat_quest_aktif(session, god_mode):
    """A2+A3: saat q_akademi_3aa aktif, bicara Penatua langsung membuka
    node_konfrontasi (bukan node_umum) — urutan naratif cabang benar."""
    from tests.conftest import play_to_incident

    play_to_incident(session)
    finish_dialog(session, [0, 0])  # membongkar → konfrontasi langsung = opt_3aa
    assert session.state.current_quest == "q_akademi_3aa"
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_penatua"})
    v = session.dialog.view()
    assert v["node_id"] == "node_konfrontasi"  # bukan node_umum
    finish_dialog(session, [0])  # selesaikan konfrontasi
    assert session.state.current_quest == "q_akademi_07" or "q_akademi_3aa" in session.state.completed_quests
    assert session.state.flags.get("branch_3aa") is True


def test_suqing_intro_friendly_choice_relation(session):
    """Pilihan ramah saat perkenalan Su Qing memberi efek relation +5."""
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "move", "to": "loc_paviliun"})
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    assert session.state.pending_dialog is not None
    assert session.state.relations.get("npc_suqing", 0) == 0
    # Pilih opsi ramah (indeks 0: "Aku Chen Xu. Senang bertemu, Su Qing.")
    session.apply_action({"type": "dialog_choice", "choice_index": 0})
    assert session.state.relations.get("npc_suqing") == 5


def test_suqing_dialog_memory_branch(session):
    """Cabang dialog ingatan (mem_01) pada Su Qing hanya muncul saat ingatan terbuka."""
    from tests.conftest import finish_dialog
    session.state.flags["hari_pertama_selesai"] = True
    session.state.location = "loc_paviliun"
    # Tanpa ingatan mem_01
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert not any("istana" in l.lower() for l in labels)
    finish_dialog(session, [1])

    # Dengan ingatan mem_01
    session.state.memories.append("mem_01")
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    v = session.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert any("istana" in l.lower() for l in labels)
    # Pilih cabang ingatan
    mem_idx = next(i for i, c in enumerate(v["choices"]) if "istana" in c["label"].lower())
    session.apply_action({"type": "dialog_choice", "choice_index": mem_idx})
    v2 = session.dialog.view()
    assert "istana yang megah" in v2["text"].lower() or "berbahaya" in v2["text"].lower()


def test_q05_requires_specific_node(session):
    """q_akademi_05 membutuhkan node_intro2 untuk selesai."""
    session.state.current_quest = "q_akademi_05"
    # Dialog Su Qing berakhir di node selain node_intro2 (misal node_umum) -> belum selesai
    session.quest.notify_dialog_ended("npc_suqing", "node_umum")
    assert session.state.current_quest == "q_akademi_05"
    assert "q_akademi_05" not in session.state.completed_quests

    # Dialog mencapai node_intro2 -> quest selesai
    session.quest.notify_dialog_ended("npc_suqing", ["node_intro", "node_intro2"])
    assert "q_akademi_05" in session.state.completed_quests


