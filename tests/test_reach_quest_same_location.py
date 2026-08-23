"""Bug: quest_a05_c05_005 stuck — reach quest tidak selesai jika pemain sudah di lokasi.

Root cause: _note_main_start() tidak mengecek apakah pemain sudah di lokasi target
saat quest reach baru aktif. notify_move() hanya dipanggil saat pemain berpindah.

Fix: Tambahkan pengecekan di _note_main_start() — jika quest baru adalah reach
dan pemain sudah di lokasi target, selesaikan langsung.
"""
from __future__ import annotations


def test_reach_quest_completes_when_already_at_location(session, registry):
    """Reach quest harus selesai meskipun pemain sudah di lokasi target saat quest aktif.

    Simulasi: quest sebelumnya selesai → _advance_main() mengaktifkan quest reach
    baru → pemain sudah di lokasi → quest harus langsung selesai.
    """
    # Setup: pemain di loc_hutan
    session.state.location = "loc_hutan"

    # Inject reach quest yang menuntut pemain ke loc_hutan (lokasi saat ini)
    reach_quest = {
        "id": "q_test_reach",
        "kind": "main",
        "title": "Test Reach Same Location",
        "objective": {"kind": "reach", "location": "loc_hutan", "hint": "Pergi ke hutan."},
        "on_complete": {"effects": [], "rewards": {"gold": 10}},
        "next": [],
    }
    registry.quests.append(reach_quest)
    registry.quest_by_id["q_test_reach"] = reach_quest

    # Advance: previous quest selesai → q_test_reach aktif
    session.quest._advance_main({"next": [{"quest": "q_test_reach"}]})

    # ASSERT: quest harus selesai karena pemain sudah di loc_hutan
    assert "q_test_reach" in session.state.completed_quests, (
        f"Quest harus selesai tapi masih aktif: {session.state.current_quest}. "
        f"Pemain di {session.state.location}, target = loc_hutan"
    )
    assert session.state.current_quest != "q_test_reach", (
        "current_quest masih q_test_reach seharusnya sudah None"
    )


def test_reach_quest_still_requires_movement_when_not_at_location(session, registry):
    """Reach quest normal: pemain harus bergerak ke lokasi target (regression test)."""
    # Setup: pemain di loc_gerbang (BERBEDA dari target)
    session.state.location = "loc_gerbang"

    reach_quest = {
        "id": "q_test_reach2",
        "kind": "main",
        "title": "Test Reach Different Location",
        "objective": {"kind": "reach", "location": "loc_hutan", "hint": "Pergi ke hutan."},
        "on_complete": {"effects": [], "rewards": {}},
        "next": [],
    }
    registry.quests.append(reach_quest)
    registry.quest_by_id["q_test_reach2"] = reach_quest

    session.quest._advance_main({"next": [{"quest": "q_test_reach2"}]})

    # ASSERT: quest TIDAK boleh selesai (pemain belum di lokasi)
    assert session.state.current_quest == "q_test_reach2", (
        f"Quest tidak boleh selesai premature: "
        f"completed={session.state.completed_quests}, "
        f"current={session.state.current_quest}"
    )


def test_reach_quest_with_time_window_at_location(session, registry):
    """Reach quest dengan time_window: tetap selesai jika pemain di lokasi dan waktu valid."""
    session.state.location = "loc_hutan"
    session.state.day = 5
    session.state.hour = 10

    reach_quest = {
        "id": "q_test_reach_tw",
        "kind": "main",
        "title": "Test Reach Time Window",
        "objective": {
            "kind": "reach",
            "location": "loc_hutan",
            "hint": "Pergi ke hutan.",
            "time_window": {"hour_start": 8, "hour_end": 18},
        },
        "on_complete": {"effects": [], "rewards": {}},
        "next": [],
    }
    registry.quests.append(reach_quest)
    registry.quest_by_id["q_test_reach_tw"] = reach_quest

    session.quest._advance_main({"next": [{"quest": "q_test_reach_tw"}]})

    # Waktu dalam window (10 ∈ [8,18]) → quest selesai
    assert "q_test_reach_tw" in session.state.completed_quests, (
        "Reach quest dengan time_window valid harus selesai saat pemain di lokasi"
    )
