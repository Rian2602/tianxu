"""Test sesi — pergerakan, grounding, toko, simpan, item."""

from __future__ import annotations

import os

import pytest


def test_pindah_valid_dan_invalid(session):
    v = session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    assert v["location"]["id"] == "loc_aula_ujian"
    # lokasi tidak terhubung → ditolak
    v = session.apply_action({"type": "move", "to": "loc_ruang_lonceng"})
    assert v["location"]["id"] == "loc_aula_ujian"  # tidak pindah


def test_jadwal_npc_lintas_tengah_malam(session):
    """A1: jadwal 19→06 tersedia di malam & subuh, tidak di siang (pola quest._in_window)."""
    npc = {"id": "npc_test", "name": "Test",
           "schedule": [{"day": 1, "hour_start": 19, "hour_end": 6, "location": "loc_x"}]}
    session.state.hour = 20
    assert session._is_npc_available(npc) is True
    session.state.hour = 5
    assert session._is_npc_available(npc) is True
    session.state.hour = 12
    assert session._is_npc_available(npc) is False
    # batas: hour_end eksklusif (sama dengan quest._in_window) — jam 6 tepat sudah tidak tersedia
    session.state.hour = 6
    assert session._is_npc_available(npc) is False


def test_grounding_hanya_di_titik_aman(session):
    # di gerbang (tidak aman) → ditolak
    session.apply_action({"type": "grounding", "hours": 4})
    assert session.state.grounding_hours_today == 0
    # pindah asrama (aman) → bisa, exp bertambah
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "move", "to": "loc_asrama"})
    exp0 = session.state.player.exp
    session.apply_action({"type": "grounding", "hours": 4})
    assert session.state.grounding_hours_today == 4
    assert session.state.player.exp > exp0
    # lewati batas harian → dibatasi (clamp) ke sisa kuota 4 jam
    v = session.apply_action({"type": "grounding", "hours": 8})
    assert session.state.grounding_hours_today == 8  # 4 + min(8, 4)
    # lewati lagi setelah penuh → ditolak
    session.apply_action({"type": "grounding", "hours": 1})
    assert session.state.grounding_hours_today == 8
    # hari baru → kuota reset
    session.apply_action({"type": "advance_time", "hours": 24})
    assert session.state.grounding_hours_today == 0


def test_toko_beli_jual(session):
    session.state.player.gold = 100
    session.state.inventory["material_tulang"] = 5
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "move", "to": "loc_asrama"})
    session.apply_action({"type": "move", "to": "loc_pasar"})
    # beli Pil Qi (50)
    session.apply_action({"type": "shop_buy", "item": "pil_qi", "count": 1})
    assert session.state.player.gold == 50
    assert session.state.inventory.get("pil_qi", 0) >= 1
    # uang tidak cukup
    v = session.apply_action({"type": "shop_buy", "item": "pedang_bambu", "count": 1})
    assert session.state.player.gold == 50  # ditolak (100 > 50)
    # jual tulang (10)
    session.apply_action({"type": "shop_sell", "item": "material_tulang", "count": 2})
    assert session.state.player.gold == 70
    assert session.state.inventory.get("material_tulang", 0) == 3


def test_simpan_hanya_di_titik_aman(session, tmp_path, monkeypatch):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    # di gerbang (tidak aman) → ditolak
    session.apply_action({"type": "save", "save_name": "tes"})
    assert not list(tmp_path.iterdir())
    # di asrama → tersimpan
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "move", "to": "loc_asrama"})
    session.apply_action({"type": "save", "save_name": "tes"})
    assert (tmp_path / "tes.json").exists()
    # muat ulang → state sama
    from src.engine.session import GameSession

    loaded = GameSession.load(session.reg, "tes")
    assert loaded.state.location == "loc_asrama"
    assert loaded.state.current_quest == session.state.current_quest


def test_pakai_item(session):
    session.state.player.hp = 30
    session.state.player.qi = 5
    session.state.inventory["pil_qi"] = 2
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert session.state.player.qi == 35  # +30, max 40
    assert session.state.inventory.get("pil_qi", 0) == 1


