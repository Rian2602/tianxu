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

    play_to_incident(session)  # hari 1 jam 20, dialog pilih sikap pending
    finish_dialog(session, [2])  # berdiam diri → q_akademi_3c
    assert session.state.current_quest == "q_akademi_3c"
    # baru lewat 2 jam → belum 1 hari penuh → quest tetap aktif
    session.apply_action({"type": "advance_time", "hours": 2})  # hari 1 jam 22
    assert session.state.current_quest == "q_akademi_3c"
    # lewati ke hari berikutnya → selesai menuju kebenaran
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2 jam 22
    assert session.state.current_quest == "q_akademi_07"


def test_side_quest_berburu_selesai_via_kemenangan_dan_lapor(session, god_mode, monkeypatch):
    """A2 (keputusan §17): side quest defeat selesai setelah 2 kill DAN lapor ke Pemburu."""

    monkeypatch.setattr("src.engine.session.random.choice", lambda seq: "eno_serigala_qi")
    session.apply_action({"type": "advance_time", "hours": 24})  # hari 2, jam 8
    session.apply_action({"type": "talk", "npc": "npc_pemburu"})
    finish_dialog(session, [0])  # "Aku ambil tugasnya."
    assert "q_side_berburu" in session.state.active_side_quests

    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    session.apply_action({"type": "advance_time", "hours": 5})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    # 2 kill tercapai tapi belum lapor → quest BELUM selesai
    assert "q_side_berburu" in session.state.active_side_quests
    # lapor ke Pemburu → selesai
    session.apply_action({"type": "move", "to": "loc_gerbang_akademi"})
    session.apply_action({"type": "talk", "npc": "npc_pemburu"})
    finish_dialog(session, [])
    assert "q_side_berburu" not in session.state.active_side_quests
    assert "q_side_berburu" in session.state.completed_quests


def test_objective_text_lapor_check_hanya_saat_kill_terpenuhi(dummy_session):
    """Fix UX: indikator lapor (✓) hanya tampil setelah target kill TERCAPAI juga,
    bukan sejak talk pertama (lapor sebelum kill bukan laporan yang sah)."""
    qe = dummy_session.quest
    q = {
        "id": "q_side_berburu", "kind": "side", "title": "Berburu",
        "objective": {
            "kind": "defeat", "enemies": ["eno_serigala_qi"], "target": 2,
            "report_to": "npc_pemburu", "hint": "Kalahkan 2 binatang.",
        },
        "next": [], "on_complete": {"rewards": {"exp": 1}},
    }
    # sudah lapor (talk=1) tapi baru 1 kill → laporan belum sah → harus "—"
    dummy_session.state.active_side_quests["q_side_berburu"] = {"talk": 1, "defeated": 1}
    txt = qe.objective_text(q)
    assert "—" in txt, f"kill belum penuh harus tampil '—', dapat: {txt}"
    assert "✓" not in txt, f"kill belum penuh tidak boleh tampil '✓', dapat: {txt}"
    # kill penuh (2) + sudah lapor → laporan sah → "✓"
    dummy_session.state.active_side_quests["q_side_berburu"]["defeated"] = 2
    txt = qe.objective_text(q)
    assert "✓" in txt, f"kill penuh + lapor harus tampil '✓', dapat: {txt}"


