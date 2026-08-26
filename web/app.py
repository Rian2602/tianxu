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

Jalankan:  python3 web/app.py  →  http://localhost:8000
"""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # agar `src` bisa diimpor dari mana saja

from src.engine.session import GameSession, SaveError  # noqa: E402
from src.loader import DataRegistry  # noqa: E402

STATIC_DIR = ROOT / "web" / "static"

registry = None  # lazy init — tidak crash saat import tanpa data/
session: GameSession | None = None  # sesi aktif (single-player lokal)
_session_lock = threading.Lock()  # K4: defense-in-depth — satu mutasi sesi per waktu


def _ensure_registry() -> None:
    global registry
    if registry is None:
        registry = DataRegistry()


def _context() -> dict:
    """Konteks UI yang tidak ada di view engine: NPC di lokasi, teknik akademi & kurikulum."""
    web_cfg = (registry.config.get("web") if registry else None) or {}
    _meta = {
        # aset visual data-driven (config.web) — tema story baru bisa
        # menunjuk lagu/avatar/judul sendiri; fallback ke default xianxia
        "audio": web_cfg.get("audio", "/static/assets/audio/dawn-over-tian-xu.mp3"),
        "avatar": web_cfg.get("avatar", "/static/assets/img/avatar.jpg"),
        "title": web_cfg.get("title", "天缘灵"),
        "subtitle": web_cfg.get("subtitle", "TIAN XU: SECOND LIFE"),
        "tagline": web_cfg.get("tagline", "天缘灵 · Tian Xu: Second Life"),
        "panel": web_cfg.get("panel", "Tianyuan Ling"),
        # Playtest #3: id dialog intro untuk layar sinematik full-screen
        "intro_dialog": (registry.config.get("intro_dialog") if registry else None),
    }
    if registry is None or session is None:
        return {
            "meta": _meta,
            "npcs": [],
            "techniques": [],
            "merchant_shop": None,
            "recipes": [],
            "curriculum": [],
            "academy_curriculum": [],
            "relations": {},
            "npc_names": {n["id"]: n["name"] for n in (registry.npcs if registry else [])},
            "loc_names": {l["id"]: l["name"] for l in (registry.locations if registry else [])},
            "item_names": {i["id"]: i["name"] for i in ((registry.items.values()) if registry else [])},
            "academy": None,
            "hunts": [],
            "character_status": [],
        }
    loc = session.state.location
    npcs = [
        {"id": n["id"], "name": n["name"], "can_spar": session.can_spar(n), "shop": bool(n.get("shop")),
         "avatar": n.get("avatar", "")}
        for n in registry.npcs if session.npc_location(n) == loc and session._is_npc_available(n)
    ]
    techniques = registry.player_techniques(
        session.state.player.academy or "", session.state.player.realm,
        frozenset(session.state.completed_quests),
        owned=tuple(session.state.player.techniques))
    academy = next(
        (a["name"] for a in registry.config.get("academies", []) if a["id"] == session.state.player.academy),
        session.state.player.academy,
    )
    curriculum = []
    if session.state.player.academy:
        cur_realm = registry.realms.get(session.state.player.realm)
        player_order = int(cur_realm["order"]) if cur_realm else 1
        learned_ids = set(session.state.player.techniques)
        all_prev_learned = True
        for tek in registry.academy_curriculum(session.state.player.academy):
            tid = tek["id"]
            if tid in learned_ids:
                status = "learned"
            else:
                tek_realm = registry.realms.get(tek.get("realm_required", ""), cur_realm)
                tek_order = int(tek_realm["order"]) if tek_realm else 1
                if all_prev_learned and tek_order <= player_order:
                    status = "available"
                else:
                    status = "locked"
                all_prev_learned = False
            curriculum.append({
                "id": tid,
                "name": tek["name"],
                "element": tek.get("element", ""),
                "kind": tek.get("kind", ""),
                "power": int(tek.get("power", 0)),
                "qi_cost": int(tek.get("qi_cost", 0)),
                "realm_required": tek.get("realm_required", ""),
                "description": tek.get("description", ""),
                "status": status,
                "level": session.state.player.technique_levels.get(tid, 1) if status == "learned" else None,
            })
    merchant_shop = None
    merchant = session._merchant_here()
    if merchant:
        merchant_shop = {
            "merchant_id": merchant["id"],
            "merchant_name": merchant["name"],
            "buy": [
                {"item": s["item"], "name": (registry.item(s["item"]) or {}).get("name", s["item"]),
                 "price": s["price"], "type": (registry.item(s["item"]) or {}).get("type", "")}
                for s in merchant["shop"].get("buy", [])
            ],
            "sell": [
                {"item": s["item"], "name": (registry.item(s["item"]) or {}).get("name", s["item"]),
                 "price": s["price"], "type": (registry.item(s["item"]) or {}).get("type", "")}
                for s in merchant["shop"].get("sell", [])
            ],
        }

    recipes = [
        {
            "id": r["id"],
            "result": r["result"],
            # F1.2: resep dengan item tak dikenal (referensi putus dari save lama)
            # → fallback id, bukan 500
            "result_name": (registry.item(r["result"]) or {}).get("name", r["result"]),
            "count": r.get("count", 1),
            "ingredients": [
                {"item": ing["item"], "name": (registry.item(ing["item"]) or {}).get("name", ing["item"]),
                 "count": ing["count"]}
                for ing in r.get("ingredients", [])
            ],
            "description": r.get("description", ""),
        }
        for r in registry.recipes
    ]

    return {
        "meta": _meta,
        "npcs": npcs,
        "merchant_shop": merchant_shop,
        "recipes": recipes,
        "npc_names": {n["id"]: n["name"] for n in registry.npcs},
        "npc_avatars": {n["id"]: n.get("avatar", "") for n in registry.npcs if n.get("avatar")},
        "relations": dict(session.state.relations),
        "npc_profiles": {
            n["id"]: {
                "name": n["name"],
                "profile": n.get("profile", {}),
                "relation": session.state.relations.get(n["id"], 0),
            }
            for n in registry.npcs
        },
        "techniques": [
            {"id": t["id"], "name": t["name"], "qi_cost": int(t.get("qi_cost", 0)),
             "kind": t.get("kind"), "description": t.get("description", ""),
             "level": session.state.player.technique_levels.get(t["id"], 1)}
            for t in techniques
        ],
        "curriculum": curriculum,
        "academy_curriculum": curriculum,
        "academy": academy,
        "loc_names": {l["id"]: l["name"] for l in registry.locations},
        "item_names": {i["id"]: i["name"] for i in registry.items.values()},
        # defense: id/location opsional di data → fallback aman (validator
        # mewajibkannya, tapi web tidak boleh crash pada data lama/parsial)
        "hunts": [{"id": h.get("id", "?"), "name": h.get("name", h.get("id", "?")),
                     "location": h.get("location", ""),
                     "search_item_name": (registry.item(h["search_item"]).get("name", "")
                                           if h.get("search_item") else
                                           ", ".join((registry.item(si["item"]) or {}).get("name", si["item"])
                                                     for si in (h.get("search_items") or [])[:2]))}
                    for h in registry.hunts if h.get("location") == loc],
        # flags untuk frontend gating (meditasi, dll)
        "flags": dict(session.state.flags),
        # status karakter (docs 04: Family Crisis status per anggota) —
        # data-driven: flag `state_{npc}_status` (npc id tanpa prefix `npc_`,
        # mis. npc_lin_yue → state_lin_yue_status) → nilai (loyal/separated/…)
        "character_status": [
            {"npc": n["id"], "name": n["name"],
             "status": session.state.flags[f"state_{n['id'].removeprefix('npc_')}_status"]}
            for n in registry.npcs
            if session.state.flags.get(f"state_{n['id'].removeprefix('npc_')}_status")
        ],
    }


def _payload() -> dict:
    """view + context dalam satu respons (dipakai semua endpoint)."""
    return {"view": session.view() if session else None, "context": _context()}


def _tianyuan_payload() -> dict:
    """Panel Tianyuan Ling: ingatan terbuka (dengan teks) + log sistem."""
    if not session or not registry:
        return {
            "mission": {"main": None, "side_quests": []},
            "memories": [],
            "unlocked_count": 0,
            "total_count": len(registry.memories) if registry else 0,
            "system_log": [],
        }

    q = session.quest.current_main()
    mission = {
        "main": {
            "id": q["id"],
            "title": q["title"],
            "objective": session.quest.objective_text(q),
        } if q else None,
        "side_quests": [
            {
                "id": qd["id"],
                "title": qd["title"],
                "objective": session.quest.objective_text(qd),
            }
            for qd in session.quest.active_side()
        ],
    }

    memories = []
    # memory state v3 = list of dicts {id, reliability} (bukan string) — cek
    # id-nya, bukan membership list (mid in state.memories selalu False utk dict)
    owned = {m["id"] if isinstance(m, dict) else m for m in session.state.memories}
    for mem in registry.memories:
        mid = mem["id"]
        unlocked = mid in owned
        memories.append({
            "id": mid,
            "title": mem["title"] if unlocked else "???",
            "text": mem.get("text", "") if unlocked else None,
            "unlocked": unlocked,
            # docs 06: keandalan ingatan (kurva RENDAH→TINGGI) — dari data
            "reliability": mem.get("reliability", "unknown"),
        })

    system_log = [e["text"] for e in session.state.log if e["type"] == "system"]

    return {
        "mission": mission,
        "memories": memories,
        "unlocked_count": len(session.state.memories),
        "total_count": len(registry.memories),
        "system_log": system_log[-30:],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "TianXuWeb/1.0"

    # ---------- utilitas ----------

    def _send(self, body: bytes, ctype: str, status: int = 200, extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
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
        # no-cache: file statis dibaca dari disk tiap request — browser wajib revalidasi,
        # sehingga perbaikan frontend (app.js/style.css) selalu termuat tanpa hard-refresh
        self._send(path.read_bytes(), ctype, extra={"Cache-Control": "no-cache"})

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    # ---------- GET / HEAD ----------

    def do_HEAD(self) -> None:
        """HEAD: header saja tanpa body (RFC 9110). Untuk file statis dipakai
        curl -I / validasi; API HEAD tidak dijanjikan (fallback 501)."""
        if self.path.startswith("/static/"):
            path = STATIC_DIR / self.path[len("/static/"):]
            if path.is_file() and path.resolve().is_relative_to(STATIC_DIR.resolve()):
                ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(path.stat().st_size))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                return
            self._send_json({"error": "tidak ditemukan"}, 404)
            return
        self.send_error(501, "HEAD tidak didukung untuk endpoint ini")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send_file(STATIC_DIR / "index.html")
        elif self.path.startswith("/static/"):
            self._send_file(STATIC_DIR / self.path[len("/static/"):])
        elif self.path == "/api/state":
            with _session_lock:
                self._send_json({"ok": True, **_payload()})
        elif self.path == "/api/saves":
            names = sorted(p.stem for p in (ROOT / "saves").glob("*.json"))
            self._send_json({"ok": True, "saves": names})
        elif self.path == "/api/reload":
            global registry
            registry = DataRegistry()
            if session is not None:
                session = GameSession(registry, session.state)
            self._send_json({"ok": True, "message": "Data reloaded."})
        elif self.path == "/api/tianyuan":
            with _session_lock:
                self._send_json({"ok": True, "tianyuan": _tianyuan_payload()})
        else:
            self._send_json({"error": "endpoint tidak dikenal"}, 404)

    # ---------- POST ----------

    def do_POST(self) -> None:
        global session
        body = self._read_body()
        with _session_lock:
            if self.path == "/api/new":
                _ensure_registry()
                session = GameSession.new(registry)
                self._send_json({"ok": True, **_payload()})
            elif self.path == "/api/load":
                _ensure_registry()
                name = body.get("name", "save1")
                try:
                    session = GameSession.load(registry, name)
                    self._send_json({"ok": True, **_payload()})
                except FileNotFoundError:
                    self._send_json({"ok": False, "error": f"Save '{name}' tidak ditemukan."}, 404)
                except SaveError as e:
                    self._send_json({"ok": False, "error": f"Save '{name}' rusak: {e}"}, 400)
            elif self.path == "/api/action":
                if session is None or registry is None:
                    self._send_json({"ok": False, "error": "Belum ada permainan. Mulai baru atau lanjut save."}, 400)
                    return
                action = body.get("action")
                if not isinstance(action, dict):
                    self._send_json({"ok": False, "error": "Format aksi tidak valid — butuh objek {type, ...}."}, 400)
                    return
                try:
                    res = session.apply_action(action)
                except Exception as exc:  # engine error → respons JSON, bukan koneksi mati diam-diam
                    self._send_json({"ok": False, "error": f"Terjadi kesalahan: {exc}"}, 500)
                    return
                payload = _payload()
                if res and res.get("error"):  # penolakan aksi (guard dialog/battle, dll) → diteruskan
                    payload["error"] = res["error"]
                self._send_json({"ok": True, **payload})
            else:
                self._send_json({"error": "endpoint tidak dikenal"}, 404)

    def log_message(self, fmt: str, *args) -> None:  # tenang, tanpa spam
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    # banner data-driven (config.web.tagline) — aman bila data/ kosong
    try:
        _ensure_registry()
        tagline = (registry.config.get("web") or {}).get(
            "tagline", "天缘灵 Tian Xu: Second Life")
    except Exception as exc:
        tagline = "天缘灵 Tian Xu: Second Life"
        import traceback
        print(f"[PERINGATAN] Gagal memuat data/: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("[DAMPAK] Server berjalan tanpa data game — beberapa endpoint mungkin gagal.", file=sys.stderr)
    print(f"{tagline} — http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