def test_racik_hanya_di_titik_aman(session):
    """Kontrak §9.3: craft hanya di lokasi aman."""
    session.state.inventory["material_herba"] = 2
    pil_before = session.state.inventory.get("pil_qi", 0)  # mulai dengan 3
    # gerbang bukan titik aman → ditolak
    v = session.apply_action({"type": "craft", "recipe": "rc_pil_qi"})
    assert session.state.inventory.get("pil_qi", 0) == pil_before  # tidak bertambah
    assert session.state.inventory.get("material_herba", 0) == 2
    assert "titik aman" in v["log"][-1]["text"]
    # pasar (titik aman) → berhasil
    session.apply_action({"type": "move", "to": "loc_pasar"})
    session.apply_action({"type": "craft", "recipe": "rc_pil_qi"})
    assert session.state.inventory.get("pil_qi", 0) == pil_before + 1
    assert session.state.inventory.get("material_herba", 0) == 0
    # bahan tidak cukup → ditolak
    session.state.inventory["material_tulang"] = 1
    v = session.apply_action({"type": "craft", "recipe": "rc_pil_pemulihan"})
    assert session.state.inventory.get("material_tulang", 0) == 1


def test_gate_battle_blok_aksi_lain(session):
    """Saat battle aktif, aksi non-battle ditolak (pindah/talk/rest tidak jalan)."""
    foe = {"id": "eno_serigala_qi", "name": "Serigala Qi", "hp": 30, "qi": 0,
           "attack": 8, "defense": 3, "speed": 7, "element": "logam"}
    session.battle.start([foe], "hunt")
    assert session.state.pending_battle
    loc_before = session.state.location
    hp_before = session.state.player.hp
    session.apply_action({"type": "move", "to": "loc_pasar"})
    assert session.state.location == loc_before  # pindah ditolak
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert session.state.pending_battle  # dialog tidak mulai
    session.apply_action({"type": "rest"})
    assert session.state.player.hp == hp_before  # rest tidak jalan
    # aksi battle tetap sah — akhiri battle deterministik
    session.state.pending_battle = None


def test_equip_senjata(session):
    from src.engine.battle import player_combat

    # tanpa senjata
    base_atk = player_combat(session.state, session.reg)["attack"]
    # item bukan senjata → ditolak
    session.state.inventory["pil_qi"] = 1
    session.apply_action({"type": "equip", "item": "pil_qi"})
    assert session.state.player.equipment["weapon"] is None
    # senjata tidak dimiliki → ditolak
    session.apply_action({"type": "equip", "item": "pedang_angin"})
    assert session.state.player.equipment["weapon"] is None
    # pasang pedang_angin (+5 serangan)
    session.state.inventory["pedang_angin"] = 1
    session.apply_action({"type": "equip", "item": "pedang_angin"})
    assert session.state.player.equipment["weapon"] == "pedang_angin"
    atk = player_combat(session.state, session.reg)["attack"]
    assert atk == base_atk + 5


def test_waktu_maju_dan_hari_berganti(session):
    # mulai jam 8 hari 1; +20 jam = jam 4 hari 2
    session.apply_action({"type": "advance_time", "hours": 20})
    assert session.state.day == 2
    assert session.state.hour == 4
    # lewati 24 jam → hari 3, jam 4
    session.apply_action({"type": "advance_time", "hours": 24})
    assert session.state.day == 3
    assert session.state.hour == 4


def test_load_save_rusak_menolak(tmp_path, monkeypatch, registry):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    (tmp_path / "save1.json").write_text("{rusak", encoding="utf-8")
    with pytest.raises(session_mod.SaveError):
        session_mod.GameSession.load(registry, "save1")


def test_load_save_format_salah_menolak(tmp_path, monkeypatch, registry):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    (tmp_path / "save1.json").write_text('{"player": 1}', encoding="utf-8")
    with pytest.raises(session_mod.SaveError):
        session_mod.GameSession.load(registry, "save1")


def test_load_save_non_utf8_menolak(tmp_path, monkeypatch, registry):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    (tmp_path / "save1.json").write_bytes(b"\xff\xfe")
    with pytest.raises(session_mod.SaveError):
        session_mod.GameSession.load(registry, "save1")


