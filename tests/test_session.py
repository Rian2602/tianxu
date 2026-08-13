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
