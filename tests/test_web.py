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
    # di awal belum ada ingatan terbuka
    assert data["tianyuan"]["memories"] == []


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