def test_action_blocked_in_battle(dummy_session):
    # Ubah state secara manual agar terlihat sedang dalam pertarungan
    dummy_session.state.ui.mode = "battle"
    dummy_session.state.ui.battle = {"active": True}

    # Mencoba aksi move (pindah lokasi) saat battle
    response = dummy_session.apply_action({"type": "move", "to": "loc_asrama"})

    # Harus ditolak
    assert response.get("error") is not None or "blocked" in str(response.get("log_delta", []))


def test_ui_mode_transition_clears_pending_battle(dummy_session):
    state = dummy_session.state
    state.ui.mode = "battle"
    assert state.pending_battle is not None
    assert state.ui.mode == "battle"

    # Setting mode back to explore clears pending_battle
    state.ui.mode = "explore"
    assert state.pending_battle is None
    assert state.ui.mode == "explore"


def test_crafting_blocked_in_unsafe_zone(dummy_session):
    # Set lokasi ke area tidak aman
    dummy_session.state.location = "loc_gerbang_akademi"  # asumsi is_safe: false

    # Coba craft
    response = dummy_session.apply_action({"type": "craft", "recipe": "rc_pil_qi"})

    # Harus ditolak karena tidak aman
    assert response.get("error") is not None


def test_resting_blocked_in_unsafe_zone(dummy_session):
    # Set lokasi ke area tidak aman
    dummy_session.state.location = "loc_gerbang_akademi"  # is_safe: false
    response = dummy_session.apply_action({"type": "rest"})
    assert response.get("error") is not None


def test_saving_blocked_in_unsafe_zone(dummy_session, tmp_path, monkeypatch):
    from src.engine import session as session_mod

    monkeypatch.setattr(session_mod, "SAVES_DIR", tmp_path)
    dummy_session.state.location = "loc_gerbang_akademi"  # is_safe: false
    response = dummy_session.apply_action({"type": "save", "save_name": "unsafe_save"})
    assert response.get("error") is not None
    assert not (tmp_path / "unsafe_save.json").exists()


def test_grounding_blocked_in_unsafe_zone(dummy_session):
    dummy_session.state.location = "loc_gerbang_akademi"  # is_safe: false
    response = dummy_session.apply_action({"type": "grounding", "hours": 4})
    assert response.get("error") is not None
    assert dummy_session.state.grounding_hours_today == 0


def test_branch_dialog_included_in_apply_action_view(session, god_mode):
    """Memastikan view yang dikembalikan apply_action menyertakan dialog cabang saat quest bercabang selesai."""
    from conftest import finish_dialog, move_path

    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_arena"})
    session.apply_action({"type": "talk", "npc": "npc_hanxiu"})
    finish_dialog(session, [])
    session.apply_action({"type": "battle_action", "action": "attack"})

    session.apply_action({"type": "choose", "option": "akademi_elemen"})

    move_path(session, ["loc_aula_ujian", "loc_paviliun"])
    session.apply_action({"type": "talk", "npc": "npc_suqing"})
    finish_dialog(session, [0])

    session.apply_action({"type": "move", "to": "loc_perpustakaan"})
    session.apply_action({"type": "advance_time", "hours": 12})

    # Aksi move ke loc_ruang_lonceng menyelesaikan q_akademi_02 dan memicu dialog percabangan
    v = session.apply_action({"type": "move", "to": "loc_ruang_lonceng"})

    assert session.state.pending_dialog is not None
    assert v["dialog"] is not None
    assert v["mode"] == "dialog"

def test_hunt_respawn_cooldown(session, god_mode, monkeypatch):
    monkeypatch.setattr("src.engine.session.random.choice", lambda seq: "eno_serigala_qi")
    session.apply_action({"type": "move", "to": "loc_wilayah_berburu"})
    session.apply_action({"type": "hunt"})
    session.apply_action({"type": "battle_action", "action": "attack"})
    
    # Langsung berburu lagi -> ditolak
    v = session.apply_action({"type": "hunt"})
    assert "masih sepi" in v["log"][-1]["text"]
    assert session.state.pending_battle is None
    
    # Lewat 4 jam -> masih ditolak
    session.apply_action({"type": "advance_time", "hours": 4})
    v = session.apply_action({"type": "hunt"})
    assert "masih sepi" in v["log"][-1]["text"]
    assert session.state.pending_battle is None
    
    # Lewat 1 jam lagi (total 5) -> bisa
    session.apply_action({"type": "advance_time", "hours": 1})
    v = session.apply_action({"type": "hunt"})
    assert session.state.pending_battle is not None

