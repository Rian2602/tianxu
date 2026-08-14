"""Test quest engine DAG — satu-aktif, percabangan, konvergensi (DoD GDD §11.2)."""

from __future__ import annotations

from src.engine.session import GameSession

from conftest import finish_dialog, move_path, play_to_incident  # noqa: F401



def _assert_arc_done(session: GameSession) -> None:
    assert session.state.flags.get("arc_akademi_selesai") is True
    assert session.state.current_quest is None
    assert "q_akademi_07" in session.state.completed_quests


def _finish_truth(session: GameSession) -> None:
    """Selesaikan arc: bicara Mo Yun sampai kebenaran (q_akademi_07) tercapai.

    Di cabang 3ab, pengakuan Mo Yun menyelesaikan quest bukti lebih dulu,
    lalu percakapan kedua mengungkap kebenaran.
    """
    if session.state.location == "loc_aula_ujian":
        move_path(session, ["loc_paviliun", "loc_perpustakaan"])
    else:
        session.apply_action({"type": "move", "to": "loc_perpustakaan"})
    guard = 0
    while "q_akademi_07" not in session.state.completed_quests and guard < 10:
        guard += 1
        session.apply_action({"type": "talk", "npc": "npc_moyun"})
        finish_dialog(session, [])


def test_branch_3aa_konfrontasi(session, god_mode):
    play_to_incident(session)
    # pilih: membongkar (0) → konfrontasi langsung (0) = opt_3aa
    finish_dialog(session, [0, 0])
    assert session.state.flags.get("jalur_3a") is True
    assert session.state.current_quest == "q_akademi_3aa"

    # ruang_lonceng → perpustakaan → paviliun
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_penatua"})
    finish_dialog(session, [0])

    _finish_truth(session)
    _assert_arc_done(session)
    assert "mem_01" in session.state.memories
    assert "mem_02" in session.state.memories
    assert session.state.flags.get("branch_3aa") is True
    assert session.state.player.morality >= 5


def test_branch_3ab_diam_diam(session, god_mode):
    play_to_incident(session)
    finish_dialog(session, [0, 1])  # membongkar (0) → kumpulkan bukti (1) = opt_3ab
    assert session.state.current_quest == "q_akademi_3ab"

    _finish_truth(session)  # talk Mo Yun: pengakuan lalu kebenaran
    _assert_arc_done(session)
    assert "mem_02" in session.state.memories
    assert session.state.flags.get("branch_3ab") is True


def test_branch_3b_ambil_keuntungan(session, god_mode):
    play_to_incident(session)
    finish_dialog(session, [1])  # manfaatkan situasi = opt_3b
    assert session.state.current_quest == "q_akademi_3b"

    # ruang_lonceng → perpustakaan → paviliun → aula ujian
    move_path(session, ["loc_perpustakaan", "loc_paviliun", "loc_aula_ujian"])
    session.apply_action({"type": "talk", "npc": "npc_zhouyan"})
    finish_dialog(session, [0])

    _finish_truth(session)
    _assert_arc_done(session)
    assert "mem_03" in session.state.memories
    assert session.state.flags.get("branch_3b") is True
    assert session.state.player.morality < 0
    assert session.state.player.gold >= 30  # keuntungan


def test_branch_3c_berdiam_diri(session, god_mode):
    play_to_incident(session)
    finish_dialog(session, [2])  # berdiam diri = opt_3c
    assert session.state.current_quest == "q_akademi_3c"

    session.apply_action({"type": "advance_time", "hours": 24})  # biarkan waktu berlalu
    _finish_truth(session)
    _assert_arc_done(session)
    assert "mem_04" in session.state.memories
    assert session.state.flags.get("branch_3c") is True


def test_balancing_arc_quest_only_berakhir_lv4_6(session, god_mode):
    """Pengawal balancing (target GDD §11.1): quest saja (tanpa grinding) harus
    berakhir di Pengumpul Qi Lv.4–6 — bukan Lv.10/breakthrough (regresi exp)."""
    play_to_incident(session)
    finish_dialog(session, [0, 0])  # opt_3aa
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_penatua"})
    finish_dialog(session, [0])
    _finish_truth(session)
    _assert_arc_done(session)
    lvl = session.state.player.realm_level
    assert 4 <= lvl <= 6, f"quest-only berakhir Lv.{lvl} — target GDD Lv.5-6, was Lv.10 sebelum rebalancing"
    assert session.state.player.realm == "realm_pengumpul_qi"


