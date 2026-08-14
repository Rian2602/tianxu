"""Test dialog engine — entri kondisional, efek, pilihan cabang, gating side quest."""

from __future__ import annotations

from conftest import finish_dialog, move_path
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


def test_konfrontasi_pilihan_efek_beda(session, god_mode):
    """J3#6: opsi 'menuntut' (0) memberi morality +1; opsi 'diam' (1) tidak — hilangkan choice illusion."""
    from conftest import play_to_incident
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
    from conftest import play_to_incident
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
    from conftest import play_to_incident
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
    from conftest import play_to_incident

    play_to_incident(session)
    finish_dialog(session, [1])  # manfaatkan situasi → opt_3b
    assert session.state.current_quest == "q_akademi_3b"
    assert session.state.flags.get("jalur_3b") is True


def test_start_quest_hanya_jika_bisa_ditawarkan(session, god_mode):
    from conftest import play_to_incident

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
    from conftest import move_path, play_to_incident

    play_to_incident(session)
    finish_dialog(session, [1])  # tutup dialog insiden (cabang 3b)
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    finish_dialog(session, [0])  # "Aku bantu kumpulkan ramuannya." → start_quest
    assert "q_side_suqing" in session.state.active_side_quests, "side quest tidak aktif"

    # kumpulkan 3 herba → selesai (notify_gather dipicu lewat use_item)
    session.state.inventory["material_herba"] = 3
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert "q_side_suqing" not in session.state.active_side_quests
    assert "q_side_suqing" in session.state.completed_quests
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