def test_npc_schedule_availability(session):
    npc = {
        "id": "npc_test_schedule",
        "name": "Test NPC",
        "location": session.state.location,
        "schedule": [{"hour_start": 9, "hour_end": 17}]
    }
    session.reg.npcs.append(npc)
    session.reg.npc_by_id["npc_test_schedule"] = npc
    
    session.state.hour = 10
    v = session.apply_action({"type": "talk", "npc": "npc_test_schedule"})
    assert "sedang beristirahat" not in v["log"][-1].get("text", "")
    session.state.pending_dialog = None
    
    session.state.hour = 20
    v = session.apply_action({"type": "talk", "npc": "npc_test_schedule"})
    assert "sedang beristirahat" in v["log"][-1]["text"]
    
    session.reg.npcs.remove(npc)


def test_shop_buy_rejected_and_edge_cases(session):
    # Di lokasi tanpa pedagang
    session.state.location = "loc_asrama"
    v = session.apply_action({"type": "shop_buy", "item": "pil_qi", "count": 1})
    assert any("Tidak ada pedagang di sini" in e["text"] for e in session.state.log)

    # Pindah ke pasar (ada pedagang)
    session.state.location = "loc_pasar"
    # Item tidak dijual
    session.apply_action({"type": "shop_buy", "item": "item_gaib_99", "count": 1})
    assert any("Pedagang tidak menjual item itu" in e["text"] for e in session.state.log)

    # Emas tidak cukup
    pil_before = session.state.inventory.get("pil_qi", 0)
    session.state.player.gold = 10  # Pil Qi seharga 50
    session.apply_action({"type": "shop_buy", "item": "pil_qi", "count": 1})
    assert any("Koin Emas tidak cukup" in e["text"] for e in session.state.log)
    assert session.state.player.gold == 10
    assert session.state.inventory.get("pil_qi", 0) == pil_before


def test_shop_sell_rejected_and_edge_cases(session):
    # Di lokasi tanpa pedagang
    session.state.location = "loc_asrama"
    session.apply_action({"type": "shop_sell", "item": "material_tulang", "count": 1})
    assert any("Tidak ada pedagang di sini" in e["text"] for e in session.state.log)

    # Pindah ke pasar
    session.state.location = "loc_pasar"
    # Item tidak dibeli pedagang
    session.apply_action({"type": "shop_sell", "item": "item_gaib_99", "count": 1})
    assert any("Pedagang tidak membeli item itu" in e["text"] for e in session.state.log)

    # Item tidak dimiliki / jumlah tidak cukup
    session.state.inventory["material_tulang"] = 1
    session.state.player.gold = 50
    session.apply_action({"type": "shop_sell", "item": "material_tulang", "count": 5})
    assert any("Kau tidak punya item sebanyak itu" in e["text"] for e in session.state.log)
    assert session.state.player.gold == 50
    assert session.state.inventory["material_tulang"] == 1


def test_craft_rejected_and_edge_cases(session):
    # Di titik aman (pasar)
    session.state.location = "loc_pasar"
    # Resep tidak dikenal
    session.apply_action({"type": "craft", "recipe": "rc_resep_palsu"})
    assert any("Resep tidak dikenal" in e["text"] for e in session.state.log)

    # Bahan tidak cukup (misal rc_pil_qi butuh material_herba: 2)
    session.state.inventory.clear()
    session.apply_action({"type": "craft", "recipe": "rc_pil_qi"})
    assert any("Bahan tidak cukup untuk meracik" in e["text"] for e in session.state.log)


def test_search_rolls_success_and_failure(session, monkeypatch):
    # Di luar wilayah berburu
    session.state.location = "loc_asrama"
    session.apply_action({"type": "search"})
    assert any("Mencari herba hanya bisa dilakukan di Wilayah Berburu" in e["text"] for e in session.state.log)

    # Di wilayah berburu: Gagal roll (random >= 0.6)
    session.state.location = "loc_wilayah_berburu"
    session.state.inventory.clear()
    monkeypatch.setattr("src.engine.session.random.random", lambda: 0.8)
    session.apply_action({"type": "search"})
    assert any("tidak menemukan herba" in e["text"] for e in session.state.log)
    assert session.state.inventory.get("material_herba", 0) == 0

    # Di wilayah berburu: Berhasil roll (random < 0.6)
    monkeypatch.setattr("src.engine.session.random.random", lambda: 0.2)
    session.apply_action({"type": "search"})
    assert any("Kau menemukan 1 Herba Awan" in e["text"] for e in session.state.log)
    assert session.state.inventory.get("material_herba", 0) == 1


