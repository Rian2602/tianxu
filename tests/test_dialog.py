"""Test dialog engine — entri kondisional, efek, pilihan cabang, gating side quest."""

from __future__ import annotations

from conftest import finish_dialog, move_path


def test_penjaga_dialog_flow(session):
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    v = session.dialog.view()
    assert v["speaker"] == "npc:npc_penjaga"
    assert len(v["choices"]) == 2
    finish_dialog(session, [0])
    assert session.state.current_quest == "q_akademi_02"
    assert session.state.flags.get("met_penjaga") is True


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

    # repeatable: bisa ditawarkan lagi setelah selesai
    assert session.quest.is_offerable("q_side_suqing") is True


def test_dialog_tidak_dikenal(session):
    s = session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    # Gu Canghai ada di aula, bukan gerbang → tidak bisa bicara dari sini
    assert s["mode"] == "explore"
