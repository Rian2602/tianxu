"""Web game vs data story 7 arc yang NYATA (`data/`) — bukan fixture.

Membuktikan web (app.py + app.js payload) siap menampilkan data kampanye
7 arc: /api/new → playthrough Arc I via HTTP → arc_summary (branch paviliun +
ending), panel Tianyuan (keandalan ingatan dari data), faksi, NPC di lokasi.
Skip bila `data/` kosong (pola sama test_arc1_data) — suite tetap hijau.

Efisiensi: server stdlib di-port acak, SEKALI per modul (start/stop ~0.5s);
playthrough Arc I lewat HTTP memakai urutan persis test_arc1_data.
"""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from src.loader import DataRegistry, DATA_DIR
from src.engine.session import GameSession

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "quests" / "arc01.json").exists(),
    reason="data story 7 arc belum ada di data/",
)


@pytest.fixture(scope="module")
def web_server():
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
def web_app(web_server, monkeypatch):
    """Registry data 7 arc nyata + sesi kosong per test."""
    import web.app as app
    monkeypatch.setattr(app, "registry", DataRegistry())
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


def _talk_through_http(base: str, npc: str) -> None:
    """Buka dialog via HTTP lalu auto-lanjut sampai selesai."""
    r = _post(base, "/api/action", {"action": {"type": "talk", "npc": npc}})
    assert r["ok"] is True and r["view"]["mode"] == "dialog", f"dialog {npc} tak terbuka"
    guard = 0
    while r["view"]["mode"] == "dialog" and guard < 20:
        r = _post(base, "/api/action", {"action": {"type": "dialog_choice", "choice_index": -1}})
        assert r["ok"] is True
        guard += 1


def test_web_new_game_real_data(web_app):
    """POST /api/new → mode dialog (intro narrative) atau explore, quest Arc I aktif."""
    base = web_app
    r = _post(base, "/api/new")
    assert r["ok"] is True
    v, c = r["view"], r["context"]
    # Intro narrative bisa aktif (mode dialog) atau langsung explore
    assert v["mode"] in ("explore", "dialog")
    # Jika intro dialog aktif, selesaikan dulu
    if v["mode"] == "dialog":
        guard = 0
        while v["mode"] == "dialog" and guard < 20:
            r = _post(base, "/api/action", {"action": {"type": "dialog_choice", "choice_index": -1}})
            assert r["ok"] is True
            v = r["view"]
            guard += 1
    assert v["current_quest"]["id"] == "quest_a01_c01_001"
    assert v["location"]["id"] == "loc_tianxu_gate"
    assert "factions" in v  # key view selalu ada (bisa kosong di awal)
    assert any(n["id"] == "npc_aptitude_examiner" for n in c["npcs"])
    assert c["npc_names"]["npc_lin_yue"]
    assert c["loc_names"]["loc_training_hall"]
    # aset visual + judul data-driven: fallback default saat config.web tidak ada
    assert c["meta"]["audio"].endswith("dawn-over-tian-xu.mp3")
    assert c["meta"]["avatar"].endswith("avatar.jpg")
    assert c["meta"]["title"] == "天缘灵"
    assert c["meta"]["subtitle"] == "TIAN XU: SECOND LIFE"
    assert c["meta"]["panel"] == "Tianyuan Ling"
    # status karakter: key selalu ada; kosong di awal game (belum ada keputusan)
    assert c["character_status"] == []


def test_web_character_status_from_flags(web_server, monkeypatch):
    """Status karakter (docs 04: state_*_status Family Crisis) diekspos ke
    frontend setelah keputusan dibuat — data-driven dari flag, bukan hardcode."""
    import web.app as app
    from src.engine.session import GameSession
    reg = DataRegistry()
    s = GameSession.new(reg)
    # simulasi hasil Family Crisis (jalur protect)
    s.state.flags["state_lin_yue_status"] = "loyal"
    s.state.flags["state_mei_ruo_status"] = "loyal"
    s.state.flags["state_shen_luo_status"] = "separated"
    s.state.flags["state_gu_han_status"] = "disillusioned"
    monkeypatch.setattr(app, "registry", reg)
    monkeypatch.setattr(app, "session", s)
    c = _get(web_server, "/api/state")["context"]
    status = {x["npc"]: x["status"] for x in c["character_status"]}
    assert status == {
        "npc_lin_yue": "loyal", "npc_mei_ruo": "loyal",
        "npc_shen_luo": "separated", "npc_gu_han": "disillusioned",
    }
    # nama karakter ikut terkirim untuk ditampilkan UI
    by_id = {x["npc"]: x["name"] for x in c["character_status"]}
    assert by_id["npc_lin_yue"] == "Lin Yue"


