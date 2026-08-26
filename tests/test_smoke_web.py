"""Smoke web end-to-end — F0.4 (dikerjakan setelah F1.2 lazy registry).

Menangkis/mengkonfirmasi klaim audit "web 500": server stdlib dijalankan
di port acak, registry minimal di-suntikkan (lazy), lalu endpoint inti
dipanggil lewat HTTP asli. `SAVES_DIR` di-monkeypatch agar tidak menyentuh
`web/../saves` repo.
"""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path

import pytest

from src.loader import DataRegistry
from src.engine.session import GameSession


@pytest.fixture(scope="module")
def web_server():
    """Server web di port acak — SEKALI per modul (efisiensi: start/stop server
    memakan ~0.5s teardown karena poll_interval serve_forever default 0.5s).
    Registry/sesi di-inject per test via `web_app` (monkeypatch)."""
    import web.app as app
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.05),
                              daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def web_app(web_server, data_dir, monkeypatch):
    """Registry minimal + sesi kosong per test — server dipakai bersama.
    Mengembalikan URL base (sama seperti web_server), bukan modul app."""
    import web.app as app
    monkeypatch.setattr(app, "registry", DataRegistry(data_dir=data_dir))
    monkeypatch.setattr(app, "session", None)
    return web_server


def _post(base: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(base + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(base: str, path: str) -> dict:
    with urllib.request.urlopen(base + path) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_web_new_and_talk(web_app):
    """F0.4: POST /api/new → view; POST /api/action talk → dialog; lanjut → quest selesai."""
    base = web_app

    r = _post(base, "/api/new")
    assert r["ok"] is True
    assert r["view"]["mode"] == "explore"
    assert r["view"]["current_quest"]["id"] == "q_min_intro"
    # F2.3: hunts = zona di lokasi pemain (gerbang aman → kosong); zona hunt
    # hanya muncul setelah pindah ke lokasi berburu
    assert r["context"]["hunts"] == []

    # talk ke NPC guru → dialog
    r = _post(base, "/api/action", {"action": {"type": "talk", "npc": "npc_guru"}})
    assert r["ok"] is True
    assert r["view"]["mode"] == "dialog"
    assert r["view"]["dialog"]["speaker"] == "npc:npc_guru"

    # lanjutkan dialog → quest talk selesai, quest choose aktif
    r = _post(base, "/api/action", {"action": {"type": "dialog_choice", "choice_index": -1}})
    assert r["ok"] is True
    assert r["view"]["mode"] == "choose"
    assert r["view"]["current_quest"]["id"] == "q_min_pilih"

    # pilih akademi → quest utama selesai
    r = _post(base, "/api/action", {"action": {"type": "choose", "option": "akademi_bambu"}})
    assert r["ok"] is True
    assert r["view"]["mode"] == "explore"
    assert r["view"]["current_quest"] is None


def test_web_tianyuan(web_app):
    _post(web_app, "/api/new")
    r = _get(web_app, "/api/tianyuan")
    assert r["ok"] is True
    assert r["tianyuan"]["mission"]["main"]["id"] == "q_min_intro"


def test_web_state_no_500(web_app):
    """Tanpa sesi: /api/state → view null, bukan 500."""
    r = _get(web_app, "/api/state")
    assert r["ok"] is True
    assert r["view"] is None


def test_web_action_without_session(web_app):
    """Tanpa sesi: aksi → 400 pesan jelas, bukan 500."""
    import urllib.error
    with pytest.raises(urllib.error.HTTPError) as ei:
        _post(web_app, "/api/action", {"action": {"type": "move", "to": "loc_hutan"}})
    assert ei.value.code == 400


def test_web_meta_asset_config_driven(web_server, tmp_path, monkeypatch):
    """Aset visual data-driven: `config.web.{audio,avatar}` menimpa fallback
    default — tema story baru menunjuk lagu/avatar sendiri tanpa ubah kode."""
    import web.app as app
    from tests.test_adaptivity import build_data
    d = build_data(
        tmp_path,
        quests=[{"id": "q1", "kind": "main", "title": "T",
                 "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}}],
        config_extra={"web": {
            "audio": "/static/assets/audio/theme-baru.mp3",
            "avatar": "/static/assets/img/hero-baru.png",
            "title": "Kisah Baru",
            "subtitle": "THE NEW TALE",
            "tagline": "Kisah Baru · The New Tale",
            "panel": "Memori",
        }})
    monkeypatch.setattr(app, "registry", DataRegistry(data_dir=d))
    monkeypatch.setattr(app, "session", None)
    r = _post(web_server, "/api/new")
    assert r["ok"] is True
    assert r["context"]["meta"]["audio"] == "/static/assets/audio/theme-baru.mp3"
    assert r["context"]["meta"]["avatar"] == "/static/assets/img/hero-baru.png"
    assert r["context"]["meta"]["title"] == "Kisah Baru"
    assert r["context"]["meta"]["subtitle"] == "THE NEW TALE"
    assert r["context"]["meta"]["tagline"] == "Kisah Baru · The New Tale"
    assert r["context"]["meta"]["panel"] == "Memori"


def test_web_craft_recipe_real_flow(web_app):
    """B9 (audit opencode): jalur craft dieksekusi dengan data nyata — bukan 500.

    Fixture `recipes.json` kosong (T2 F0) — resep disuntikkan ke registry runtime
    (tanpa mengubah fixture global), lalu POST craft via HTTP asli."""
    import web.app as app
    base = web_app
    _post(base, "/api/new")
    # resep nyata: bahan pil_qi (pemain mulai dengan 2) → hasil pil_qi
    app.registry.recipes.append({
        "id": "r_uji", "result": "pil_qi",
        "ingredients": [{"item": "pil_qi", "count": 1}],
    })
    r = _post(base, "/api/action", {"action": {"type": "craft", "recipe": "r_uji"}})
    assert r["ok"] is True
    assert r["view"]["mode"] == "explore"


def test_reload_rebinds_session_registry(data_dir, monkeypatch):
    """Reload data tidak boleh meninggalkan sesi memakai registry lama."""
    import web.app as app

    reg1 = DataRegistry(data_dir=data_dir)
    sess = GameSession.new(reg1)
    monkeypatch.setattr(app, "registry", reg1)
    monkeypatch.setattr(app, "session", sess)

    app.registry = DataRegistry(data_dir=data_dir)
    app.session = GameSession(app.registry, app.session.state)

    payload = app._payload()
    assert app.session.reg is app.registry
    assert payload["view"]["location"]["id"] == app.session.state.location
    assert payload["context"]["loc_names"][app.session.state.location]


def test_context_merchant_shop_follows_npc_state_location(tmp_path, monkeypatch):
    """Merchant yang dipindah via npc_state harus ikut membuka panel toko di web."""
    import web.app as app
    from tests.test_adaptivity import build_data

    data_dir = build_data(
        tmp_path,
        quests=[{"id": "q1", "kind": "main", "title": "T",
                 "objective": {"kind": "choose", "options": [{"value": "a", "label": "A"}]}}],
        npcs=[{
            "id": "npc_merchant",
            "name": "Pedagang",
            "location": "l2",
            "shop": {
                "buy": [{"item": "i1", "price": 3}],
                "sell": [{"item": "i1", "price": 1}],
            },
        }],
    )
    reg = DataRegistry(data_dir=data_dir)
    sess = GameSession.new(reg)
    merchant = next(n for n in reg.npcs if n.get("shop"))
    sess.state.npc_states[merchant["id"]] = {"location": sess.state.location}
    monkeypatch.setattr(app, "registry", reg)
    monkeypatch.setattr(app, "session", sess)

    ctx = app._context()
    assert any(n["id"] == merchant["id"] for n in ctx["npcs"])
    assert ctx["merchant_shop"] is not None
    assert ctx["merchant_shop"]["merchant_id"] == merchant["id"]