def test_talk_edge_cases(session):
    # NPC tidak ditemukan
    session.apply_action({"type": "talk", "npc": "npc_palsu_999"})
    assert any("NPC tidak ditemukan" in e["text"] for e in session.state.log)

    # NPC tidak di lokasi ini
    session.state.location = "loc_asrama"
    session.apply_action({"type": "talk", "npc": "npc_gucanghai"})
    assert any("tidak ada di sini" in e["text"] for e in session.state.log)


def test_move_unknown_location(session):
    session.apply_action({"type": "move", "to": "loc_alam_gaib"})
    assert any("Lokasi tidak dikenal" in e["text"] for e in session.state.log)


def test_spar_edge_cases(session):
    # NPC tidak bisa diajak spar
    session.apply_action({"type": "spar", "npc": "npc_penjaga"})
    assert any("tidak bisa diajak sparing" in e["text"] for e in session.state.log)

    # NPC tidak ada di lokasi ini
    session.state.location = "loc_asrama"
    session.apply_action({"type": "spar", "npc": "npc_hanxiu"})
    assert any("tidak ada di sini" in e["text"] for e in session.state.log)


def test_hunt_outside_hunt_area_and_miniboss(session, monkeypatch):
    session.state.location = "loc_asrama"
    session.apply_action({"type": "hunt"})
    assert any("Berburu hanya bisa dilakukan di Wilayah Berburu" in e["text"] for e in session.state.log)

    # Mini-boss roll (< 0.1)
    session.state.location = "loc_wilayah_berburu"
    session.state.last_hunt_time = None
    monkeypatch.setattr("src.engine.session.random.random", lambda: 0.05)
    session.apply_action({"type": "hunt"})
    assert session.state.pending_battle is not None
    assert session.state.pending_battle["foes"][0]["id"] == "eno_raja_serigala"
    session.state.pending_battle = None


def test_rest_revives_companion(session):
    session.state.location = "loc_asrama"
    session.state.companion = {"id": "komp_roh_awan", "active": False, "hp": 0}
    session.apply_action({"type": "rest", "hours": 8})
    assert session.state.companion["active"] is True
    assert session.state.companion["hp"] > 0
    assert any("bangkit kembali" in e["text"] for e in session.state.log)


def test_safe_save_path_security():
    from src.engine.session import _safe_save_path, SaveError

    for bad in ["../hack", "sub/save", "sub\\save", "bad\x00name", ""]:
        with pytest.raises(SaveError):
            _safe_save_path(bad)


def test_unknown_action(session):
    v = session.apply_action({"type": "aksi_gaib"})
    assert "error" in v
    assert any("Aksi tak dikenal" in e["text"] for e in session.state.log)


def test_view_arc_summaries(session):
    session.state.completed_quests.append("q_akademi_07")
    
    # 3ab
    session.state.flags["branch_3ab"] = True
    v = session.view()
    assert "Cabang 3AB" in v["arc_summary"]["branch"]

    # 3b
    session.state.flags.pop("branch_3ab")
    session.state.flags["branch_3b"] = True
    v = session.view()
    assert "Cabang 3B" in v["arc_summary"]["branch"]

    # 3c
    session.state.flags.pop("branch_3b")
    session.state.flags["branch_3c"] = True
    v = session.view()
    assert "Cabang 3C" in v["arc_summary"]["branch"]

    # 3aa
    session.state.flags.pop("branch_3c")
    session.state.flags["branch_3aa"] = True
    v = session.view()
    assert "Cabang 3AA" in v["arc_summary"]["branch"]

    # unknown branch
    session.state.flags.pop("branch_3aa")
    v = session.view()
    assert "Tidak Diketahui" in v["arc_summary"]["branch"]