def test_satu_aktif_invariant(session, god_mode):
    """Quest utama bergerak satu-per-satu, tidak pernah dua sekaligus."""
    seen = []
    play_to_incident(session)
    # telusuri quest utama yang terselesaikan dalam urutan
    for qid in ["q_akademi_01", "q_akademi_02", "q_akademi_03", "q_akademi_04", "q_akademi_05", "q_akademi_06"]:
        assert qid in session.state.completed_quests
    assert session.state.current_quest is None or session.state.current_quest.startswith("q_akademi_3")
    # hanya satu quest aktif per waktu (field tunggal) — pastikan tidak ada side quest ganda main
    assert "arc_akademi_selesai" not in session.state.flags


def test_advance_time_day_offset_ditegakkan(session, god_mode):
    """Cabang 3c (advance_time + day_offset 1): butuh sehari penuh, bukan cuma jam target."""
    from conftest import finish_dialog, play_to_incident

    play_to_incident(session)  # hari 1 jam 20, dialog pilih sikap pending
    finish_dialog(session, [2])  # berdiam diri → q_akademi_3c
    assert session.state.current_quest == "q_akademi_3c"
    # baru lewat 2 jam → belum 1 hari penuh → quest tetap aktif
    session.apply_action({"type": "advance_time", "hours": 2})  # hari 1 jam 22
    assert session.state.current_quest == "q_akademi_3c"
    # lewati ke hari berikutnya → selesai menuju kebenaran
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2 jam 22
    assert session.state.current_quest == "q_akademi_07"


def test_side_quest_berburu_selesai_via_kemenangan(session, god_mode, monkeypatch):
    """Side quest defeat: mulai lewat dialog pemburu, selesai setelah 2 kill."""
    from conftest import finish_dialog

    monkeypatch.setattr("src.engine.session.random.choice", lambda seq: "eno_serigala_qi")
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2, jam 8
    session.apply_action({"type": "talk", "npc": "npc_pemburu"})
    finish_dialog(session, [0])  # "Aku ambil tugasnya."
    assert "q_side_berburu" in session.state.active_side_quests

    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    assert "q_side_berburu" not in session.state.active_side_quests
    assert "q_side_berburu" in session.state.completed_quests


def test_konvergensi_semua_cabang(session, god_mode):
    """Semua 4 cabang menyatu di q_akademi_07."""
    for branch, choices in [("3aa", [0, 0]), ("3ab", [0, 1]), ("3b", [1]), ("3c", [2])]:
        s = GameSession.new(session.reg)
        play_to_incident(s)
        finish_dialog(s, choices)
        if branch in ("3aa",):
            move_path(s, ["loc_perpustakaan", "loc_paviliun"])
            s.apply_action({"type": "talk", "npc": "npc_penatua"})
            finish_dialog(s, [0])
        elif branch == "3b":
            move_path(s, ["loc_perpustakaan", "loc_paviliun", "loc_aula_ujian"])
            s.apply_action({"type": "talk", "npc": "npc_zhouyan"})
            finish_dialog(s, [0])
        elif branch == "3c":
            s.apply_action({"type": "advance_time", "hours": 24})
        _finish_truth(s)
        assert "q_akademi_07" in s.state.completed_quests
        assert s.state.flags.get("arc_akademi_selesai") is True


def test_single_active_main_quest(dummy_session):
    state = dummy_session.state
    # Asumsikan 'q_akademi_01' adalah quest awal dari data nyata
    state.current_quest = "q_akademi_01"
    
    # Selesaikan objektif (misalnya bicara dengan penjaga)
    dummy_session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(dummy_session)
    
    # Verifikasi bahwa current quest berpindah ke next (misal q_akademi_02)
    assert state.current_quest != "q_akademi_01"
    assert state.current_quest == "q_akademi_02"
    # Pastikan tidak ada 2 quest utama yang tercatat
    assert isinstance(state.current_quest, str)


def test_side_quest_cooldown(session, god_mode, monkeypatch):
    """Side quest can be completed, cannot be immediately started again, but can be started after cooldown."""
    from conftest import finish_dialog

    monkeypatch.setattr("src.engine.session.random.choice", lambda seq: "eno_serigala_qi")
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2, jam 8
    
    # 1. Take and finish quest
    assert session.quest.is_offerable("q_side_berburu") is True
    session.apply_action({"type": "talk", "npc": "npc_pemburu"})
    finish_dialog(session, [0])  # Take quest
    assert "q_side_berburu" in session.state.active_side_quests
    
    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    assert "q_side_berburu" not in session.state.active_side_quests
    assert "q_side_berburu" in session.state.completed_quests
    assert "q_side_berburu" in session.state.side_quest_cooldowns
    
    # 2. Cannot start again immediately
    assert session.quest.is_offerable("q_side_berburu") is False
    
    # 3. Advance time by cooldown (2 hours) and start again
    session.apply_action({"type": "advance_time", "hours": 2})
    assert session.quest.is_offerable("q_side_berburu") is True


