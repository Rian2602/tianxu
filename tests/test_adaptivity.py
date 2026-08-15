"""Test adaptivitas (G1-T3, plan 2026-08-15): fixture arc 2 sintetis.

Arc 2 (id ber-prefix `arc2` — BUKAN id arc-1) diinjeksi ke registry:
lokasi, NPC, dialog (dengan choice bersyarat relation_min), item, musuh, dan
quest (talk → reach+time_window → defeat+report_to; side gather+report_to).

Alur lengkap dijalankan lewat `GameSession` TANPA perubahan kode engine —
bukti klaim "arc baru = data saja". Bila arc berikutnya butuh mekanik baru,
test inilah yang harus diperluas (sinyal sadar, bukan hardcode diam-diam).
"""

from __future__ import annotations

import pytest

from src.engine.session import GameSession
from src.loader import DataRegistry

from tests.conftest import finish_dialog, move_path  # noqa: F401


def _inject_arc2(reg: DataRegistry) -> None:
    # --- lokasi (terhubung dari paviliun — dunia existing) ---
    reg.locations += [
        {"id": "loc_arc2_a", "name": "Pos Arc2", "is_safe": True,
         "description": "Pos penjaga arc 2.", "connections": ["loc_arc2_b"], "ambience": "forest"},
        {"id": "loc_arc2_b", "name": "Gua Arc2", "is_safe": False,
         "description": "Gua rahasia arc 2.", "connections": ["loc_arc2_a"], "ambience": "night"},
    ]
    pav = next(l for l in reg.locations if l["id"] == "loc_paviliun")
    pav["connections"] = pav.get("connections", []) + ["loc_arc2_a"]
    reg.location_by_id = {l["id"]: l for l in reg.locations}

    # --- NPC + dialog (choice bersyarat relation_min) ---
    reg.npcs.append({"id": "npc_arc2", "name": "Penjaga Arc2", "location": "loc_arc2_a",
                     "role": "guard", "default_dialog": "dlg_arc2"})
    reg.npc_by_id = {n["id"]: n for n in reg.npcs}
    reg.dialogs.append({
        "id": "dlg_arc2", "npc": "npc_arc2", "start": "node_awal",
        "nodes": {
            "node_awal": {"speaker": "npc:npc_arc2", "text": "Ada yang bisa kubantu?",
                          "choices": [
                              {"label": "Ceritakan tentang gua itu.", "next": "node_cerita",
                               "effects": [{"type": "relation", "npc": "npc_arc2", "value": 3}]},
                              {"label": "Aku butuh tugas.", "next": "node_tugas",
                               "effects": [{"type": "start_quest", "quest": "q_side_arc2"}]},
                          ]},
            "node_cerita": {"speaker": "npc:npc_arc2", "text": "Gua itu menyimpan rahasia.", "end": True},
            "node_tugas": {"speaker": "npc:npc_arc2", "text": "Ambil 2 bahan dari gua itu.",
                           "choices": [
                               {"label": "Baik.", "next": "node_tutup",
                                "condition": {"relation_min": {"npc": "npc_arc2", "value": 3}}},
                               {"label": "Baiklah.", "next": "node_tutup"},
                           ]},
            "node_tutup": {"speaker": "npc:npc_arc2", "text": "Sampai jumpa.", "end": True},
        },
    })
    reg.dialog_by_id = {d["id"]: d for d in reg.dialogs}

    # --- item & musuh ---
    reg.items["item_arc2"] = {"id": "item_arc2", "name": "Bahan Arc2", "type": "material",
                              "description": "Bahan arc 2.", "price": "5", "hp_restore": "0",
                              "qi_restore": "0", "power": "0", "rarity": "common", "usable": "false"}
    reg.enemies["eno_arc2"] = {"id": "eno_arc2", "name": "Binatang Arc2", "realm": "realm_pengumpul_qi",
                               "hp": "10", "qi": "0", "attack": "3", "defense": "0", "speed": "5",
                               "element": "api", "exp_reward": "5", "drop_item": "", "drop_chance": "0"}

    # --- quest: talk → reach+window → defeat+report; side gather+report ---
    reg.quests += [
        {"id": "q_arc2_01", "kind": "main", "title": "Arc2 T1",
         "objective": {"kind": "talk", "npc": "npc_arc2"}, "next": [{"quest": "q_arc2_02"}],
         "on_complete": {"rewards": {"exp": 1}}},
        {"id": "q_arc2_02", "kind": "main", "title": "Arc2 T2",
         "objective": {"kind": "reach", "location": "loc_arc2_b",
                       "time_window": {"hour_start": 0, "hour_end": 24}},
         "next": [{"quest": "q_arc2_03"}], "on_complete": {"rewards": {"exp": 1}}},
        {"id": "q_arc2_03", "kind": "main", "title": "Arc2 T3",
         "objective": {"kind": "defeat", "enemies": ["eno_arc2"], "target": 1, "report_to": "npc_arc2"},
         "next": [], "on_complete": {"rewards": {"exp": 1}}},
        {"id": "q_side_arc2", "kind": "side", "title": "Arc2 S1",
         "objective": {"kind": "gather", "item": "item_arc2", "target": 2, "report_to": "npc_arc2"},
         "available_from": {"day": 1, "hour": 0}, "cooldown": 5, "next": [],
         "on_complete": {"rewards": {"exp": 1}}},
    ]
    reg.quest_by_id = {q["id"]: q for q in reg.quests}

    # --- arc 2 + transisi dari arc 1 (data) ---
    reg.config.setdefault("arcs", []).append({
        "id": "arc2", "final_quest": "q_arc2_03", "title": "AKHIR ARC 2: INTRIK",
        "teaser": "Teaser.", "memories_total": 1, "branches": {"branch_arc2": "Cabang Arc 2"}})
    reg.quest_by_id["q_akademi_07"]["next"] = [{"quest": "q_arc2_01"}]


