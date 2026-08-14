"""Playthrough 4 cabang moral — verifikasi world-state akhir (G1-T1, plan 2026-08-15).

Untuk tiap cabang (3aa/3ab/3b/3c): main dari awal → pilih cabang → selesaikan
sampai q_akademi_07 → assertion world-state akhir: flags, relations, morality,
memories, gold, dan arc_summary.

Nilai yang di-assert berasal dari efek data (quest on_complete + pilihan dialog
yang diambil), bukan asumsi longgar:
- Semua jalur: Su Qing +5 (intro dlg_suqing node_intro, play_to_incident).
- 3aa: penatua +1 (dlg_penatua node_konfrontasi) +8 quest +2 q07 = 11;
  suqing +10 (intro + quest), hanxiu +10 (spar win + quest).
- 3ab: +5 quest +2 q07 = 7; moyun +5.
- 3b: zhouyan -3 (dlg_zhouyan node_keuntungan) -8 quest +2 q07 = -9;
  suqing 0 (5-5), gold +30.
- 3c: -2 quest +2 q07 = 0; suqing +2 (5-3).
"""

from __future__ import annotations

import pytest

from src.engine.session import GameSession

from conftest import finish_dialog, move_path, play_to_incident  # noqa: F401


def _finish_truth(session: GameSession) -> None:
    """Selesaikan arc: bicara Mo Yun sampai kebenaran (q_akademi_07) tercapai."""
    if session.state.location == "loc_aula_ujian":
        move_path(session, ["loc_paviliun", "loc_perpustakaan"])
    else:
        session.apply_action({"type": "move", "to": "loc_perpustakaan"})
    guard = 0
    while "q_akademi_07" not in session.state.completed_quests and guard < 10:
        guard += 1
        session.apply_action({"type": "talk", "npc": "npc_moyun"})
        finish_dialog(session)
    assert "q_akademi_07" in session.state.completed_quests, "arc tidak selesai"


def _play_3aa(session: GameSession) -> None:
    play_to_incident(session)
    finish_dialog(session, [0, 0])  # membongkar → konfrontasi langsung (opt_3aa)
    assert session.state.current_quest == "q_akademi_3aa"
    move_path(session, ["loc_perpustakaan", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_penatua"})
    finish_dialog(session, [0])
    _finish_truth(session)


def _play_3ab(session: GameSession) -> None:
    play_to_incident(session)
    finish_dialog(session, [0, 1])  # membongkar → kumpulkan bukti (opt_3ab)
    assert session.state.current_quest == "q_akademi_3ab"
    _finish_truth(session)


def _play_3b(session: GameSession) -> None:
    play_to_incident(session)
    finish_dialog(session, [1])  # manfaatkan situasi (opt_3b)
    assert session.state.current_quest == "q_akademi_3b"
    move_path(session, ["loc_perpustakaan", "loc_paviliun", "loc_aula_ujian"])
    session.apply_action({"type": "talk", "npc": "npc_zhouyan"})
    finish_dialog(session, [0])
    _finish_truth(session)


def _play_3c(session: GameSession) -> None:
    play_to_incident(session)
    finish_dialog(session, [2])  # berdiam diri (opt_3c)
    assert session.state.current_quest == "q_akademi_3c"
    session.apply_action({"type": "advance_time", "hours": 24})
    _finish_truth(session)


BRANCHES = [
    (
        "3aa",
        _play_3aa,
        {
            "flag": "branch_3aa",
            "label": "Cabang 3AA — Konfrontasi Terbuka Penatua An",
            "zhouyan_status": "bebas",
            "elder_exposed": True,
            "academy_knows_truth": True,
            "memories": {"mem_01", "mem_02"},
            "morality": 11,
            "relations": {"npc_suqing": 10, "npc_hanxiu": 10},  # hanxiu: +5 spar (battle) +5 quest
            "gold_min": None,
        },
    ),
    (
        "3ab",
        _play_3ab,
        {
            "flag": "branch_3ab",
            "label": "Cabang 3AB — Penyelidikan Diam-Diam Mo Yun",
            "zhouyan_status": "bebas",
            "elder_exposed": False,
            "academy_knows_truth": False,
            "memories": {"mem_01", "mem_02"},
            "morality": 7,
            "relations": {"npc_suqing": 5, "npc_moyun": 5},
            "gold_min": None,
        },
    ),
    (
        "3b",
        _play_3b,
        {
            "flag": "branch_3b",
            "label": "Cabang 3B — Memeras Zhou Yan & Mengambil Keuntungan",
            "zhouyan_status": "diusir",
            "elder_exposed": False,
            "academy_knows_truth": False,
            "memories": {"mem_01", "mem_03"},
            "morality": -9,
            "relations": {"npc_suqing": 0},
            "gold_min": 30,
        },
    ),
    (
        "3c",
        _play_3c,
        {
            "flag": "branch_3c",
            "label": "Cabang 3C — Berdiam Diri & Menjaga Diri",
            "zhouyan_status": "diusir",
            "elder_exposed": False,
            "academy_knows_truth": False,
            "memories": {"mem_01", "mem_04"},
            "morality": 0,
            "relations": {"npc_suqing": 2},
            "gold_min": None,
        },
    ),
]


@pytest.mark.parametrize("bid,play,exp", BRANCHES, ids=[b[0] for b in BRANCHES])
def test_playthrough_branch_world_state(session, god_mode, bid, play, exp):
    """G1-T1: world-state akhir per cabang deterministik sesuai efek data."""
    play(session)
    s = session.state

    # quest utama tuntas
    assert s.flags.get("arc_akademi_selesai") is True
    assert s.flags.get("bell_status") == "kembali"
    assert s.current_quest is None
    assert "q_akademi_07" in s.completed_quests

    # flags cabang & konsekuensi dunia
    assert s.flags.get(exp["flag"]) is True
    assert s.flags.get("zhouyan_status") == exp["zhouyan_status"]
    assert s.flags.get("elder_exposed") is exp["elder_exposed"]
    assert s.flags.get("academy_knows_truth") is exp["academy_knows_truth"]

    # ingatan
    assert exp["memories"] <= set(s.memories), f"memory {s.memories} != {exp['memories']}"

    # moralitas akhir sesuai jalur
    assert s.player.morality == exp["morality"], f"moral {s.player.morality} != {exp['morality']}"

    # hubungan NPC sesuai cabang
    for nid, val in exp["relations"].items():
        assert s.relations.get(nid, 0) == val, f"relation {nid} = {s.relations.get(nid)} != {val}"

    # 3b: keuntungan emas
    if exp["gold_min"] is not None:
        assert s.player.gold >= exp["gold_min"]

    # arc_summary menunjuk arc yang benar
    v = session.view()
    summ = v.get("arc_summary")
    assert summ is not None
    assert summ["completed"] is True
    assert summ["title"] == "AKHIR ARC 1: AKADEMI CHANGFENG"
    assert summ["branch"] == exp["label"]
    assert summ["ending"] is None  # arc akademi tanpa endings
    assert summ["memories_unlocked"] == "2/4"
    assert summ["player_name"] == "Chen Xu"