def test_spar_kalah_tetap_selesai_dan_dialog_beda(session, monkeypatch):
    """G4a: kalah sparring ujian → quest spar selesai + flag spar_kalah + dialog Gu Canghai berbeda."""
    monkeypatch.setattr("src.engine.battle.random.uniform", lambda a, z: 1.0)
    monkeypatch.setattr("src.engine.battle.random.random", lambda: 1.0)
    monkeypatch.setattr(GameSession, "_is_npc_available", lambda self, npc: True)

    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(session, [0])
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(session, [0])
    session.apply_action({"type": "move", "to": "loc_arena"})
    assert session.state.current_quest == "q_akademi_03"

    session.state.player.hp = 5  # hampir KO — musuh membalas dan mengalahkan
    session.apply_action({"type": "spar", "npc": "npc_hanxiu"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    assert session.state.pending_battle is None  # KO → battle selesai
    assert session.state.current_quest == "q_akademi_04"  # spar quest tetap selesai
    assert session.state.flags.get("spar_kalah") is True
    assert session.state.location != "loc_arena"  # respawn titik aman

    # dialog Gu Canghai berbeda (entri kondisional spar_kalah)
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert "kalah" in session.dialog.view()["text"].lower()
    # regresi evaluasi: setelah konsolasi, dialog normal (node_umum) tetap terjangkau
    # dalam sesi yang sama — satu langkah lanjut dari node_kalah → node_umum
    session.apply_action({"type": "dialog_choice", "choice_index": -1})
    v = session.dialog.view()  # TypeError bila dialog tertutup (regresi node_kalah end)
    assert "Kultivasi itu seperti laut" in v["text"]
    assert v["choices"]  # node_umum punya pilihan nasihat
    finish_dialog(session, [])


def test_konvergensi_semua_cabang(session, god_mode):
    """Semua 4 cabang menyatu di q_akademi_07 + world-facts per cabang (G4b/#10)."""
    expected_world = {
        "3aa": {"zhouyan_status": "bebas", "elder_exposed": True, "academy_knows_truth": True},
        "3ab": {"zhouyan_status": "bebas", "elder_exposed": False, "academy_knows_truth": False},
        "3b": {"zhouyan_status": "diusir", "elder_exposed": False, "academy_knows_truth": False},
        "3c": {"zhouyan_status": "diusir", "elder_exposed": False, "academy_knows_truth": False},
    }
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
        for k, v in expected_world[branch].items():
            assert s.state.flags.get(k) == v, f"{branch}: flag {k} = {s.state.flags.get(k)!r}, harap {v!r}"
        assert s.state.flags.get("bell_status") == "kembali"


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
    session.apply_action({"type": "advance_time", "hours": 5})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    # A2: lapor ke Pemburu untuk menyelesaikan
    session.apply_action({"type": "move", "to": "loc_gerbang_akademi"})
    session.apply_action({"type": "talk", "npc": "npc_pemburu"})
    finish_dialog(session, [])
    assert "q_side_berburu" not in session.state.active_side_quests
    assert "q_side_berburu" in session.state.completed_quests
    assert "q_side_berburu" in session.state.side_quest_cooldowns
    
    # 2. Cannot start again immediately
    assert session.quest.is_offerable("q_side_berburu") is False
    
    # 3. Advance time by cooldown (2 hours) and start again
    session.apply_action({"type": "advance_time", "hours": 2})
    assert session.quest.is_offerable("q_side_berburu") is True


def test_notify_move_reach_outside_time_window(dummy_session):
    """Reach quest dengan time_window (q_akademi_06, 19–6): di luar jendela → tidak selesai."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_akademi_06"
    state.location = "loc_ruang_lonceng"
    state.hour = 12
    qe.notify_move()
    assert state.current_quest == "q_akademi_06"


def test_notify_battle_won_completes_main_defeat(dummy_session, monkeypatch):
    """Quest utama berobjektif defeat selesai saat battle dimenangkan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_synth_defeat"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_defeat", "title": "Buru Synth", "kind": "main",
            "objective": {"kind": "defeat", "target": 1, "enemies": ["eno_serigala_qi"]},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    qe.notify_battle_won(["eno_serigala_qi"])
    assert state.current_quest is None
    assert "q_synth_defeat" in state.completed_quests


def test_in_window_regular_range(dummy_session):
    """_in_window tanpa lintas tengah malam: dalam jendela True, di luar False."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.hour = 12
    assert qe._in_window({"hour_start": 8, "hour_end": 18}) is True
    state.hour = 20
    assert qe._in_window({"hour_start": 8, "hour_end": 18}) is False


def test_resolve_choose_noop_without_choose_objective(dummy_session):
    """resolve_choose tanpa quest utama / bukan objektif choose → no-op."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = None
    qe.resolve_choose("akademi_elemen")
    assert state.player.academy is None
    state.current_quest = "q_akademi_01"  # objektif talk
    qe.resolve_choose("akademi_elemen")
    assert state.player.academy is None


def test_grant_companion_ignores_missing_companion(dummy_session, monkeypatch):
    """Akademi menunjuk companion tak dikenal → tidak crash, companion tidak diberikan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_synth_choose"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_choose", "title": "Pilih Synth", "kind": "main",
            "objective": {"kind": "choose", "options": [{"label": "x", "value": "akademi_xyz"}]},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    qe.reg.config["academies"].append({"id": "akademi_xyz", "companion": "mem_999"})
    qe.resolve_choose("akademi_xyz")
    assert state.companion is None


def test_advance_time_notes_start_when_missing(dummy_session):
    """advance_time_target_met saat progres belum tercatat → mencatat start tanpa crash."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_akademi_3c"
    qe.advance_time_target_met()
    assert "q_akademi_3c" in state.active_side_quests


def test_complete_main_ignores_wrong_quest(dummy_session):
    """_complete_main untuk quest yang bukan current → tidak terjadi apa-apa."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_akademi_01"
    qe._complete_main("q_akademi_99")
    assert state.current_quest == "q_akademi_01"
    assert state.completed_quests == []


def test_select_branch_noop_without_completed_quest(dummy_session):
    """select_branch tanpa quest terselesaikan → pending branch dipertahankan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.branch_pending = "dlg_3_pilih_sikap"
    qe.select_branch("opt_3aa")
    assert state.branch_pending == "dlg_3_pilih_sikap"


def test_select_branch_unmatched_option_clears_pending(dummy_session):
    """Opsi tak cocok dengan cabang mana pun → branch_pending dibersihkan, quest tidak berubah."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.completed_quests.append("q_akademi_06")
    state.branch_pending = "dlg_3_pilih_sikap"
    qe.select_branch("opt_tidak_ada")
    assert state.branch_pending is None
    assert state.current_quest == "q_akademi_01"  # tidak berubah


def test_is_offerable_rejects_unknown_and_main(dummy_session):
    """Quest tak dikenal dan quest utama bukan side → tidak dapat ditawarkan."""
    qe = dummy_session.quest
    assert qe.is_offerable("q_tidak_ada") is False
    assert qe.is_offerable("q_akademi_01") is False


def test_is_offerable_rejects_completed_non_repeatable(dummy_session, monkeypatch):
    """Side quest non-repeatable yang sudah selesai → tidak dapat ditawarkan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.completed_quests.append("q_synth_side")
    monkeypatch.setattr(qe.reg, "quest", lambda qid: {"id": "q_synth_side", "kind": "side"})
    assert qe.is_offerable("q_synth_side") is False


def test_is_offerable_available_from_day(dummy_session, monkeypatch):
    """available_from hari belum tiba → tidak dapat ditawarkan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.day = 1
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {"id": "q_synth_side", "kind": "side", "available_from": {"day": 5, "hour": 0}},
    )
    assert qe.is_offerable("q_synth_side") is False


def test_is_offerable_available_from_hour(dummy_session, monkeypatch):
    """available_from hari sama tapi jam belum tiba → tidak dapat ditawarkan."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.day = 1
    state.hour = 5
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {"id": "q_synth_side", "kind": "side", "available_from": {"day": 1, "hour": 8}},
    )
    assert qe.is_offerable("q_synth_side") is False


def test_start_side_rejects_unofferable(dummy_session):
    """start_side quest yang tak dapat ditawarkan → False, tidak aktif."""
    qe = dummy_session.quest
    assert qe.start_side("q_akademi_01") is False
    assert "q_akademi_01" not in dummy_session.state.active_side_quests


def test_complete_side_ignores_inactive(dummy_session):
    """_complete_side quest yang tidak aktif → tidak crash, tidak tercatat selesai."""
    qe = dummy_session.quest
    qe._complete_side("q_side_berburu")
    assert "q_side_berburu" not in dummy_session.state.completed_quests


def test_advance_time_menyelesaikan_reach_dalam_window(dummy_session):
    """Reach quest (q_akademi_06, window 19-6): lewati waktu dalam jendela → selesai (H1)."""
    state = dummy_session.state
    state.current_quest = "q_akademi_06"
    state.location = "loc_ruang_lonceng"
    state.hour = 18
    state.day = 1
    dummy_session.apply_action({"type": "advance_time", "hours": 2})  # jam 20 → dalam window
    assert "q_akademi_06" in state.completed_quests


def test_rest_memproses_quest_advance_time(dummy_session, monkeypatch):
    """Rest (lewati waktu) ikut memproses quest advance_time — bukan hanya aksi Tunggu (H1)."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_synth_wait"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_wait", "title": "Tunggu Synth", "kind": "main",
            "objective": {"kind": "advance_time", "hour": 20, "day_offset": 0},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    state.location = "loc_asrama"  # titik aman
    state.hour = 19
    state.day = 1
    dummy_session.apply_action({"type": "rest", "hours": 1})  # jam 20
    assert "q_synth_wait" in state.completed_quests


def test_resolve_choose_opsi_invalid_tidak_menuntaskan(dummy_session, monkeypatch):
    """resolve_choose dengan opsi di luar daftar → quest tidak selesai (H2)."""
    qe = dummy_session.quest
    state = dummy_session.state
    state.current_quest = "q_synth_choose"
    monkeypatch.setattr(
        qe.reg, "quest",
        lambda qid: {
            "id": "q_synth_choose", "title": "Pilih Synth", "kind": "main",
            "objective": {"kind": "choose", "options": [{"label": "x", "value": "akademi_xyz"}]},
            "next": [], "on_complete": {"rewards": {"exp": 1}},
        },
    )
    qe.resolve_choose("akademi_tidak_ada")
    assert state.current_quest == "q_synth_choose"
    assert state.player.academy is None