@pytest.fixture
def arc2_session(registry: DataRegistry) -> GameSession:
    _inject_arc2(registry)
    return GameSession.new(registry)


def test_adaptif_main_quest_talk_reach_defeat(arc2_session, god_mode):
    """Main quest arc 2 sintetis: talk → reach+time_window → defeat+report — tanpa ubah engine."""
    from tests.test_playthrough_branches import _play_3aa
    s = arc2_session
    _play_3aa(s)  # selesaikan arc 1 → transisi otomatis ke arc 2 (data)
    assert s.state.current_quest == "q_arc2_01"

    # T1: talk npc_arc2 di loc_arc2_a — pilih cerita (relation +3)
    move_path(s, ["loc_paviliun", "loc_arc2_a"])
    s.apply_action({"type": "talk", "npc": "npc_arc2"})
    finish_dialog(s, [0])
    assert s.state.current_quest == "q_arc2_02"
    assert s.state.relations.get("npc_arc2", 0) == 3

    # T2: reach loc_arc2_b (dalam window 0-24)
    s.apply_action({"type": "move", "to": "loc_arc2_b"})
    assert s.state.current_quest == "q_arc2_03"

    # T3: defeat eno_arc2 (1 kill) — belum selesai, wajib lapor (report_to)
    foe = dict(s.reg.enemies["eno_arc2"], name="Binatang Arc2")
    s.battle.start([foe], "hunt")
    s.apply_action({"type": "battle_action", "action": "attack"})
    assert s.state.pending_battle is None
    assert s.state.current_quest == "q_arc2_03", "defeat + report_to belum lapor → belum selesai"

    # lapor ke npc_arc2
    s.apply_action({"type": "move", "to": "loc_arc2_a"})
    s.apply_action({"type": "talk", "npc": "npc_arc2"})
    finish_dialog(s)
    assert s.state.current_quest is None
    assert "q_arc2_03" in s.state.completed_quests

    # arc_summary menunjuk arc 2 (generik via final_quest)
    assert s.view()["arc_summary"]["title"] == "AKHIR ARC 2: INTRIK"


def test_adaptif_dialog_bersyarat_dan_side_quest(arc2_session, god_mode):
    """Dialog bersyarat (relation_min) + side quest gather+report — data arc 2 murni."""
    s = arc2_session
    move_path(s, ["loc_aula_ujian", "loc_paviliun", "loc_arc2_a"])

    # bicara → pilih "Aku butuh tugas" → side quest aktif → node_tugas
    s.apply_action({"type": "talk", "npc": "npc_arc2"})
    s.apply_action({"type": "dialog_choice", "choice_index": 1})
    assert "q_side_arc2" in s.state.active_side_quests

    # node_tugas: pilihan "Baik." (relation_min 3) TERSEMBUNYI — relation masih 0
    v = s.dialog.view()
    labels = [c["label"] for c in v["choices"]]
    assert "Baik." not in labels, "choice bersyarat relation_min harus disembunyikan"
    assert "Baiklah." in labels
    finish_dialog(s, [0])
    assert not s.state.pending_dialog

    # kumpulkan bahan → lapor → quest selesai + item diambil
    s.state.inventory["item_arc2"] = 2
    s.apply_action({"type": "talk", "npc": "npc_arc2"})
    finish_dialog(s)
    assert "q_side_arc2" in s.state.completed_quests
    assert s.state.inventory.get("item_arc2", 0) == 0, "bahan harus diambil saat serah"