def _skip_intro_dialog(base: str) -> None:
    """Selesaikan intro narrative jika aktif."""
    r = _get(base, "/api/state")
    v = r.get("view")
    if v and v.get("mode") == "dialog":
        guard = 0
        while v.get("mode") == "dialog" and guard < 20:
            r = _post(base, "/api/action", {"action": {"type": "dialog_choice", "choice_index": -1}})
            assert r["ok"] is True
            v = r.get("view", {})
            guard += 1


def test_web_arc1_playthrough_summary_tianyuan(web_app):
    """Arc I penuh via HTTP: arc_summary branch paviliun + ending, panel
    Tianyuan menampilkan keandalan ingatan dari data (docs 06)."""
    base = web_app
    _post(base, "/api/new")
    _skip_intro_dialog(base)

    _talk_through_http(base, "npc_aptitude_examiner")
    _talk_through_http(base, "npc_aptitude_examiner")
    r = _post(base, "/api/action", {"action": {"type": "move", "to": "loc_training_hall"}})
    assert r["ok"] is True
    # Complete lesson chain: proctor → lin_yue → shen_luo → gu_han → proctor
    _talk_through_http(base, "npc_proctor")
    _talk_through_http(base, "npc_lin_yue")
    _talk_through_http(base, "npc_shen_luo")
    _talk_through_http(base, "npc_gu_han")
    _talk_through_http(base, "npc_proctor")
    r = _post(base, "/api/action", {"action": {"type": "choose", "option": "pavilion_jianxin"}})
    assert r["ok"] is True
    # Advance through pavilion explanation dialog if triggered
    if r["view"]["mode"] == "dialog":
        while r["view"]["mode"] == "dialog":
            r = _post(base, "/api/action", {"action": {"type": "dialog_choice", "choice_index": -1}})
            assert r["ok"] is True
    # 005a: reach formation
    r = _post(base, "/api/action", {"action": {"type": "move", "to": "loc_outer_region"}})
    # 005b: talk Lin Yue
    _talk_through_http(base, "npc_lin_yue")
    # 005c: defeat 2 binatang_hutan — simulate battle wins via session
    import web.app as _app
    _app.session.quest.notify_battle_won(["binatang_hutan", "binatang_hutan"])
    # 005d: return to formation (move away first, then back)
    _post(base, "/api/action", {"action": {"type": "move", "to": "loc_hutan_akademi"}})
    r = _post(base, "/api/action", {"action": {"type": "move", "to": "loc_outer_region"}})
    # Insiden Malam
    r = _post(base, "/api/action", {"action": {"type": "move", "to": "loc_training_hall"}})
    r = _post(base, "/api/action", {"action": {"type": "move", "to": "loc_protagonist_room"}})
    r = _post(base, "/api/action", {"action": {"type": "rest"}})
    assert r["ok"] is True
    v = r["view"]
    assert v["current_quest"]["id"] == "quest_a02_c01_001"  # transisi ke Arc II
    a = v["arc_summary"]
    assert a is not None and a["completed"] is True
    assert a["title"] == "A New Life"
    assert a["ending"]["id"] == "end_a01_awakening"
    # branch paviliun dari akademi pemain (docs 13: state_pavilion)
    assert a["branch"] == "Pavilion Jianxin (Hati Pedang)"

    # panel Tianyuan: memory yang terbuka membawa reliability dari data
    t = _get(base, "/api/tianyuan")["tianyuan"]
    assert t["mission"]["main"]["id"] == "quest_a02_c01_001"
    by_id = {m["id"]: m for m in t["memories"]}
    assert by_id["memory_a01_m01"]["unlocked"] is True
    assert by_id["memory_a01_m01"]["reliability"] == "RENDAH"
    assert by_id["memory_a01_m04"]["unlocked"] is True
    assert by_id["memory_a01_m04"]["reliability"] == "SEDANG-TINGGI"
    # memory yang belum terbuka tidak bocor teksnya
    assert by_id["memory_a02_m01"]["unlocked"] is False
    assert by_id["memory_a02_m01"]["text"] is None
