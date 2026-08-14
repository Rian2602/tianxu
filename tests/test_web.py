"""Test server web (web/app.py) — ENGINE_ARCHITECTURE §12.5.

Menjalankan server nyata (ThreadingHTTPServer) di port acak lalu
memanggil endpoint API lewat urllib.
"""

from __future__ import annotations

import json
import os
import threading
import urllib.request

import pytest

from web import app


@pytest.fixture(scope="module")
def base_url():
    srv = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{port}"
    srv.shutdown()


def post(base: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get(base: str, path: str) -> tuple[bytes, int]:
    with urllib.request.urlopen(base + path) as r:
        return r.read(), r.status


def test_halaman_index(base_url: str) -> None:
    body, status = get(base_url, "/")
    assert status == 200
    assert b"Tian Xu" in body


def test_new_game_mulai_dari_q1(base_url: str) -> None:
    data = post(base_url, "/api/new")
    assert data["ok"] is True
    v = data["view"]
    assert v["current_quest"]["id"] == "q_akademi_01"
    assert v["mode"] == "explore"
    assert v["location"]["id"] == "loc_gerbang_akademi"
    # konteks: penjaga gerbang ada di lokasi
    npcs = [n["id"] for n in data["context"]["npcs"]]
    assert "npc_penjaga" in npcs
    assert "recipes" in data["context"]
    assert isinstance(data["context"]["recipes"], list)


def test_aksi_talk_membuka_dialog(base_url: str) -> None:
    post(base_url, "/api/new")
    data = post(base_url, "/api/action", {"action": {"type": "talk", "npc": "npc_penjaga"}})
    v = data["view"]
    assert v["mode"] == "dialog"
    assert v["dialog"]["speaker"].startswith("npc:")


def test_save_ditolak_di_luar_titik_aman(base_url: str) -> None:
    post(base_url, "/api/new")  # gerbang = bukan titik aman
    data = post(base_url, "/api/action", {"action": {"type": "save", "save_name": "test_web_x"}})
    last = data["view"]["log"][-1]
    assert "titik aman" in last["text"]
    assert not os.path.exists("saves/test_web_x.json")


def test_save_dan_load_di_titik_aman(base_url: str) -> None:
    post(base_url, "/api/new")
    # gerbang → pasar (titik aman)
    post(base_url, "/api/action", {"action": {"type": "move", "to": "loc_pasar"}})
    data = post(base_url, "/api/action", {"action": {"type": "save", "save_name": "test_web_save"}})
    assert data["view"]["location"]["is_safe"] is True
    assert os.path.exists("saves/test_web_save.json")
    # daftar save memuat nama
    body, _ = get(base_url, "/api/saves")
    saves = json.loads(body)
    assert "test_web_save" in saves["saves"]
    # muat kembali
    data2 = post(base_url, "/api/load", {"name": "test_web_save"})
    assert data2["ok"] is True
    assert data2["view"]["location"]["id"] == "loc_pasar"
    os.remove("saves/test_web_save.json")


def test_tianyuan_panel(base_url: str) -> None:
    post(base_url, "/api/new")
    body, status = get(base_url, "/api/tianyuan")
    assert status == 200
    data = json.loads(body)
    assert data["ok"] is True
    # di awal semua ingatan terkunci
    memories = data["tianyuan"]["memories"]
    assert len(memories) == 4
    assert all(m["unlocked"] is False for m in memories)
    assert all(m["title"] == "???" for m in memories)
    assert all(m["text"] is None for m in memories)
    assert data["tianyuan"]["unlocked_count"] == 0
    assert data["tianyuan"]["total_count"] == 4
    assert data["tianyuan"]["mission"]["main"]["id"] == "q_akademi_01"
    assert "side_quests" in data["tianyuan"]["mission"]
    assert "system_log" in data["tianyuan"]
    assert isinstance(data["tianyuan"]["system_log"], list)


def test_tianyuan_panel_side_quest(base_url: str) -> None:
    post(base_url, "/api/new")
    app.session.state.active_side_quests = {"sq_dummy": 0}
    # Mock the quest in registry just for the test to avoid KeyError
    app.registry.quest_by_id["sq_dummy"] = {"id": "sq_dummy", "kind": "side", "title": "Dummy SQ", "objectives": [{"id": "obj1", "desc": "Test"}]}
    
    try:
        body, status = get(base_url, "/api/tianyuan")
        assert status == 200
        data = json.loads(body)
        assert len(data["tianyuan"]["mission"]["side_quests"]) == 1
        assert data["tianyuan"]["mission"]["side_quests"][0]["id"] == "sq_dummy"
    finally:
        # Cleanup mock
        del app.registry.quest_by_id["sq_dummy"]


def test_web_shop_buy_sell(base_url: str) -> None:
    post(base_url, "/api/new")
    app.session.state.player.gold = 500  # give player some gold to buy
    
    # move to market
    data = post(base_url, "/api/action", {"action": {"type": "move", "to": "loc_pasar"}})
    assert data["ok"] is True
    assert "merchant_shop" in data["context"]
    assert data["context"]["merchant_shop"] is not None
    assert "buy" in data["context"]["merchant_shop"]
    
    buy_items = data["context"]["merchant_shop"]["buy"]
    item_price = next(i["price"] for i in buy_items if i["item"] == "material_herba")
    
    gold_before = app.session.state.player.gold
    item_before = app.session.state.inventory.get("material_herba", 0)
    
    # buy an item
    data = post(base_url, "/api/action", {"action": {"type": "shop_buy", "item": "material_herba", "count": 1}})
    assert data["ok"] is True
    
    gold_after_buy = app.session.state.player.gold
    item_after_buy = app.session.state.inventory.get("material_herba", 0)
    
    assert gold_after_buy == gold_before - item_price
    assert item_after_buy == item_before + 1

    sell_items = data["context"]["merchant_shop"]["sell"]
    item_sell_price = next(i["price"] for i in sell_items if i["item"] == "material_herba")

    # sell an item
    data = post(base_url, "/api/action", {"action": {"type": "shop_sell", "item": "material_herba", "count": 1}})
    assert data["ok"] is True

    gold_after_sell = app.session.state.player.gold
    item_after_sell = app.session.state.inventory.get("material_herba", 0)

    assert gold_after_sell == gold_after_buy + item_sell_price
    assert item_after_sell == item_after_buy - 1


def test_api_state_tanpa_sesi(base_url: str) -> None:
    app.session = None
    body, status = get(base_url, "/api/state")
    assert status == 200
    data = json.loads(body)
    assert data["ok"] is True
    assert data["view"] is None
    assert data["context"]["merchant_shop"] is None
    assert data["context"]["recipes"] == []
    assert data["context"]["npcs"] == []


def test_aksi_tanpa_sesi_ditolak() -> None:
    """Tanpa POST /api/new dulu, aksi ditolak dengan pesan jelas."""
    # sesi global dibersihkan
    app.session = None
    srv = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/action",
            data=json.dumps({"action": {"type": "talk", "npc": "npc_penjaga"}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
            assert data["ok"] is False
        except urllib.error.HTTPError as e:
            assert e.code == 400
            data = json.loads(e.read())
            assert "Mulai baru" in data["error"]
    finally:
        srv.shutdown()
        app.session = None


def test_aksi_format_salah_ditolak_400(base_url: str) -> None:
    """Payload action bukan objek → respons JSON 400 (bukan koneksi mati diam-diam)."""
    post(base_url, "/api/new")
    req = urllib.request.Request(
        base_url + "/api/action",
        data=json.dumps({"action": "racik"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        assert False, "harusnya ditolak dengan 400"
    except urllib.error.HTTPError as e:
        assert e.code == 400
        data = json.loads(e.read())
        assert data["ok"] is False
        assert "Format aksi" in data["error"]


def test_body_non_dict_tidak_crash(base_url: str) -> None:
    """Body JSON top-level non-dict (array) → respons JSON 400, bukan koneksi mati (F1)."""
    post(base_url, "/api/new")
    req = urllib.request.Request(
        base_url + "/api/action",
        data=json.dumps(["bukan", "dict"]).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        assert False, "harusnya ditolak dengan 400"
    except urllib.error.HTTPError as e:
        assert e.code == 400
        data = json.loads(e.read())
        assert data["ok"] is False
        assert "Format aksi" in data["error"]


def test_tianyuan_tidak_menampilkan_main_quest_sebagai_side(base_url: str) -> None:
    """Quest utama yang tercatat di active_side_quests tidak boleh tampil sebagai side (G3b)."""
    post(base_url, "/api/new")
    app.session.state.active_side_quests["q_akademi_01"] = {"talk": 0}
    body, status = get(base_url, "/api/tianyuan")
    assert status == 200
    data = json.loads(body)
    side_ids = [s["id"] for s in data["tianyuan"]["mission"]["side_quests"]]
    assert "q_akademi_01" not in side_ids


def test_context_loc_names(base_url: str) -> None:
    """Konteks menyediakan peta id lokasi → nama untuk tombol Pindah (G3a)."""
    data = post(base_url, "/api/new")
    assert data["context"]["loc_names"]["loc_aula_ujian"] == "Aula Ujian"
