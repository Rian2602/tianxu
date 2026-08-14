"""Pembaca data — memuat semua file JSON/CSV ke struktur Python.

Data dipegang sebagai dict (data-driven): menambah field di data tidak
memerlukan perubahan kode. Lookup disediakan lewat dict index.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


class DataRegistry:
    """Indeks semua data game (dibaca sekali saat startup)."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = Path(data_dir)

        self.config = self._json("config.json")

        main_quests = self._json("quests/quests_akademi.json")["quests"]
        side_quests = self._json("quests/quests_side.json")["quests"]
        self.quests = main_quests + side_quests

        self.dialogs = self._json("dialogs/dialogs_akademi.json")["dialogs"]
        self.npcs = self._json("npcs.json")["npcs"]
        self.locations = self._json("locations.json")["locations"]
        self.memories = self._json("memories.json")["memories"]
        self.recipes = self._json("recipes.json")["recipes"]
        self.companions = self._json("companions.json")["companions"]

        self.items = {r["id"]: r for r in self._csv("items.csv")}
        self.enemies = {r["id"]: r for r in self._csv("enemies.csv")}
        self.realms = {r["id"]: r for r in self._csv("realms.csv")}
        self.techniques = {r["id"]: r for r in self._csv("techniques.csv")}

        # lookup index
        self.quest_by_id = {q["id"]: q for q in self.quests}
        self.dialog_by_id = {d["id"]: d for d in self.dialogs}
        self.npc_by_id = {n["id"]: n for n in self.npcs}
        self.location_by_id = {l["id"]: l for l in self.locations}
        self.memory_by_id = {m["id"]: m for m in self.memories}

        # konfigurasi turunan
        self.roots_tier = {t["id"]: t for t in self.config.get("roots", {}).get("tiers", [])}
        self.element_advantage = self.config.get("element_advantage", {})

    # ---------- pembaca file ----------

    def _json(self, rel: str):
        with open(self.data_dir / rel, encoding="utf-8") as f:
            return json.load(f)

    def _csv(self, rel: str) -> list[dict]:
        with open(self.data_dir / rel, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    # ---------- bantuan umum ----------

    def realm_by_id(self, realm_id: str) -> dict | None:
        return self.realms.get(realm_id)

    def quest(self, qid: str) -> dict | None:
        return self.quest_by_id.get(qid)

    def dialog(self, did: str) -> dict | None:
        return self.dialog_by_id.get(did)

    def npc(self, nid: str) -> dict | None:
        return self.npc_by_id.get(nid)

    def location(self, lid: str) -> dict | None:
        return self.location_by_id.get(lid)

    def item(self, iid: str) -> dict | None:
        return self.items.get(iid)

    def enemy(self, eid: str) -> dict | None:
        return self.enemies.get(eid)

    def memory(self, mid: str) -> dict | None:
        return self.memory_by_id.get(mid)

    def technique(self, tid: str) -> dict | None:
        return self.techniques.get(tid)

    # ---------- pemain ----------

    def player_techniques(self, academy: str, realm: str | None = None,
                          completed_quests: frozenset = frozenset(),
                          owned: tuple = ()) -> list[dict]:
        """Teknik yang tersedia untuk pemain: skill_pool akademi + unlock_arc (B4) +
        teknik yang dimiliki (`owned`, C1 — reward quest/dialog), dibatasi ranah.

        Bila `realm` diberikan, teknik dengan `realm_required` lebih tinggi disembunyikan
        (H4) — pola sama seperti `dialog.py` membandingkan `order` ranah.

        B4 (GDD §5.2): teknik dengan `unlock_arc` terisi ikut tampil untuk akademi mana
        pun bila quest final arc itu sudah selesai (arc selesai = data arc berikutnya
        bisa membuka teknik akademi lain tanpa mengubah engine).
        C1 (GDD §7): `owned` = id teknik milik pemain (dari efek `technique`).
        """
        pools: list[str] = []
        for a in self.config.get("academies", []):
            if a["id"] == academy:
                pools = list(a.get("skill_pool") or [])
                break
        out: list[dict] = []
        # A6: semua elemen skill_pool diproses (bukan hanya [0]) — pool 2+ (mis.
        # ["tek_elemen_*", "tek_universal_*"]); dedup via `t not in out`.
        for pool in pools:
            prefix = pool.rstrip("*")
            for t in self.techniques.values():
                if t["id"].startswith(prefix) and t not in out:
                    out.append(t)
        # teknik lintas akademi: unlock_arc → arc selesai bila final_quest-nya di completed_quests
        done_arcs = {
            a["id"] for a in self.config.get("arcs", [])
            if a.get("final_quest") in completed_quests
        }
        out += [
            t for t in self.techniques.values()
            if t.get("unlock_arc") and t["unlock_arc"] in done_arcs
            and t not in out
        ]
        # teknik yang dimiliki (reward quest/dialog) — C1
        for tid in owned:
            t = self.techniques.get(tid)
            if t and t not in out:
                out.append(t)
        if realm:
            cur_r = self.realms.get(realm)
            if cur_r:
                order_cur = int(cur_r["order"])
                out = [
                    t for t in out
                    if int(self.realms.get(t.get("realm_required", realm), cur_r)["order"]) <= order_cur
                ]
        return out
