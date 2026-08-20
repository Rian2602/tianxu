"""Smoke test jalur dasar engine — F0.3 (ENGINE_ADAPTATION_PLAN).

Membuktikan engine bisa startup & menjalankan loop dasar dengan data minimal:
mulai → bicara (quest talk selesai) → pindah → berburu (battle menang) →
pakai item → pasang senjata → meditasi → istirahat → save/load.

Ini juga gerbang konfirmasi klaim-klaim audit yang selama ini hanya inferensi
statis (lihat docs/AUDIT_VERIFICATION.md).
"""

from __future__ import annotations

from pathlib import Path


def test_new_game_view(registry, session):
    v = session.view()
    assert v["mode"] == "explore"
    assert v["location"]["id"] == "loc_gerbang"
    assert v["location"]["is_safe"] is True
    assert v["player"]["name"] == "Chen Xu"
    assert v["player"]["realm"] == "Chu Ji"
    assert v["player"]["hp"] > 0
    assert v["current_quest"] is not None
    assert v["current_quest"]["id"] == "q_min_intro"
    assert v["arc_summary"] is None


def test_talk_then_choose_flow(registry, session):
    """Alur utama minimal: talk (q_min_intro) → choose akademi (q_min_pilih)
    → quest utama selesai, akademi + starter kit + companion ter-set."""
    v = session.view()
    npcs = [n for n in registry.npcs if session.npc_location(n) == v["location"]["id"]]
    assert npcs, "harus ada NPC di lokasi awal"
    nid = npcs[0]["id"]

    session.apply_action({"type": "talk", "npc": nid})
    v = session.view()
    assert v["mode"] == "dialog", "talk harus membuka dialog"
    assert v["dialog"]["speaker"] == "npc:npc_guru"

    session.apply_action({"type": "dialog_choice", "choice_index": -1})
    v = session.view()
    assert v["mode"] == "choose", "quest chain harus membuka mode choose"
    assert v["current_quest"]["id"] == "q_min_pilih"
    assert "q_min_intro" in session.state.completed_quests

    # pilih akademi → quest selesai + efek akademi diterapkan
    session.apply_action({"type": "choose", "option": "akademi_bambu"})
    v = session.view()
    assert v["mode"] == "explore"
    assert v["current_quest"] is None, "quest choose harus selesai setelah pilih"
    assert "q_min_pilih" in session.state.completed_quests
    assert session.state.player.academy == "akademi_bambu"
    assert session.state.companion and session.state.companion["id"] == "companion_serigala"
    assert session.state.inventory.get("pil_qi", 0) >= 2 + 1  # 2 awal + 1 starter kit


def test_move_and_hunt_battle(registry, session):
    assert registry.hunts and len(registry.hunts) == 1
    hunt_loc = registry.hunts[0]["location"]
    assert hunt_loc == "loc_hutan"

    session.apply_action({"type": "move", "to": hunt_loc})
    v = session.view()
    assert v["location"]["id"] == hunt_loc
    assert v["location"]["is_safe"] is False

    session.apply_action({"type": "hunt"})
    v = session.view()
    assert v["mode"] == "battle", "berburu harus membuka battle"
    assert v["battle"]["foes"], "harus ada musuh"

    # serang sampai menang (guard loop pengaman)
    guard = 0
    while v["mode"] == "battle" and guard < 50:
        session.apply_action({"type": "battle_action", "action": "attack"})
        v = session.view()
        guard += 1
    assert guard < 50, "battle tidak selesai"
    assert v["mode"] == "explore"
    assert session.state.player.hp > 0


def test_use_item_and_equip(registry, session):
    max_hp = session.state.max_hp(registry)
    # pemain mulai full HP → pakai item: inventori berkurang, HP ter-cap di max
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert session.state.inventory.get("pil_qi", 0) == 1
    assert session.state.player.hp == max_hp
    # simulasi luka → pakai item pulihkan +20 (cap max)
    session.state.player.hp = 10
    session.apply_action({"type": "use_item", "item": "pil_qi"})
    assert session.state.player.hp == min(max_hp, 30)
    assert session.state.inventory.get("pil_qi", 0) == 0

    session.apply_action({"type": "equip", "item": "pedang_kayu"})
    assert session.state.player.equipment["weapon"] == "pedang_kayu"
    v = session.view()
    assert v["player"]["equipment"]["weapon"] == "pedang_kayu"


def test_key_item_not_usable_or_equippable(registry, session):
    """B2 (Arc 1): key_item tersimpan di inventori tapi tak bisa dipakai/dipasang."""
    registry.items["kunci_test"] = {"id": "kunci_test", "name": "Kunci Kuno",
                                    "type": "key_item"}
    session.state.inventory["kunci_test"] = 1
    session.apply_action({"type": "equip", "item": "kunci_test"})
    assert session.state.player.equipment.get("weapon") is None
    assert session.state.inventory.get("kunci_test") == 1
    session.apply_action({"type": "use_item", "item": "kunci_test"})
    assert session.state.inventory.get("kunci_test") == 1


def test_grounding_and_rest(registry, session):
    # meditasi di lokasi aman (default 4 jam, tapi dibatasi max per hari)
    session.apply_action({"type": "meditate"})
    v = session.view()
    assert v["mode"] == "explore"
    assert session.state.player.dantian_exp >= 0, "meditasi harus jalan"

    session.apply_action({"type": "move", "to": "loc_training_hall"})
    session.apply_action({"type": "move", "to": "loc_protagonist_room"})
    session.apply_action({"type": "rest"})
    v = session.view()
    assert v["mode"] == "explore"
    assert session.state.player.hp == session.state.max_hp(registry)


def test_save_load(registry, session, tmp_path, monkeypatch):
    import src.engine.session as sess_mod

    # F0 evaluasi #5: SAVES_DIR hardcode repo → wajib di-monkeypatch agar test
    # tidak menulis ke `saves/` asli.
    monkeypatch.setattr(sess_mod, "SAVES_DIR", tmp_path)

    session.apply_action({"type": "save", "save_name": "smoke1"})
    assert (tmp_path / "smoke1.json").exists()

    from src.engine.session import GameSession
    loaded = GameSession.load(registry, "smoke1")
    assert loaded.state.location == session.state.location
    assert loaded.state.day == session.state.day
    assert loaded.state.hour == session.state.hour
    assert loaded.state.player.gold == session.state.player.gold
    # B6 (audit opencode): round-trip tidak cukup 4 field — inventori, quest
    # aktif, flags, equipment ikut diverifikasi agar regresi serialisasi tertangkap.
    assert loaded.state.inventory == session.state.inventory
    assert loaded.state.current_quest == session.state.current_quest
    assert loaded.state.flags == session.state.flags
    assert loaded.state.player.equipment == session.state.player.equipment