def test_view_arc_summaries_data_driven(session):
    """B1: arc_summary dibaca dari config.arcs — memories_total mengikuti config
    (bukan hardcode 4), arc terakhir yang selesai menang, quest asing tak memicu."""
    cfg_arcs = session.reg.config["arcs"]
    session.state.completed_quests.append(cfg_arcs[0]["final_quest"])
    session.state.flags["branch_3aa"] = True

    # (c) memories_total dari config, bukan hardcode 4
    cfg_arcs[0]["memories_total"] = 7
    v = session.view()
    assert v["arc_summary"]["memories_unlocked"] == "0/7", v["arc_summary"]

    # (d) arc terakhir di config yang selesai yang menang
    cfg_arcs.append({
        "id": "sekte", "final_quest": "q_sekte_final", "title": "AKHIR ARC 2: SEKTE",
        "teaser": "t", "memories_total": 5, "branches": {"branch_sekte": "Cabang Sekte"},
    })
    session.state.completed_quests.append("q_sekte_final")
    session.state.flags["branch_sekte"] = True
    v = session.view()
    assert v["arc_summary"]["title"] == "AKHIR ARC 2: SEKTE"
    assert "Cabang Sekte" in v["arc_summary"]["branch"]

    # (b) quest asing tanpa arc → tidak crash, summary tetap arc terakhir yang selesai
    session.state.completed_quests.append("q_asing")
    v = session.view()
    assert v["arc_summary"]["title"] == "AKHIR ARC 2: SEKTE"


def test_session_use_item_edge_cases(session):
    # Item tidak ada
    session.state.inventory.clear()
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert any("Item tidak tersedia" in e["text"] for e in session.state.log)

    # Item bukan consumable
    session.state.inventory["pedang_angin"] = 1
    session.apply_action({"type": "use_item", "item": "pedang_angin"})
    assert any("Item itu tidak bisa dipakai di sini" in e["text"] for e in session.state.log)

    # Item consumable habis (count == 0 dihapus dari dict)
    session.state.inventory["pil_qi"] = 1
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert "pil_qi" not in session.state.inventory


def test_session_spar_success_and_schedule(session):
    # Spar sukses
    session.state.location = "loc_arena"
    v = session.apply_action({"type": "spar", "npc": "npc_hanxiu"})
    assert session.state.pending_battle is not None
    assert session.state.pending_battle["context"] == "spar"
    session.state.pending_battle = None

    # Spar ditolak karena jadwal
    npc = session.reg.npc("npc_hanxiu")
    npc["schedule"] = [{"hour_start": 8, "hour_end": 12}]
    session.state.hour = 20
    session.apply_action({"type": "spar", "npc": "npc_hanxiu"})
    assert any("tidak berada di tempat untuk berlatih" in e["text"] for e in session.state.log)
    npc.pop("schedule", None)


def test_spar_id_pendek_simpan_id_penuh(session):
    # CLI menerima id pendek ("hanxiu") → spar_npc harus menyimpan id penuh agar quest spar selesai
    session.state.location = "loc_arena"
    session.apply_action({"type": "spar", "npc": "hanxiu"})
    assert session.state.pending_battle is not None
    assert session.state.pending_battle["spar_npc"] == "npc_hanxiu"
    session.state.pending_battle = None


def test_guard_pending_dialog_tolak_aksi_lain(session):
    # saat dialog aktif, aksi non-dialog ditolak & dialog tidak hilang (asimetri F2)
    session.apply_action({"type": "talk", "npc": "npc_penjaga"})
    assert session.state.pending_dialog
    session.apply_action({"type": "move", "to": "loc_aula_ujian"})
    assert any("Selesaikan dialog" in e["text"] for e in session.state.log)
    assert session.state.pending_dialog
    assert session.state.location != "loc_aula_ujian"  # aksi terlarang tidak mengeksekusi
    session.apply_action({"type": "dialog_choice", "choice_index": 0})
    assert session.state.pending_dialog == "dlg_penjaga"  # dialog berlanjut normal


