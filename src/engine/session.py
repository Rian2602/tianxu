"""Sesi game — orkestrasi semua aksi pemain (web & CLI memakai ini).

Aksi (ENGINE_ARCHITECTURE §12.3):
talk, dialog_choice, move, advance_time, choose, battle_action, use_item,
equip, grounding, spar, hunt, search, shop_buy, shop_sell, craft, rest, save.

Gate: saat battle aktif, hanya aksi `battle_action` yang diterima.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..loader import DataRegistry
from .battle import BattleEngine, companion_stats, player_combat
from .dialog import DialogEngine
from .events import add_log
from .quest import QuestEngine
from .state import GameState, PlayerState

SAVES_DIR = Path(__file__).resolve().parent.parent.parent / "saves"


def _safe_save_path(save_name: str) -> Path:
    if not save_name or "/" in save_name or "\\" in save_name or ".." in save_name or "\x00" in save_name:
        raise SaveError(f"nama save tidak valid: '{save_name}'")
    SAVES_DIR.mkdir(exist_ok=True)
    try:
        path = (SAVES_DIR / f"{save_name}.json").resolve()
    except (ValueError, OSError) as e:
        raise SaveError(f"nama save tidak valid: '{save_name}'") from e
    if path.parent != SAVES_DIR.resolve():
        raise SaveError(f"nama save tidak valid: '{save_name}'")
    return path


class SaveError(Exception):
    """Save tidak dapat dimuat: file rusak atau format tidak dikenal."""


class GameSession:
    def __init__(self, registry: DataRegistry, state: GameState) -> None:
        self.reg = registry
        self.state = state
        self.quest = QuestEngine(registry, state)
        self.dialog = DialogEngine(registry, state, self.quest)
        self.battle = BattleEngine(registry, state, self.quest)
        self._maybe_start_branch_dialog()



    # ---------- buat / muat ----------

    @classmethod
    def new(cls, registry: DataRegistry) -> "GameSession":
        start = registry.config["starting"]
        p = start["player"]
        state = GameState(
            player=PlayerState(
                name=p["name"],
                hp=p["hp"],
                qi=p["qi"],
                realm=p["realm"],
                realm_level=p["realm_level"],
                gold=p.get("gold", 0),
                roots=p.get("roots", "akar_mid"),
                equipment=dict(p.get("equipment", {"weapon": None})),
            ),
            location=start["location"],
            day=registry.config["time"]["start_day"],
            hour=registry.config["time"]["start_hour"],
            current_quest=start.get("current_quest"),
            inventory={i["id"]: i["count"] for i in start.get("inventory", [])},
            flags=dict(start.get("flags", {})),
        )
        loc = registry.location(state.location)
        if loc and loc.get("is_safe"):
            state.last_safe_location = state.location
        return cls(registry, state)

    @classmethod
    def load(cls, registry: DataRegistry, save_name: str) -> "GameSession":
        path = _safe_save_path(save_name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise
        except (OSError, ValueError) as e:
            raise SaveError(f"save '{save_name}' rusak: {e}") from e
        try:
            state = GameState.from_dict(data)
        except (KeyError, TypeError, ValueError) as e:
            raise SaveError(f"save '{save_name}' format tidak dikenal: {e}") from e
        return cls(registry, state)

    # ---------- aksi utama ----------

    def apply_action(self, action: dict) -> dict:
        t = action.get("type")
        # battle aktif: hanya aksi battle yang sah (cegah pindah/bicara saat bertarung)
        if self.state.pending_battle and t != "battle_action":
            msg = "Kau sedang bertarung — selesaikan atau kabur dulu."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        # dialog aktif: hanya pilihan dialog yang sah (asimetri dengan guard battle di atas)
        if self.state.pending_dialog and t != "dialog_choice":
            msg = "Selesaikan dialog dulu."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        handler = {
            "talk": self._talk,
            "dialog_choice": self._dialog_choice,
            "move": self._move,
            "advance_time": self._advance_time,
            "choose": self._choose,
            "battle_action": self._battle_action,
            "use_item": self._use_item,
            "equip": self._equip,
            "grounding": self._grounding,
            "spar": self._spar,
            "hunt": self._hunt,
            "search": self._search,
            "rest": self._rest,
            "shop_buy": self._shop_buy,
            "shop_sell": self._shop_sell,
            "craft": self._craft,
            "upgrade_technique": self._upgrade_technique,
            "save": self._save,
        }
        fn = handler.get(t)
        if fn:
            return fn(action)
        msg = f"Aksi tak dikenal: {t}."
        add_log(self.state, "system", msg)
        res = self.view()
        res["error"] = msg
        return res

    def _battle_action(self, action: dict) -> dict:
        self.battle.player_action(action)
        self._maybe_start_branch_dialog()
        return self.view()

    def _maybe_start_branch_dialog(self) -> None:
        """Saat quest percabangan selesai — mulai dialog pilih cabang."""
        if self.state.branch_pending and not self.state.pending_dialog and not self.state.pending_battle:
            res = self.dialog.start(self.state.branch_pending)
            if not res:
                self.state.branch_pending = None

    def can_hunt(self) -> bool:
        """G2-T1: lokasi berburu dibaca dari data (config.world.hunt.location) —
        tanpa hardcode id lokasi arc-1; konsisten dengan `_hunt` (A8)."""
        loc = (self.reg.config.get("world", {}).get("hunt") or {}).get("location")
        return bool(loc) and self.state.location == loc

    def _is_npc_available(self, npc: dict) -> bool:
        """Jadwal NPC — pola sama dengan quest._in_window (A1): dukung lintas tengah
        malam (19 → 6) dan batas hour_end eksklusif (start <= h < end)."""
        schedules = npc.get("schedule", [])
        if not schedules:
            return True
        for s in schedules:
            h_start = s.get("hour_start", 0)
            h_end = s.get("hour_end", 24)
            h = self.state.hour
            if h_start <= h_end:
                if h_start <= h < h_end:
                    return True
            elif h >= h_start or h < h_end:  # lintas tengah malam
                return True
        return False

    # ---------- aksi spesifik ----------

    def _talk(self, action: dict) -> dict:
        if self.state.pending_battle:
            return self.view()
        nid = action.get("npc")
        npc = self.reg.npc(nid)
        if not npc:
            add_log(self.state, "system", "NPC tidak ditemukan.")
            return self.view()
        if not self._is_npc_available(npc):
            add_log(self.state, "system", f"{npc['name']} sedang beristirahat/bertapa dan tidak menerima tamu saat ini.")
            return self.view()
        if npc.get("location") != self.state.location:
            add_log(self.state, "system", f"{npc['name']} tidak ada di sini.")
            return self.view()
        # A3: quest talk aktif dengan `start_node` → dialog dipaksa mulai dari node itu
        # (mis. konfrontasi 3aa terjadi SAAT quest berjalan, bukan setelah selesai)
        forced = None
        q = self.quest.current_main()
        if q and q.get("objective", {}).get("kind") == "talk" and q["objective"].get("npc") == nid:
            forced = q["objective"].get("start_node")
        dlg = self.dialog.start(npc.get("default_dialog", ""), forced_node=forced)
        if not dlg:
            add_log(self.state, "system", f"{npc['name']} tidak ingin bicara.")
        return self.view()

    def _dialog_choice(self, action: dict) -> dict:
        idx = action.get("choice_index")
        if idx is None or idx < 0:
            self.dialog.advance()
        else:
            self.dialog.choose(idx)
        if self.dialog.current is None and not self.dialog.node_id:
            self._after_dialog()
        return self.view()

    def _after_dialog(self) -> None:
        npc_id = self.dialog.last_npc
        # objektif talk — A3: laporkan semua node yang dimainkan (node wajib)
        self.quest.notify_dialog_ended(npc_id or "", getattr(self.dialog, "last_nodes", None))
        # objektif spar: mulai battle melawan NPC
        q = self.quest.current_main()
        if q and q.get("objective", {}).get("kind") == "spar" and q["objective"].get("npc") == npc_id:
            npc = self.reg.npc(npc_id or "")
            if npc and npc.get("combat"):
                foe = dict(npc["combat"], name=npc["name"], id=npc["id"])
                self.battle.start([foe], "spar")
                self.state.pending_battle["spar_npc"] = npc_id
                return
        # pilihan cabang quest (dialog percabangan)
        if self.state.branch_pending:
            if getattr(self.dialog, "last_dialog_id", None) == self.state.branch_pending:
                self.quest.select_branch(self.dialog.chosen_option or "")
            else:
                self._maybe_start_branch_dialog()

    def _move(self, action: dict) -> dict:
        to = action.get("to")
        loc = self.reg.location(to)
        cur = self.reg.location(self.state.location)
        if not loc:
            add_log(self.state, "system", "Lokasi tidak dikenal.")
            return self.view()
        if to not in cur.get("connections", []):
            add_log(self.state, "system", f"Kau tidak bisa langsung pergi ke {loc['name']} dari sini.")
            return self.view()
        self.state.location = to
        add_log(self.state, "narration", f"Kau pindah ke {loc['name']}.")
        if loc.get("is_safe"):
            self.state.last_safe_location = to
        self.quest.notify_move()
        self._maybe_start_branch_dialog()
        return self.view()

    def _advance_time(self, action: dict) -> dict:
        hours = max(1, int(action.get("hours", 1)))
        self._pass_time(hours)
        return self.view()

    def _pass_time(self, hours: int) -> None:
        self.state.hour += hours
        while self.state.hour >= 24:
            self.state.hour -= 24
            self.state.day += 1
            self.state.grounding_hours_today = 0  # hari baru
            self.state.exp_grind_today = 0
        self.quest.notify_move()
        self.quest.advance_time_target_met()
        self._maybe_start_branch_dialog()

    def _choose(self, action: dict) -> dict:
        self.quest.resolve_choose(action.get("option", ""))
        self._maybe_start_branch_dialog()
        return self.view()

    def _equip(self, action: dict) -> dict:
        """Pasang senjata ke slot equipment.weapon (ENGINE_ARCHITECTURE §9.3)."""
        iid = action.get("item")
        if self.state.inventory.get(iid, 0) < 1:
            add_log(self.state, "system", "Item tidak tersedia.")
            return self.view()
        it = self.reg.item(iid)
        if not it or it.get("type") != "weapon":
            add_log(self.state, "system", "Item itu bukan senjata.")
            return self.view()
        self.state.player.equipment["weapon"] = iid
        add_log(self.state, "narration", f"Memasang {it['name']} (+{int(it.get('power', 0))} serangan).")
        return self.view()

    def _use_item(self, action: dict) -> dict:
        iid = action.get("item")
        if self.state.inventory.get(iid, 0) < 1:
            add_log(self.state, "system", "Item tidak tersedia.")
            return self.view()
        it = self.reg.item(iid)
        if not it or it.get("type") != "consumable":
            add_log(self.state, "system", "Item itu tidak bisa dipakai di sini.")
            return self.view()
        self.state.inventory[iid] -= 1
        if self.state.inventory[iid] <= 0:
            del self.state.inventory[iid]
        hp = int(it.get("hp_restore", 0))
        qi = int(it.get("qi_restore", 0))
        self.state.player.hp = min(self.state.max_hp(self.reg), self.state.player.hp + hp)
        self.state.player.qi = min(self.state.max_qi(self.reg), self.state.player.qi + qi)
        add_log(self.state, "narration", f"Memakai {it['name']} (+{hp} HP, +{qi} Qi).")
        self.quest.notify_gather()
        return self.view()

    def _grounding(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Berkultivasi hanya bisa dilakukan di lokasi aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        hours = max(1, int(action.get("hours", 1)))
        cfg = self.reg.config["cultivation"]
        allowed = cfg.get("grounding_max_hours_per_day", 8) - self.state.grounding_hours_today
        if allowed <= 0:
            add_log(self.state, "system", "Kau sudah berkultivasi maksimal hari ini.")
            return self.view()
        hours = min(hours, allowed)
        exp = hours * cfg.get("grounding_exp_per_hour", 4)
        self.state.grounding_hours_today += hours
        self._pass_time(hours)
        add_log(self.state, "narration", f"Kau bermeditasi selama {hours} jam... (+{exp} exp, Qi pulih pelan.)")
        from .cultivation import gain_exp
        gain_exp(self.state, self.reg, exp)
        self.state.player.qi = min(self.state.max_qi(self.reg), self.state.player.qi + hours * 2)
        return self.view()

    def can_spar(self, npc: dict) -> bool:
        """Sparring manual tersedia bila NPC bisa spar DAN syarat `spar_require` terpenuhi.

        Data-driven: kondisi di npcs.json (format sama seperti kondisi dialog —
        `flag`, `realm_min`, dll). Tanpa field itu → perilaku lama (can_spar saja)."""
        if not npc.get("can_spar"):
            return False
        req = npc.get("spar_require")
        if not req:
            return True
        from src.engine.dialog import DialogEngine
        return DialogEngine._eval_condition(self.state, req, self.reg)

    def _spar(self, action: dict) -> dict:
        nid = action.get("npc")
        npc = self.reg.npc(nid) or self.reg.npc(f"npc_{nid}")  # terima id pendek ("hanxiu")
        if not npc or not npc.get("can_spar"):
            add_log(self.state, "system", "NPC itu tidak bisa diajak sparing.")
            return self.view()
        if not self.can_spar(npc):
            add_log(self.state, "system", f"{npc['name']} belum bersedia melayanimu sparing.")
            return self.view()
        if not self._is_npc_available(npc):
            add_log(self.state, "system", f"{npc['name']} sedang tidak berada di tempat untuk berlatih tanding.")
            return self.view()
        if npc.get("location") != self.state.location:
            add_log(self.state, "system", f"{npc['name']} tidak ada di sini.")
            return self.view()
        foe = dict(npc["combat"], name=npc["name"], id=npc["id"])
        self.battle.start([foe], "spar")
        self.state.pending_battle["spar_npc"] = npc["id"]
        return self.view()

    def _hunt(self, action: dict) -> dict:
        # A8: semua konten hunt dari config.world.hunt — TANPA fallback id konten
        # arc-1 (data-driven murni; arc baru = data saja)
        hunt = self.reg.config.get("world", {}).get("hunt")
        if not hunt:
            add_log(self.state, "system", "Berburu belum tersedia di dunia ini.")
            return self.view()
        hunt_loc = hunt.get("location")
        if not hunt_loc:
            add_log(self.state, "system", "Berburu belum tersedia di dunia ini.")
            return self.view()
        if self.state.location != hunt_loc:
            loc = self.reg.location(hunt_loc)
            nama = loc.get("name", "Wilayah Berburu") if loc else "Wilayah Berburu"
            add_log(self.state, "system", f"Berburu hanya bisa dilakukan di {nama}.")
            return self.view()
        # P1-3: pool malam (GDD §8) — jam dalam night_window memakai night_pool
        nw = hunt.get("night_window")
        if nw and self.quest._in_window(nw):
            pool = list(hunt.get("night_pool") or [])
        else:
            pool = []
        if not pool:
            pool = list(hunt.get("pool") or [])
        if not pool:
            add_log(self.state, "system", "Tidak ada mangsa di sini.")
            return self.view()
        if random.random() < float(hunt.get("mini_boss_chance", 0.1)):  # mini-boss jarang
            pool = [hunt["mini_boss"]] if hunt.get("mini_boss") else pool
        eid = random.choice(pool)
        foe = self.reg.enemy(eid)
        if not foe:
            add_log(self.state, "system", "Tidak ada mangsa di sini.")
            return self.view()

        respawn_hours = self.reg.config.get("world", {}).get("monster_respawn_hours", 5)
        now_abs_hours = self.state.absolute_hours
        if self.state.last_hunt_time is not None and (now_abs_hours - self.state.last_hunt_time) < respawn_hours:
            remaining = respawn_hours - (now_abs_hours - self.state.last_hunt_time)
            add_log(self.state, "system", f"Wilayah Berburu masih sepi. Monster liar baru muncul kembali dalam {remaining} jam.")
            return self.view()

        self.state.last_hunt_time = now_abs_hours
        self.battle.start([foe], "hunt")
        return self.view()

    def _search(self, action: dict) -> dict:
        # A8: item & lokasi dari config.world.hunt — tanpa fallback id konten
        hunt = self.reg.config.get("world", {}).get("hunt")
        if not hunt or not hunt.get("location"):
            add_log(self.state, "system", "Mencari belum tersedia di dunia ini.")
            return self.view()
        hunt_loc = hunt.get("location")
        if self.state.location != hunt_loc:
            loc = self.reg.location(hunt_loc)
            nama = loc.get("name", "Wilayah Berburu") if loc else "Wilayah Berburu"
            add_log(self.state, "system", f"Mencari herba hanya bisa dilakukan di {nama}.")
            return self.view()
        item_id = hunt.get("search_item")
        if not item_id:
            add_log(self.state, "system", "Tidak ada yang bisa dicari di sini.")
            return self.view()
        if random.random() < 0.6:
            self.state.inventory[item_id] = self.state.inventory.get(item_id, 0) + 1
            it = self.reg.item(item_id)
            nama = it.get("name", item_id) if it else item_id
            add_log(self.state, "narration", f"Kau menemukan 1 {nama} di antara semak.")
            self.quest.notify_gather()
        else:
            add_log(self.state, "narration", "Kau mencari-cari, tapi tidak menemukan herba.")
        return self.view()

    def _rest(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Istirahat hanya bisa dilakukan di titik aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        hours = max(1, int(action.get("hours", 8)))
        self._pass_time(hours)
        self.state.player.hp = self.state.max_hp(self.reg)
        self.state.player.qi = self.state.max_qi(self.reg)
        # kompanion KO bangkit kembali di titik aman (§9.4)
        revived = False
        if self.state.companion and not self.state.companion.get("active"):
            cid = self.state.companion["id"]
            comp = next((c for c in self.reg.companions if c["id"] == cid), None)
            if comp:
                scale = self.reg.config.get("companion", {})
                hp_max = int(comp["base_hp"]) + self.state.player.realm_level * int(scale.get("hp_per_level", 12))
                self.state.companion["active"] = True
                self.state.companion["hp"] = hp_max
                revived = True
        msg = f"Kau beristirahat selama {hours} jam. HP & Qi pulih penuh."
        if revived:
            msg += f" {comp['name']} bangkit kembali."
        add_log(self.state, "narration", msg)
        return self.view()

    def _shop_buy(self, action: dict) -> dict:
        npc = self._merchant_here()
        if not npc:
            add_log(self.state, "system", "Tidak ada pedagang di sini.")
            return self.view()
        iid = action.get("item")
        count = max(1, int(action.get("count", 1)))
        entry = next((s for s in npc["shop"].get("buy", []) if s["item"] == iid), None)
        if not entry:
            add_log(self.state, "system", "Pedagang tidak menjual item itu.")
            return self.view()
        cost = int(entry["price"]) * count
        if self.state.player.gold < cost:
            add_log(self.state, "system", "Koin Emas tidak cukup.")
            return self.view()
        self.state.player.gold -= cost
        self.state.inventory[iid] = self.state.inventory.get(iid, 0) + count
        it = self.reg.item(iid)
        add_log(self.state, "narration", f"Membeli {count}× {it['name']} ({cost} Koin Emas).")
        self.quest.notify_gather()
        return self.view()

    def _shop_sell(self, action: dict) -> dict:
        npc = self._merchant_here()
        if not npc:
            add_log(self.state, "system", "Tidak ada pedagang di sini.")
            return self.view()
        iid = action.get("item")
        count = max(1, int(action.get("count", 1)))
        entry = next((s for s in npc["shop"].get("sell", []) if s["item"] == iid), None)
        if not entry:
            add_log(self.state, "system", "Pedagang tidak membeli item itu.")
            return self.view()
        if self.state.inventory.get(iid, 0) < count:
            add_log(self.state, "system", "Kau tidak punya item sebanyak itu.")
            return self.view()
        self.state.inventory[iid] -= count
        if self.state.inventory[iid] <= 0:
            del self.state.inventory[iid]
        gold = int(entry["price"]) * count
        self.state.player.gold += gold
        it = self.reg.item(iid)
        add_log(self.state, "narration", f"Menjual {count}× {it['name']} (+{gold} Koin Emas).")
        return self.view()

    def _craft(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Meracik hanya bisa dilakukan di titik aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        rid = action.get("recipe")
        recipe = next((r for r in self.reg.recipes if r["id"] == rid), None)
        if not recipe:
            add_log(self.state, "system", "Resep tidak dikenal.")
            return self.view()
        for ing in recipe.get("ingredients", []):
            if self.state.inventory.get(ing["item"], 0) < ing["count"]:
                add_log(self.state, "system", "Bahan tidak cukup untuk meracik.")
                return self.view()
        for ing in recipe["ingredients"]:
            self.state.inventory[ing["item"]] -= ing["count"]
            if self.state.inventory[ing["item"]] <= 0:
                del self.state.inventory[ing["item"]]
        result = recipe["result"]
        self.state.inventory[result] = self.state.inventory.get(result, 0) + recipe.get("count", 1)
        it = self.reg.item(result)
        add_log(self.state, "narration", f"Meracik {recipe.get('count', 1)}× {it['name']}!")
        self.quest.notify_gather()
        return self.view()

    def _upgrade_technique(self, action: dict) -> dict:
        """C1 (GDD §7): naikkan level teknik di titik aman — biaya gold, batas
        `order` ranah + 1 (realms.csv; verifikasi eksekusi: `technique_slots` ranah
        awal = 1 sehingga slots tak memberi ruang upgrade — order+1 memberi 1×
        upgrade di ranah awal & naik per ranah). Hanya teknik yang dimiliki."""
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Meningkatkan teknik hanya bisa dilakukan di titik aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        tid = action.get("technique")
        tek = self.reg.technique(tid)
        if not tek:
            add_log(self.state, "system", "Teknik tidak dikenal.")
            return self.view()
        owned = set(self.state.player.techniques) | {
            t["id"] for t in self.reg.player_techniques(
                self.state.player.academy or "", None,
                frozenset(self.state.completed_quests))
        }
        if tid not in owned:
            add_log(self.state, "system", "Kau belum menguasai teknik itu.")
            return self.view()
        cur = int(self.state.player.technique_levels.get(tid, 1))
        realm = self.reg.realm_by_id(self.state.player.realm)
        max_lvl = (int(realm.get("order", 1)) + 1) if realm else 2
        if cur >= max_lvl:
            add_log(self.state, "system", f"{tek['name']} sudah maksimal (Lv.{cur}) untuk ranahmu.")
            return self.view()
        cfg = self.reg.config.get("cultivation", {})
        base = int(cfg.get("technique_upgrade_cost_base", 20))
        cost = base * cur
        if self.state.player.gold < cost:
            add_log(self.state, "system", f"Koin tidak cukup (butuh {cost}).")
            return self.view()
        self.state.player.gold -= cost
        self.state.player.technique_levels[tid] = cur + 1
        add_log(self.state, "narration", f"{tek['name']} naik ke Lv.{cur + 1} (−{cost} koin).")
        return self.view()

    def _merchant_here(self) -> dict | None:
        for n in self.reg.npcs:
            if n.get("shop") and n.get("location") == self.state.location:
                return n
        return None

    def _save(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Kau hanya bisa menyimpan di titik aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        name = action.get("save_name") or "save1"
        try:
            path = _safe_save_path(name)
        except (SaveError, ValueError, OSError) as e:
            msg = str(e) if isinstance(e, SaveError) else f"nama save tidak valid: '{name}'"
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
        add_log(self.state, "narration", f"Permainan disimpan ({name}).")
        return self.view()

    # ---------- tampilan UI ----------

    def view(self) -> dict:
        self._maybe_start_branch_dialog()
        s = self.state
        loc = self.reg.location(s.location)
        q = self.quest.current_main()
        pc = player_combat(s, self.reg)
        realm = self.reg.realms[s.player.realm]
        
        # arc_summary data-driven (B1): arc TERAKHIR di config yang final quest-nya selesai
        arc_summary = None
        for arc in reversed(self.reg.config.get("arcs", [])):
            if arc.get("final_quest") not in s.completed_quests:
                continue
            chosen_branch = "Tidak Diketahui"
            for flag, label in (arc.get("branches") or {}).items():
                if s.flags.get(flag):
                    chosen_branch = label
                    break
            arc_summary = {
                "completed": True,
                "title": arc.get("title", "AKHIR ARC"),
                "player_name": s.player.name,
                "realm": realm["name_pinyin"],
                "realm_level": s.player.realm_level,
                "academy": s.player.academy,
                "morality": s.player.morality,
                "branch": chosen_branch,
                "memories_unlocked": f"{len(s.memories)}/{arc.get('memories_total', len(self.reg.memories))}",
                "gold": s.player.gold,
                "day": s.day,
                "teaser": arc.get("teaser", ""),
                # C3: ending data-driven (GDD §3.4/§9) — None untuk arc tanpa `endings`
                "ending": self._pick_ending(s, arc),
            }
            break

        return {
            "location": {
                "id": loc["id"], "name": loc["name"], "description": loc["description"],
                "is_safe": loc.get("is_safe", False), "connections": loc.get("connections", []),
                # C4: ambience lokasi (data-driven, opsional) → atmosfer visual web
                "ambience": loc.get("ambience", "academy"),
            },
            "day": s.day,
            "hour": s.hour,
            "month": s.month(self.reg),
            "month_name": s.month_name(self.reg),
            "player": {
                "name": s.player.name,
                "realm": realm["name_pinyin"],
                "realm_level": s.player.realm_level,
                "exp": s.player.exp,
                "exp_next": s.exp_next(self.reg),
                "hp": pc["hp"], "hp_max": pc["hp_max"],
                "qi": pc["qi"], "qi_max": pc["qi_max"],
                "gold": s.player.gold,
                "roots": (self.reg.roots_tier.get(s.player.roots) or {}).get("name", s.player.roots),
                "academy": s.player.academy,
                "morality": s.player.morality,
                "equipment": s.player.equipment,
            },
            "current_quest": {"id": q["id"], "title": q["title"], "objective": self.quest.objective_text(q)} if q else None,
            "side_quests": [
                {"id": sq["id"], "title": sq["title"], "objective": self.quest.objective_text(sq)}
                for sq in self.quest.active_side()
            ],
            "inventory": [
                {"id": iid, "name": self.reg.item(iid)["name"], "count": c,
                 "type": self.reg.item(iid).get("type", "")}
                for iid, c in sorted(s.inventory.items())
                if self.reg.item(iid)
            ],
            "memories": [
                {"id": mid, "title": self.reg.memory(mid)["title"]}
                for mid in s.memories if self.reg.memory(mid)
            ],
            "companion": companion_stats(s, self.reg),
            "mode": self._mode(),
            "dialog": self.dialog.view() if s.pending_dialog else None,
            "battle": self.battle.view() if s.pending_battle else None,
            "choose": self._choose_view(),
            "log": s.log,
            "arc_summary": arc_summary,
        }

    def _pick_ending(self, s, arc: dict) -> dict | None:
        """C3 (GDD §3.4/§9): pilih ending dari `config.arcs[].endings` — ending
        pertama yang kondisinya cocok (first-match, AND — pola `_eval_condition`
        dipakai ulang apa adanya). Tanpa `endings` → None (kontrak view lama).
        Arc berikutnya (mis. final) cukup isi data endings tematik."""
        for end in arc.get("endings") or []:
            cond = end.get("condition") or {}
            if DialogEngine._eval_condition(s, cond, self.reg):
                return {"id": end["id"], "title": end.get("title", ""), "desc": end.get("desc", "")}
        return None

    def _mode(self) -> str:
        if self.state.pending_battle:
            return "battle"
        if self.state.pending_dialog:
            return "dialog"
        q = self.quest.current_main()
        if q and q.get("objective", {}).get("kind") == "choose":
            return "choose"
        return "explore"

    def _choose_view(self) -> dict | None:
        q = self.quest.current_main()
        if not q or q.get("objective", {}).get("kind") != "choose":
            return None
        return {
            "prompt": q.get("objective", {}).get("hint", "Pilih salah satu."),
            "options": [
                {"value": o["value"], "label": o["label"]}
                for o in q.get("objective", {}).get("options", [])
            ],
        }
