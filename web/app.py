"""Server web — ENGINE_ARCHITECTURE §12.5 (Fase 1, tanpa build step).

Server stdlib-only (http.server) yang melayani halaman statis + API JSON.
Satu sesi aktif per proses (single-player lokal); save/load lewat `saves/`.

Endpoint:
- GET  /                     → index.html
- GET  /static/*             → aset statis
- GET  /api/state            → view sesi aktif (atau null)
- GET  /api/saves            → daftar slot save
- GET  /api/tianyuan         → ingatan terbuka (dengan teks) + ringkasan
- POST /api/new              → mulai game baru
- POST /api/load             → {name} muat save
- POST /api/action           → {action} aksi pemain → view
- POST /api/save             → {name} simpan (hanya di titik aman)

Jalankan:  python3 web/app.py  →  http://localhost:8000
"""

from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # agar `src` bisa diimpor dari mana saja

from src.engine.session import GameSession, SaveError  # noqa: E402
from src.loader import DataRegistry  # noqa: E402

STATIC_DIR = ROOT / "web" / "static"

registry = DataRegistry()
session: GameSession | None = None  # sesi aktif (single-player lokal)


def _context() -> dict:
    """Konteks UI yang tidak ada di view engine: NPC di lokasi & teknik akademi."""
    if session is None:
        return {"npcs": [], "techniques": []}
    loc = session.state.location
    npcs = [
        {"id": n["id"], "name": n["name"], "can_spar": n.get("can_spar"), "shop": bool(n.get("shop"))}
        for n in registry.npcs if n.get("location") == loc
    ]
    techniques = registry.player_techniques(session.state.player.academy or "")
    academy = next(
        (a["name"] for a in registry.config.get("academies", []) if a["id"] == session.state.player.academy),
        session.state.player.academy,
    )
    return {
        "npcs": npcs,
        "npc_names": {n["id"]: n["name"] for n in registry.npcs},
        "techniques": [
            {"id": t["id"], "name": t["name"], "qi_cost": int(t.get("qi_cost", 0)),
             "kind": t.get("kind"), "description": t.get("description", "")}
            for t in techniques
        ],
        "academy": academy,
        "item_names": {i["id"]: i["name"] for i in registry.items.values()},
    }


def _payload() -> dict:
    """view + context dalam satu respons (dipakai semua endpoint)."""
    return {"view": session.view() if session else None, "context": _context()}


def _tianyuan_payload() -> dict:
    """Panel Tianyuan Ling: ingatan terbuka (dengan teks) + log sistem."""
    memories = []
    for mid in session.state.memories if session else []:
        m = registry.memory(mid)
        if m:
            memories.append({"id": m["id"], "title": m["title"], "text": m.get("text", "")})
    system_log = [e["text"] for e in (session.state.log if session else []) if e["type"] == "system"]
    return {"memories": memories, "system_log": system_log}


class Handler(BaseHTTPRequestHandler):
    server_version = "TianXuWeb/1.0"

    # ---------- utilitas ----------

    def _send(self, body: bytes, ctype: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: dict, status: int = 200) -> None:
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", status)

    def _send_file(self, path: Path) -> None:
        if not path.is_file() or not path.resolve().is_relative_to(STATIC_DIR.resolve()):
            self._send_json({"error": "tidak ditemukan"}, 404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self._send(path.read_bytes(), ctype)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    # ---------- GET ----------

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send_file(STATIC_DIR / "index.html")
        elif self.path.startswith("/static/"):
            self._send_file(STATIC_DIR / self.path[len("/static/"):])
        elif self.path == "/api/state":
            self._send_json({"ok": True, **_payload()})
        elif self.path == "/api/saves":
            names = sorted(p.stem for p in (ROOT / "saves").glob("*.json"))
            self._send_json({"ok": True, "saves": names})
        elif self.path == "/api/tianyuan":
            self._send_json({"ok": True, "tianyuan": _tianyuan_payload()})
        else:
            self._send_json({"error": "endpoint tidak dikenal"}, 404)

    # ---------- POST ----------

    def do_POST(self) -> None:
        global session
        body = self._read_body()
        if self.path == "/api/new":
            session = GameSession.new(registry)
            self._send_json({"ok": True, **_payload()})
        elif self.path == "/api/load":
            name = body.get("name", "save1")
            try:
                session = GameSession.load(registry, name)
                self._send_json({"ok": True, **_payload()})
            except FileNotFoundError:
                self._send_json({"ok": False, "error": f"Save '{name}' tidak ditemukan."}, 404)
            except SaveError as e:
                self._send_json({"ok": False, "error": f"Save '{name}' rusak: {e}"}, 400)
        elif self.path == "/api/action":
            if session is None:
                self._send_json({"ok": False, "error": "Belum ada permainan. Mulai baru atau lanjut save."}, 400)
                return
            action = body.get("action")
            if not isinstance(action, dict):
                self._send_json({"ok": False, "error": "Format aksi tidak valid — butuh objek {type, ...}."}, 400)
                return
            try:
                session.apply_action(action)
            except Exception as exc:  # engine error → respons JSON, bukan koneksi mati diam-diam
                self._send_json({"ok": False, "error": f"Terjadi kesalahan: {exc}"}, 500)
                return
            self._send_json({"ok": True, **_payload()})
        elif self.path == "/api/save":
            if session is None:
                self._send_json({"ok": False, "error": "Belum ada permainan."}, 400)
                return
            session.apply_action({"type": "save", "save_name": body.get("name", "save1")})
            self._send_json({"ok": True, **_payload()})
        else:
            self._send_json({"error": "endpoint tidak dikenal"}, 404)

    def log_message(self, fmt: str, *args) -> None:  # tenang, tanpa spam
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"天缘灵 Tian Xu: Second Life — http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