def test_berburu_malam_memakai_pool_malam(session, monkeypatch):
    """P1-3: jam dalam night_window (19–6) → pool musuh malam; siang → pool biasa."""
    import src.engine.session as sess_mod

    captured = {}
    orig_choice = sess_mod.random.choice

    def fake_choice(pool):
        captured["pool"] = list(pool)
        return pool[0]

    monkeypatch.setattr(sess_mod.random, "choice", fake_choice)
    monkeypatch.setattr(sess_mod.random, "random", lambda: 0.99)  # hindari mini-boss
    session.state.location = "loc_wilayah_berburu"

    # malam (jam 21) → pool malam
    session.state.hour = 21
    session.apply_action({"type": "hunt"})
    assert session.state.pending_battle is not None
    assert captured["pool"] == ["eno_pembelot_malam", "eno_ular_bayangan"], captured["pool"]
    session.state.pending_battle = None

    # siang (jam 10) → pool siang
    session.state.last_hunt_time = None
    session.state.hour = 10
    session.apply_action({"type": "hunt"})
    assert captured["pool"] == ["eno_serigala_qi", "eno_babi_hutan"], captured["pool"]
    session.state.pending_battle = None

    # subuh (jam 5, lintas tengah malam masih dalam window) → pool malam
    session.state.last_hunt_time = None
    session.state.hour = 5
    session.apply_action({"type": "hunt"})
    assert captured["pool"] == ["eno_pembelot_malam", "eno_ular_bayangan"], captured["pool"]
    session.state.pending_battle = None


def test_session_shop_sell_deletion(session):
    session.state.location = "loc_pasar"
    session.state.inventory["material_tulang"] = 1
    session.apply_action({"type": "shop_sell", "item": "material_tulang", "count": 1})
    assert "material_tulang" not in session.state.inventory


def test_session_hunt_no_foe(session, monkeypatch):
    session.state.location = "loc_wilayah_berburu"
    session.state.last_hunt_time = None
    monkeypatch.setattr(session.reg, "enemy", lambda eid: None)
    session.apply_action({"type": "hunt"})
    assert any("Tidak ada mangsa di sini" in e["text"] for e in session.state.log)


def test_is_npc_available_without_schedule(session):
    assert session._is_npc_available({"name": "Orang Tanpa Jadwal"}) is True


def test_upgrade_technique_hanya_di_titik_aman_dan_batas_slots(session):
    """C1: upgrade teknik di titik aman — biaya gold × level, batas technique_slots ranah."""
    s = session.state
    s.player.academy = "akademi_elemen"
    s.player.techniques = ["tek_elemen_bola_api"]
    s.player.gold = 500

    # (a) di luar titik aman → ditolak
    s.location = "loc_aula_ujian"  # is_safe: false
    v = session.apply_action({"type": "upgrade_technique", "technique": "tek_elemen_bola_api"})
    assert s.player.technique_levels.get("tek_elemen_bola_api", 1) == 1
    assert any("titik aman" in e["text"] for e in s.log)

    # (b) di titik aman → level naik, gold terpotong base × level_sekarang
    s.location = "loc_asrama"
    gold_before = s.player.gold
    base = int(session.reg.config["cultivation"]["technique_upgrade_cost_base"])
    session.apply_action({"type": "upgrade_technique", "technique": "tek_elemen_bola_api"})
    assert s.player.technique_levels.get("tek_elemen_bola_api") == 2
    assert s.player.gold == gold_before - base  # base × 1 (level lama)
    assert any("Lv.2" in e["text"] for e in s.log)

    # (c) batas order ranah + 1 (realm_pengumpul_qi order 1 → max Lv.2) — level tidak lewat
    session.apply_action({"type": "upgrade_technique", "technique": "tek_elemen_bola_api"})
    assert s.player.technique_levels.get("tek_elemen_bola_api") == 2  # tetap (max ranah awal)
    assert any("maksimal" in e["text"] for e in s.log[-1:])

    # (d) teknik di luar kepemilikan (akademi lain, bukan skill_pool & bukan reward) → ditolak
    gold_before = s.player.gold
    session.apply_action({"type": "upgrade_technique", "technique": "tek_senjata_tebasan_angin"})
    assert s.player.technique_levels.get("tek_senjata_tebasan_angin", 1) == 1
    assert s.player.gold == gold_before
    assert any("belum menguasai" in e["text"] for e in s.log[-1:])


def test_talk_returns_view_during_battle(session):
    session.state.pending_battle = {"active": True}
    session._talk({"npc": "npc_penjaga"})
    assert session.state.pending_dialog is None  # dialog tidak boleh mulai saat bertarung
    assert session.state.pending_battle == {"active": True}  # battle tetap berjalan


