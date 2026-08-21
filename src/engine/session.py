"""Sesi game — orkestrasi semua aksi pemain (web & CLI memakai ini).

Aksi (ENGINE_ARCHITECTURE §12.3):
talk, dialog_choice, move, advance_time, choose, battle_action, use_item,
equip, meditate, spar, hunt, search, shop_buy, shop_sell, craft, rest, save.

Gate: saat battle aktif, hanya aksi `battle_action` yang diterima.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..loader import DataRegistry
from .battle import BattleEngine, companion_stats, player_combat
from .cultivation import gain_exp, meditate, tick_status_effects
from .dialog import DialogEngine
from .effects import apply as apply_effects
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
    """Sesi game — orkestrasi semua aksi pemain (web & CLI)."""

    def __init__(self, registry: DataRegistry, state: GameState) -> None:
        self.reg = registry
        self.state = state
        self.quest = QuestEngine(registry, state)
        self.dialog = DialogEngine(registry, state, self.quest)
        self.battle = BattleEngine(registry, state, self.quest)
        # G3-T1: quest utama yang aktif SEJAK AWAL (config starting, atau save
        # lama tanpa start) dicatat start-nya di sini — tanpa ini timeout & objektif
        # advance_time terhitung dari cek PERTAMA (setelah waktu lewat → deadline
        # mundur diam-diam). Quest yang sudah punya start (DAG/save) tidak disentuh.
        if self.state.current_quest and self.state.current_quest not in self.state.active_side_quests:
            self.quest._note_main_start(self.state.current_quest)
        self._maybe_start_branch_dialog()



    # ---------- buat / muat ----------

    @classmethod
    def new(cls, registry: DataRegistry) -> "GameSession":
        """Buat sesi baru dari config starting."""
        # F1.2: `starting`/`time` wajib di kontrak validator — tapi tetap defensif
        # (save lama / data parsial): default aman, bukan KeyError diam-diam.
        start = registry.config.get("starting") or {}
        p = start.get("player") or {}
        time_cfg = registry.config.get("time") or {}
        realm = p.get("realm") or next(iter(registry.realms), "realm_awal")
        location = start.get("location") or (registry.locations[0]["id"] if registry.locations else "")
        state = GameState(
            player=PlayerState(
                name=p.get("name", "Kultivator"),
                hp=p.get("hp", 50),
                qi=p.get("qi", 30),
                realm=realm,
                realm_level=p.get("realm_level", 1),
                gold=p.get("gold", 0),
                roots=p.get("roots", "akar_mid"),
                equipment=dict(p.get("equipment", {"weapon": None})),
            ),
            location=location,
            day=time_cfg.get("start_day", 1),
            hour=time_cfg.get("start_hour", 6),
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
        """Muat sesi dari save file."""
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
        """Terapkan aksi pemain — return view terbaru."""
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
            "use_key_item": self._use_key_item,
            "equip": self._equip,
            "meditate": self._meditate,
            "spar": self._spar,
            "hunt": self._hunt,
            "search": self._search,
            "rest": self._rest,
            "shop_buy": self._shop_buy,
            "shop_sell": self._shop_sell,
            "craft": self._craft,
            "upgrade_technique": self._upgrade_technique,
            "unlock_technique": self._unlock_technique,
            "fuse_technique": self._fuse_technique,
            "switch_companion": self._switch_companion,
            "mine": self._mine,
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
                self.state.branch_quest = None

    def can_hunt(self) -> bool:
        """Can player hunt at current location? Multi-zone: check registry.hunts."""
        return bool(self.reg.hunts_for_location(self.state.location))

    def hunts_here(self) -> list[dict]:
        """Zones available at current location."""
        return self.reg.hunts_for_location(self.state.location)

    def npc_location(self, npc: dict) -> str:
        """Lokasi NPC — override efek npc_state menang atas data statis npcs.json.
        Jadwal dinamis dari npc_schedules.json menentukan lokasi berdasarkan waktu."""
        nid = npc.get("id", "")
        ov = self.state.npc_states.get(nid, {})
        if ov.get("location"):
            return ov["location"]
        # Cek jadwal dinamis dari npc_schedules.json
        schedules = self.reg.npc_schedules.get(nid)
        if schedules:
            for s in schedules:
                h_start = s.get("hour_start", 0)
                h_end = s.get("hour_end", 24)
                h = self.state.hour
                if h_start <= h_end:
                    if h_start <= h < h_end:
                        return s["location"]
                elif h >= h_start or h < h_end:  # lintas tengah malam
                    return s["location"]
        return npc.get("location", "")

    def _is_npc_available(self, npc: dict) -> bool:
        """Jadwal NPC — pola sama dengan quest._in_window (A1): dukung lintas tengah
        malam (19 → 6) dan batas hour_end eksklusif (start <= h < end). Efek
        npc_state dengan available=false meniadakan NPC (hilang/sembunyi)."""
        ov = self.state.npc_states.get(npc.get("id", ""), {})
        if ov.get("available") is False:
            return False
        schedules = npc.get("schedule", [])
        if not schedules:
            return True
        for s in schedules:
            if s.get("condition") and not self.dialog._eval_condition(self.state, s["condition"], self.reg):
                continue
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
        if self.state.pending_battle or self.state.pending_dialog:
            return self.view()
        nid = action.get("npc")
        npc = self.reg.npc(nid)
        if not npc:
            add_log(self.state, "system", "NPC tidak ditemukan.")
            return self.view()
        if not self._is_npc_available(npc):
            add_log(self.state, "system", f"{npc['name']} sedang beristirahat/bertapa dan tidak menerima tamu saat ini.")
            return self.view()
        if self.npc_location(npc) != self.state.location:
            add_log(self.state, "system", f"{npc['name']} tidak ada di sini.")
            return self.view()
        # A3: quest talk/spar aktif dengan `start_node` → dialog dipaksa mulai dari node itu
        # (mis. konfrontasi 3aa terjadi SAAT quest berjalan, bukan setelah selesai)
        forced = None
        q = self.quest.current_main()
        if q and q.get("objective", {}).get("kind") in ("talk", "spar") and q["objective"].get("npc") == nid:
            forced = q["objective"].get("start_node")
        dlg_id, forced_node = self._resolve_dialog(npc, forced)
        dlg = self.dialog.start(dlg_id, forced_node=forced_node)
        # F3 (adaptifitas): NPC TANPA routing eksplisit (dialog_routes/default_dialog)
        # → fallback deterministik ke dialog yang field `npc`-nya cocok. Tanpa ini,
        # data story minimal (dialog ber-npc tanpa routes) = talk quest softlock
        # diam-diam. Bila author sudah memberi routes, routes dihormati penuh.
        if not dlg and not npc.get("dialog_routes") and not npc.get("default_dialog"):
            for cand in sorted(self.reg.dialogs, key=lambda d: d.get("id", "")):
                if cand.get("npc") == nid:
                    dlg = self.dialog.start(cand["id"], forced_node=forced_node)
                    if dlg:
                        break
        if not dlg:
            add_log(self.state, "system", f"{npc['name']} tidak ingin bicara.")
        return self.view()

    @staticmethod
    def _quest_involves_npc(quest: dict, nid: str) -> bool:
        o = quest.get("objective", {})
        return o.get("npc") == nid or o.get("report_to") == nid

    def _side_objective_met(self, qid: str) -> bool:
        """Cek apakah objektif side quest sudah terpenuhi untuk report."""
        sq = self.reg.quest(qid)
        obj = sq.get("objective", {})
        kind = obj.get("kind")
        if kind == "gather":
            item = obj.get("item", "")
            return self.state.inventory.get(item, 0) >= obj.get("target", 1)
        if kind == "defeat":
            prog = self.state.active_side_quests.get(qid, {})
            return prog.get("defeated", 0) >= obj.get("target", 1)
        if kind == "talk":
            prog = self.state.active_side_quests.get(qid, {})
            return prog.get("talk", 0) >= obj.get("target", 1)
        if kind == "spar":
            return True
        if kind == "reach":
            return self.state.location == obj.get("location")
        return True

    def _offerable_side_for(self, nid: str) -> list[str]:
        out = []
        for sq in self.reg.quests:
            if sq.get("kind") == "side" and self._quest_involves_npc(sq, nid) and self.quest.is_offerable(sq["id"]):
                out.append(sq["id"])
        return out

    def _resolve_dialog(self, npc: dict, forced_node: str | None) -> tuple[str, str | None]:
        """Pilih dialog untuk `talk` berdasarkan konteks — tangga prioritas seragam
        untuk semua NPC (docs/DIALOG_SISTEM_REKOMENDASI.md §5, dialog routing adaptif):

        1. Task quest utama (talk/spar) aktif pada NPC → `routes.main[quest]`
           (+ `start_node` quest dipaksa); fallback dialog umum
        2. Side quest berjalan pada NPC → `routes.side[q].report`
        3. Pertama kali bertemu → `routes.first_meeting` ATAU dialog umum —
           TIDAK pernah side offer/spar/intimacy
        4. Reaksi naratif tertunda → entry kondisional `once` di dialog umum
           belum dimainkan → dialog umum menang atas rutinitas
        5. Side quest repeatable yang bisa ditawarkan → `routes.side[q].offer`
           (iterasi deterministik — urut quest id)
        6. Intimacy tercapai (`relation_min <= relation <= relation_max`) →
           `routes.intimacy.dialog` menggantikan posisi dialog umum
        7. Fallback → dialog umum (`routes.general` alias `default_dialog`)

        Setiap slot ter-rute difilter `can_start` — dialog yang tak punya entry
        terjangkau jatuh ke slot berikutnya (mis. offer ter-gate fase cerita).
        """
        nid = npc["id"]
        routes = npc.get("dialog_routes", {}) or {}
        general = (routes.get("general") or npc.get("default_dialog", "") or "")

        # 1. task quest utama (talk/spar) — menang mutlak atas slot lain
        q = self.quest.current_main()
        if q and q.get("objective", {}).get("kind") in ("talk", "spar") and q["objective"].get("npc") == nid:
            rid = (routes.get("main") or {}).get(q["id"])
            if rid and self.dialog.can_start(rid):
                return rid, forced_node
            return general, forced_node

        # 2. side quest aktif → report (hanya bila objektif terpenuhi)
        for qid in sorted(self.state.active_side_quests):
            sq = self.reg.quest(qid)
            if sq and sq.get("kind") == "side" and self._quest_involves_npc(sq, nid):
                if not self._side_objective_met(qid):
                    nrid = (routes.get("side") or {}).get(qid, {}).get("not_ready")
                    if nrid and self.dialog.can_start(nrid):
                        return nrid, None
                    continue
                rid = (routes.get("side") or {}).get(qid, {}).get("report")
                if rid and self.dialog.can_start(rid):
                    return rid, None
                return general, None

        # 3. pertama kali bertemu — perkenalan; bukan offer/spar/intimacy
        if nid not in self.state.talked_npcs:
            rid = routes.get("first_meeting")
            if rid and self.dialog.can_start(rid):
                return rid, None
            return general, None

        # 4. reaksi naratif tertunda (entry ber-`once` di dialog umum belum
        #    dimainkan) — mendahului offer rutin & intimacy
        if self.dialog.has_pending_once_entry(general):
            return general, None

        # 5. side quest offerable → offer rutin (tie-break deterministik)
        for qid in sorted(self._offerable_side_for(nid)):
            rid = (routes.get("side") or {}).get(qid, {}).get("offer")
            if rid and self.dialog.can_start(rid):
                return rid, None

        # 6. intimacy tercapai → dialog intimacy menggantikan dialog umum
        inti = routes.get("intimacy") or {}
        if inti.get("dialog"):
            rel = self.state.relations.get(nid, 0)
            rmin = inti.get("relation_min", 0)
            rmax = inti.get("relation_max", 100)
            if rmin <= rel <= rmax and self.dialog.can_start(inti["dialog"]):
                return inti["dialog"], None

        # 7. dialog umum (fallback)
        return general, forced_node

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
        if npc_id:
            self.state.talked_npcs.add(npc_id)  # routing: dialog umum hanya saat belum pernah bicara
        # objektif talk — A3: laporkan semua node yang dimainkan (node wajib)
        self.quest.notify_dialog_ended(npc_id or "", getattr(self.dialog, "last_nodes", None))
        # objektif spar: mulai battle melawan NPC
        q = self.quest.current_main()
        obj = q.get("objective", {}) if q else {}
        if q and obj.get("kind") == "spar" and obj.get("npc") == npc_id:
            npc = self.reg.npc(npc_id or "")
            if npc and npc.get("combat"):
                foe = dict(npc["combat"], name=npc["name"], id=npc["id"])
                # Debuff hanya berlaku untuk salinan battle quest ini.
                debuff = obj.get("spar_debuff")
                if debuff:
                    foe["hp"] = max(1, round(int(foe["hp"]) * debuff.get("hp_mult", 1)))
                    foe["hp_max"] = foe["hp"]
                    foe["attack"] = max(1, round(int(foe["attack"]) * debuff.get("atk_mult", 1)))
                    foe["defense"] = max(0, round(int(foe["defense"]) * debuff.get("def_mult", 1)))
                allies = []
                quest_allies = obj.get("allies", [])
                if obj.get("context") == "spar_team":
                    for nid in quest_allies:
                        ally_npc = self.reg.npc(nid)
                        if ally_npc and ally_npc.get("combat"):
                            c = ally_npc["combat"]
                            allies.append({
                                "id": nid,
                                "name": ally_npc["name"],
                                "element": c.get("element"),
                                "hp": int(c["hp"]),
                                "hp_max": int(c["hp"]),
                                "attack": int(c["attack"]),
                                "defense": int(c["defense"]),
                                "speed": int(c.get("speed", 5)),
                            })
                    if not allies:
                        add_log(self.state, "system", "Quest spar tim terkendala: data sekutu NPC tidak lengkap.")
                        return
                ctx = "spar_team" if obj.get("context") == "spar_team" else "spar"
                self.battle.start([foe], ctx, allies=allies or None,
                                  use_companion=ctx != "spar_team")
                self.state.pending_battle["spar_npc"] = npc_id
                return
            add_log(self.state, "system",
                    f"Quest spar terkendala: {npc['name'] if npc else npc_id} tidak punya data pertarungan.")
        # pilihan cabang quest (dialog percabangan)
        if self.state.branch_pending:
            if getattr(self.dialog, "last_dialog_id", None) == self.state.branch_pending:
                self.quest.select_branch(self.dialog.chosen_option or "")
            else:
                self._maybe_start_branch_dialog()

    def _allowed_connections(self, loc: dict) -> list:
        """Filter connections by connection_gates + state.flags."""
        gates = loc.get("connection_gates") or {}
        return [c for c in loc.get("connections", [])
                if not gates.get(c) or self.state.flags.get(gates[c])]

    def _move(self, action: dict) -> dict:
        if self.state.pending_battle or self.state.pending_dialog:
            return self.view()
        to = action.get("to")
        loc = self.reg.location(to)
        cur = self.reg.location(self.state.location)
        if not loc:
            add_log(self.state, "system", "Lokasi tidak dikenal.")
            return self.view()
        if to not in self._allowed_connections(cur):
            gates = cur.get("connection_gates") or {}
            flag_key = gates.get(to)
            if flag_key:
                add_log(self.state, "system", f"Kau harus menyelesaikan urusan di sini dulu sebelum pergi ke {loc['name']}.")
            else:
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
        if self.state.pending_battle or self.state.pending_dialog:
            return self.view()
        hours = max(1, int(action.get("hours", 1)))
        self._pass_time(hours)
        return self.view()

    def _pass_time(self, hours: int) -> None:
        self.state.hour += hours
        while self.state.hour >= 24:
            self.state.hour -= 24
            self.state.day += 1
            # fatigue: jika tidak istirahat hari ini, naikkan fatigue
            if not self.state.rested_today:
                self.state.fatigue_days += 1
                rest_cfg = self.reg.config.get("rest") or {}
                hp_pen = int(rest_cfg.get("hp_penalty_per_day", 2))
                max_pen = int(rest_cfg.get("max_hp_penalty", 20))
                cur_penalty = min(self.state.fatigue_days * hp_pen, max_pen)
                add_log(self.state, "system",
                        f"[Sistem] Kau tidak beristirahat. Fatigue naik (+{hp_pen} HP penalty, total -{cur_penalty} HP max). "
                        f"Istirahatlah di kamarmu untuk memulihkan tenaga.")
                if cur_penalty >= max_pen:
                    add_log(self.state, "system",
                            "[Sistem] ⚠ Kau kelelahan total! Stat secara permanen menyusut. Segera istirahat!")
            self.state.rested_today = False
            expired = tick_status_effects(self.state)
            for etype in expired:
                add_log(self.state, "system", f"[Sistem] Efek sementara habis: {etype}.")
            self.state.daily_spar_counts = {}
            # reset weekly meditation counter
            if self.state.day - self.state.meditate_week_start >= 7:
                self.state.meditate_week_count = 0
                self.state.meditate_week_start = self.state.day
        self.quest.notify_move()
        self.quest.advance_time_target_met()
        self.quest.check_timeouts()
        self._maybe_start_branch_dialog()

    def _time_cost(self, action_type: str) -> int:
        """Jam yang dibutuhkan aksi dari config. Default 0 (instant)."""
        costs = self.reg.config.get("cultivation", {}).get("time_costs", {})
        return int(costs.get(action_type, 0))

    def _check_time_budget(self, cost: int) -> str | None:
        """Cek sisa waktu cukup. Return error msg atau None."""
        remaining = 24 - self.state.hour
        if remaining < cost:
            return f"Waktu tidak cukup. Sisa {remaining} jam, butuh {cost} jam."
        return None
    def _choose(self, action: dict) -> dict:
        if self.state.pending_battle or self.state.pending_dialog:
            return self.view()
        self.quest.resolve_choose(action.get("option", ""))
        self._maybe_start_branch_dialog()
        return self.view()

    def _equip(self, action: dict) -> dict:
        """Pasang senjata ke slot equipment.weapon (ENGINE_ARCHITECTURE §9.3)."""
        if self.state.pending_battle or self.state.pending_dialog:
            return self.view()
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
        # pil_sukses/pil_aman: set flags, don't consume normally
        if iid == "pil_sukses":
            self.state.pil_sukses_active = True
            add_log(self.state, "narration", f"Memakai {it['name']}. Peluang meditasi +30%!")
            self.quest.notify_gather()
            return self.view()
        if iid == "pil_aman":
            self.state.pil_aman_active = True
            add_log(self.state, "narration", f"Memakai {it['name']}. Gagal meditasi tanpa debuff!")
            self.quest.notify_gather()
            return self.view()
        hp = int(it.get("hp_restore", 0))
        qi = int(it.get("qi_restore", 0))
        exp_val = int(it.get("exp_value") or 0)
        self.state.player.hp = min(self.state.max_hp(self.reg), self.state.player.hp + hp)
        self.state.player.qi = min(self.state.max_qi(self.reg), self.state.player.qi + qi)
        if exp_val > 0:
            gain_exp(self.state, self.reg, exp_val)
        parts = []
        if hp > 0:
            parts.append(f"+{hp} HP")
        if qi > 0:
            parts.append(f"+{qi} Qi")
        if exp_val > 0:
            parts.append(f"+{exp_val} dantian exp")
        desc = ", ".join(parts) if parts else "dikonsumsi"
        add_log(self.state, "narration", f"Memakai {it['name']} ({desc}).")
        self.quest.notify_gather()
        return self.view()

    def _use_key_item(self, action: dict) -> dict:
        """Gunakan key_item — terapkan use_effects dari data."""
        iid = action.get("item")
        if self.state.inventory.get(iid, 0) < 1:
            add_log(self.state, "system", "Item tidak tersedia.")
            return self.view()
        it = self.reg.item(iid)
        if not it or it.get("type") != "key_item":
            add_log(self.state, "system", "Item itu bukan kunci.")
            return self.view()
        ki_data = self.reg.key_items.get(iid)
        if not ki_data or not ki_data.get("use_effects"):
            add_log(self.state, "system", "Item itu tidak bisa dipakai saat ini.")
            return self.view()
        apply_effects(self.state, self.reg, ki_data["use_effects"])
        if ki_data.get("consumed", False):
            self.state.inventory[iid] -= 1
            if self.state.inventory[iid] <= 0:
                del self.state.inventory[iid]
        desc = ki_data.get("description", it["name"])
        add_log(self.state, "narration", f"Memakai {it['name']}: {desc}")
        self.quest.notify_gather()
        return self.view()

    def _meditate(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Meditasi hanya bisa dilakukan di lokasi aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        weekly_limit = self.reg.config.get("cultivation", {}).get("meditate_weekly_limit", 3)
        if self.state.meditate_week_count >= weekly_limit:
            msg = f"Sudah meditasi {weekly_limit} kali minggu ini. Tunggu minggu depan."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        result = meditate(self.state, self.reg)
        self.state.meditate_week_count += 1
        if self.state.meditate_week_start == 0:
            self.state.meditate_week_start = self.state.day
        self.state.pil_sukses_active = False
        self.state.pil_aman_active = False
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
        if self.npc_location(npc) != self.state.location:
            add_log(self.state, "system", f"{npc['name']} tidak ada di sini.")
            return self.view()
        foe = dict(npc["combat"], name=npc["name"], id=npc["id"])
        self.battle.start([foe], "spar")
        self.state.pending_battle["spar_npc"] = npc["id"]
        return self.view()

    def _hunt(self, action: dict) -> dict:
        zones = self.reg.hunts_for_location(self.state.location)
        if not zones:
            add_log(self.state, "system", "Berburu belum tersedia di sini.")
            return self.view()
        cost = self._time_cost("hunt")
        err = self._check_time_budget(cost)
        if err:
            add_log(self.state, "system", err)
            res = self.view()
            res["error"] = err
            return res
        # pilih zona (explicit id atau default pertama)
        hunt_id = action.get("hunt")
        hunt = None
        if hunt_id:
            hunt = next((z for z in zones if z.get("id") == hunt_id), None)
            if not hunt:
                add_log(self.state, "system", f"Zona berburu '{hunt_id}' tidak ditemukan di sini. Menggunakan zona default.")
                hunt = zones[0]
        else:
            hunt = zones[0]
        # pool
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
        if random.random() < float(hunt.get("mini_boss_chance", 0.1)):
            pool = [hunt["mini_boss"]] if hunt.get("mini_boss") else pool
        eid = random.choice(pool)
        foe = self.reg.enemy(eid)
        if not foe:
            add_log(self.state, "system", "Tidak ada mangsa di sini.")
            return self.view()
        # cooldown per zona
        respawn_hours = self.reg.config.get("world", {}).get("monster_respawn_hours", 5)
        now_abs_hours = self.state.absolute_hours
        if self.state.last_hunt_time is None:
            self.state.last_hunt_time = {}
        last = self.state.last_hunt_time.get(hunt["id"])
        if last is not None and (now_abs_hours - last) < respawn_hours:
            remaining = respawn_hours - (now_abs_hours - last)
            add_log(self.state, "system", f"Wilayah masih sepi. Monster baru muncul kembali dalam {remaining} jam.")
            return self.view()
        self.state.last_hunt_time[hunt["id"]] = now_abs_hours
        self._pass_time(cost)
        self.battle.start([foe], "hunt")
        return self.view()

    def _search(self, action: dict) -> dict:
        zones = self.reg.hunts_for_location(self.state.location)
        if not zones:
            add_log(self.state, "system", "Mencari belum tersedia di sini.")
            return self.view()
        cost = self._time_cost("search")
        err = self._check_time_budget(cost)
        if err:
            add_log(self.state, "system", err)
            res = self.view()
            res["error"] = err
            return res
        hunt = zones[0]
        search_items = hunt.get("search_items")
        if not search_items:
            # backward compat: old search_item string
            old_item = hunt.get("search_item")
            if old_item:
                search_items = [{"item": old_item, "chance": 0.6, "min": 1, "max": 1}]
            else:
                add_log(self.state, "system", "Tidak ada yang bisa dicari di sini.")
                return self.view()
        found = []
        for si in search_items:
            if random.random() < float(si.get("chance", 0.5)):
                count = random.randint(int(si.get("min", 1)), int(si.get("max", 1)))
                iid = si["item"]
                self.state.inventory[iid] = self.state.inventory.get(iid, 0) + count
                it = self.reg.item(iid)
                nama = it.get("name", iid) if it else iid
                found.append(f"{count}× {nama}")
        if found:
            add_log(self.state, "narration", f"Kau menemukan: {', '.join(found)}.")
            self.quest.notify_gather()
        else:
            add_log(self.state, "narration", "Kau mencari-cari, tapi tidak menemukan apa pun.")
        self._pass_time(cost)
        return self.view()

    def _mine(self, action: dict) -> dict:
        mines = self.reg.mines_for_location(self.state.location)
        if not mines:
            add_log(self.state, "system", "Menambang belum tersedia di sini.")
            return self.view()
        cost = self._time_cost("mine")
        err = self._check_time_budget(cost)
        if err:
            add_log(self.state, "system", err)
            res = self.view()
            res["error"] = err
            return res
        mine = mines[0]
        pool = mine.get("pool", [])
        if not pool:
            add_log(self.state, "system", "Tidak ada mineral di sini.")
            return self.view()
        found = []
        for entry in pool:
            if random.random() < float(entry.get("chance", 0.5)):
                count = random.randint(int(entry.get("min", 1)), int(entry.get("max", 1)))
                iid = entry["item"]
                self.state.inventory[iid] = self.state.inventory.get(iid, 0) + count
                it = self.reg.item(iid)
                nama = it.get("name", iid) if it else iid
                found.append(f"{count}× {nama}")
        if found:
            add_log(self.state, "narration", f"Kau menambang: {', '.join(found)}.")
            self.quest.notify_gather()
        else:
            add_log(self.state, "narration", "Kau menambang, tapi tidak menemukan mineral yang berguna.")
        self._pass_time(cost)
        return self.view()

    def _rest(self, action: dict) -> dict:
        rest_loc = (self.reg.config.get("rest") or {}).get("rest_location", "loc_protagonist_room")
        if self.state.location != rest_loc:
            msg = "Istirahat hanya bisa dilakukan di kamarmu."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        hours = max(1, int((self.reg.config.get("rest") or {}).get("rest_hours", 8)))
        self.state.rested_today = True
        self.state.fatigue_days = 0
        self._pass_time(hours)
        self.state.player.hp = self.state.max_hp(self.reg)
        self.state.player.qi = self.state.max_qi(self.reg)
        # kompanion KO bangkit kembali (§9.4)
        revived = False
        comp_name = None
        for c in self.state.companions:
            if not c.get("active"):
                cid = c["id"]
                comp = next((x for x in self.reg.companions if x.get("id") == cid), None)
                if comp:
                    scale = self.reg.config.get("companion", {})
                    hp_max = int(comp.get("base_hp", 10)) + self.state.player.realm_level * int(scale.get("hp_per_level", 12))
                    c["active"] = True
                    c["hp"] = hp_max
                    revived = True
                    comp_name = comp["name"]
                    break
        if self.state.companions:
            active_id = self.state.active_companion
            active_entry = next((c for c in self.state.companions if c.get("id") == active_id), None)
            if active_entry:
                self.state.companion = active_entry
        msg = f"Kau beristirahat selama {hours} jam di kamarmu. HP & Qi pulih penuh. Kekuatanmu kembali."
        if revived and comp_name:
            msg += f" {comp_name} bangkit kembali."
        add_log(self.state, "narration", msg)
        self.quest.notify_rest()
        return self.view()

    def _switch_companion(self, action: dict) -> dict:
        """Ganti kompanion aktif — hanya di lokasi aman."""
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            add_log(self.state, "system", "Hanya bisa mengganti kawan di lokasi aman.")
            return self.view()
        cid = action.get("companion")
        if not cid:
            add_log(self.state, "system", "Pilih kawan yang ingin diganti.")
            return self.view()
        entry = next((c for c in self.state.companions if c.get("id") == cid), None)
        if not entry:
            add_log(self.state, "system", "Kawan itu tidak ada di rombonganmu.")
            return self.view()
        if entry.get("hp", 0) <= 0:
            add_log(self.state, "system", "Kawan itu sedang pingsan. Istirahatkan dulu.")
            return self.view()
        self.state.active_companion = cid
        comp = next((x for x in self.reg.companions if x.get("id") == cid), None)
        name = comp["name"] if comp else cid
        add_log(self.state, "narration", f"{name} menjadi kawan aktifmu.")
        # backward compat
        self.state.companion = entry
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
        name = it["name"] if it else iid
        add_log(self.state, "narration", f"Membeli {count}× {name} ({cost} Koin Emas).")
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
        name = it["name"] if it else iid
        add_log(self.state, "narration", f"Menjual {count}× {name} (+{gold} Koin Emas).")
        return self.view()

    def _craft(self, action: dict) -> dict:
        loc = self.reg.location(self.state.location)
        if not loc or not loc.get("is_safe"):
            msg = "Meracik hanya bisa dilakukan di titik aman."
            add_log(self.state, "system", msg)
            res = self.view()
            res["error"] = msg
            return res
        cost = self._time_cost("craft")
        err = self._check_time_budget(cost)
        if err:
            add_log(self.state, "system", err)
            res = self.view()
            res["error"] = err
            return res
        rid = action.get("recipe")
        recipe = next((r for r in self.reg.recipes if r["id"] == rid), None)
        if not recipe:
            add_log(self.state, "system", "Resep tidak dikenal.")
            return self.view()
        # check recipe_item (key_item) is owned
        recipe_item_id = recipe.get("recipe_item")
        if recipe_item_id and self.state.inventory.get(recipe_item_id, 0) < 1:
            add_log(self.state, "system", "Kau belum memiliki resep ini.")
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
        self._pass_time(cost)
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

    def _unlock_technique(self, action: dict) -> dict:
        """Unlock technique evolution — REPLACE semantics.
        Base technique is REMOVED, variant takes its place.
        Only 1 variant per branch_group allowed.
        
        Action: {"type": "unlock_technique", "technique": "teknik_xxx"}
        """
        tid = action.get("technique")
        tek = self.reg.technique(tid)
        if not tek:
            add_log(self.state, "system", "Teknik tidak dikenal.")
            return self.view()
        # Must have evolves_from (this is an evolution technique)
        evolves_from = tek.get("evolves_from", "")
        if not evolves_from:
            add_log(self.state, "system", f"{tek['name']} bukan teknik evolusi.")
            return self.view()
        # Must own the base technique
        if evolves_from not in self.state.player.techniques:
            add_log(self.state, "system", f"Kau belum menguasai {evolves_from}.")
            return self.view()
        # Check branch_group: only 1 variant per group
        branch_group = tek.get("branch_group", "")
        if branch_group:
            existing_variants = [
                t for t in self.state.player.techniques
                if self.reg.technique(t) and self.reg.technique(t).get("branch_group") == branch_group
            ]
            if existing_variants:
                add_log(self.state, "system",
                        f"Kau sudah memilih evolusi lain di branch '{branch_group}'.")
                return self.view()
        # REPLACE: remove base, add variant
        self.state.player.techniques.remove(evolves_from)
        self.state.player.techniques.append(tid)
        # Carry over technique level (min of base level, max for new realm)
        base_level = int(self.state.player.technique_levels.pop(evolves_from, 1))
        realm = self.reg.realm_by_id(self.state.player.realm)
        max_lvl = (int(realm.get("order", 1)) + 1) if realm else 2
        self.state.player.technique_levels[tid] = min(base_level, max_lvl)
        add_log(self.state, "narration",
                f"{tek['name']} menggantikan {evolves_from} — evolusi teknik!")
        return self.view()

    def _fuse_technique(self, action: dict) -> dict:
        """Fusion: combine 2 techniques into 1 stronger technique.
        Progression chain: jianxin + badai_api → pedang_api_membara → pamungkas_wuxing.
        
        Action: {"type": "fuse_technique", "fusion_id": "fusion_xxx"}
        """
        fusion_id = action.get("fusion_id")
        recipe = next((f for f in self.reg.fusions if f.get("id") == fusion_id), None)
        if not recipe:
            add_log(self.state, "system", "Resep fusion tidak dikenal.")
            return self.view()
        # Check realm requirement
        req_realm = recipe.get("realm_required", "")
        if req_realm:
            cur_realm = self.reg.realm_by_id(self.state.player.realm)
            req_realm_data = self.reg.realm_by_id(req_realm)
            cur_order = int(cur_realm.get("order", 0)) if cur_realm else 0
            req_order = int(req_realm_data.get("order", 0)) if req_realm_data else 0
            if cur_order < req_order:
                add_log(self.state, "system",
                        f"Fusion ini membutuhkan ranah {req_realm} atau lebih tinggi.")
                return self.view()
        # Check if player already has the result technique
        result_id = recipe.get("result", "")
        if result_id in self.state.player.techniques:
            add_log(self.state, "system",
                    f"Kau sudah memiliki teknik hasil fusion.")
            return self.view()
        # Check all required techniques are owned
        requires = recipe.get("requires", [])
        owned = set(self.state.player.techniques)
        missing = [r for r in requires if r not in owned]
        if missing:
            add_log(self.state, "system",
                    f"Kau belum menguasai: {', '.join(missing)}.")
            return self.view()
        # Check technique levels
        req_level = int(recipe.get("requires_level", 1))
        for r in requires:
            lvl = int(self.state.player.technique_levels.get(r, 1))
            if lvl < req_level:
                tek = self.reg.technique(r)
                name = tek.get("name", r) if tek else r
                add_log(self.state, "system",
                        f"{name} butuh Lv.{req_level} untuk fusion (saat ini Lv.{lvl}).")
                return self.view()
        # Check result technique exists
        result_id = recipe.get("result", "")
        result_tek = self.reg.technique(result_id)
        if not result_tek:
            add_log(self.state, "system",
                    f"Teknik hasil fusion '{result_id}' tidak ditemukan.")
            return self.view()
        # Hitung level MINIMUM dari teknik yang di-fuse SEBELUM pop
        min_level = min(int(self.state.player.technique_levels.get(r, 1)) for r in requires) if requires else 1
        # FUSION: remove requirements, add result
        for r in requires:
            self.state.player.techniques.remove(r)
            self.state.player.technique_levels.pop(r, None)
        self.state.player.techniques.append(result_id)
        # Result level = max(2, min_level), capped at realm max
        realm = self.reg.realm_by_id(self.state.player.realm)
        max_lvl = (int(realm.get("order", 1)) + 1) if realm else 2
        self.state.player.technique_levels[result_id] = min(max(2, min_level), max_lvl)
        add_log(self.state, "narration",
                f"Fusion berhasil! {result_tek.get('name', result_id)} lahir dari gabungan teknik.")
        return self.view()

    def _merchant_here(self) -> dict | None:
        for n in self.reg.npcs:
            if n.get("shop") and self._is_npc_available(n) and self.npc_location(n) == self.state.location:
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
        """Tampilan UI lengkap — location, player, quests, inventory, dll."""
        self._maybe_start_branch_dialog()
        s = self.state
        loc = self.reg.location(s.location)
        q = self.quest.current_main()
        pc = player_combat(s, self.reg)
        realm = self.reg.realms.get(s.player.realm) or {"name_pinyin": s.player.realm, "name": s.player.realm, "order": "1"}
        
        # arc_summary data-driven (B1): arc TERAKHIR di config yang final quest-nya selesai
        arc_summary = None
        for arc in reversed(self.reg.config.get("arcs", [])):
            if arc.get("final_quest") not in s.completed_quests:
                continue
            # B1: pilihan akhir arc — data-driven `arcs[].branches` {flag: label}.
            # - flag boolean True → label
            # - flag bernilai string (enum, mis. state_identity_stance) → nilai humanized
            # - `state_pavilion` (docs 13) = akademi pemain (player.academy, bukan flags)
            chosen_branch = "Tidak Diketahui"
            for flag, label in (arc.get("branches") or {}).items():
                if flag == "state_pavilion":
                    if s.player.academy:
                        chosen_branch = next(
                            (a.get("name", a.get("id", s.player.academy))
                             for a in self.reg.config.get("academies", [])
                             if a.get("id") == s.player.academy),
                            s.player.academy)
                        break
                    continue
                val = s.flags.get(flag)
                if val is True:
                    chosen_branch = label
                    break
                if isinstance(val, str) and val:
                    chosen_branch = val.replace("_", " ").title()
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
                "id": loc["id"], "name": loc["name"],
                # F1.2: description opsional (pola .get sama seperti is_safe/connections/ambience)
                "description": loc.get("description", ""),
                "is_safe": loc.get("is_safe", False), "connections": self._allowed_connections(loc),
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
                "dantian_exp": s.player.dantian_exp,
                "dantian_capacity": int(realm.get("dantian_capacity", 20)),
                "hp": pc["hp"], "hp_max": pc["hp_max"],
                "qi": pc["qi"], "qi_max": pc["qi_max"],
                "gold": s.player.gold,
                "roots": (self.reg.roots_tier.get(s.player.roots) or {}).get("name", s.player.roots),
                "academy": s.player.academy,
                "morality": s.player.morality,
                "equipment": s.player.equipment,
                "realms_unlocked": s.realms_unlocked,
                "status_effects": [
                    {"type": e.get("type", "unknown"), "days_left": e.get("days_left", 0)}
                    for e in s.status_effects
                ],
                "meditate_week_count": s.meditate_week_count,
                "pil_sukses_active": s.pil_sukses_active,
                "pil_aman_active": s.pil_aman_active,
                "fatigue_days": s.fatigue_days,
                "rested_today": s.rested_today,
                "element_mastery": dict(s.element_mastery),
                "is_rest_location": s.location == (self.reg.config.get("rest") or {}).get("rest_location", "loc_protagonist_room"),
            },
            "current_quest": {"id": q["id"], "title": q["title"], "objective": self.quest.objective_text(q)} if q else None,
            "side_quests": [
                {"id": sq["id"], "title": sq["title"], "objective": self.quest.objective_text(sq)}
                for sq in self.quest.active_side()
            ],
            # audit Claude: lookup item SEKALI per baris (view() dipanggil tiap
            # tick UI — double lookup adalah pemborosan murni). Bentuk generator
            # bersarang (bukan walrus) — konsisten gaya codebase (tanpa `:=`).
            "inventory": [
                {"id": iid, "name": it["name"], "count": c,
                 "type": it.get("type", "")}
                for iid, c, it in (
                    (iid, c, self.reg.item(iid)) for iid, c in sorted(s.inventory.items())
                )
                if it
            ],
            "memories": [
                {"id": m["id"] if isinstance(m, dict) else m,
                 "title": (self.reg.memory(m["id"] if isinstance(m, dict) else m) or {}).get("title", ""),
                 "reliability": m.get("reliability", "unknown") if isinstance(m, dict) else "unknown"}
                for m in s.memories
                if self.reg.memory(m["id"] if isinstance(m, dict) else m)
            ],
            "companion": companion_stats(s, self.reg),
            "companions": [
                {"id": c["id"],
                 "name": (next((x for x in self.reg.companions if x.get("id") == c["id"]), None) or {}).get("name", c["id"]),
                 "hp": c.get("hp", 0),
                 "hp_max": int((next((x for x in self.reg.companions if x.get("id") == c["id"]), None) or {}).get("base_hp", 10)) + s.player.realm_level * int((self.reg.config.get("companion") or {}).get("hp_per_level", 12)),
                 "active": c.get("active", True),
                 "selected": c["id"] == s.active_companion}
                for c in s.companions
            ],
            "active_companion": s.active_companion,
            "recipes": [
                {"id": r["id"], "name": r.get("name", r["id"]),
                 "ingredients": [{"item": ing["item"], "count": ing["count"]}
                                 for ing in r.get("ingredients", [])],
                 "result": r.get("result", ""), "count": r.get("count", 1)}
                for r in self.reg.recipes
                if s.inventory.get(r.get("recipe_item", ""), 0) > 0
            ],
            "mode": self._mode(),
            "dialog": self.dialog.view() if s.pending_dialog else None,
            "battle": self.battle.view() if s.pending_battle else None,
            "choose": self._choose_view(),
            "log": s.log,
            "arc_summary": arc_summary,
            # faksi: id + skor + nama dari data (bila factions.json ada;
            # fallback id apa adanya — tema tanpa registri faksi tetap jalan)
            "factions": [
                {"id": fid, "score": v,
                 "name": (self.reg.faction_by_id.get(fid) or {}).get("name", fid)}
                for fid, v in s.factions.items()
            ],
        }

    def _pick_ending(self, s, arc: dict) -> dict | None:
        """C3: pilih ending dari `config.arcs[].endings` — ending pertama yang
        kondisinya cocok (first-match, AND — pola `_eval_condition` dipakai ulang
        apa adanya). Murni data-driven (flag/relation/faksi/memory), TIDAK
        berbasis skala moralitas. Tanpa `endings` → None (kontrak view lama)."""
        for end in arc.get("endings") or []:
            cond = end.get("condition") or {}
            if DialogEngine._eval_condition(s, cond, self.reg):
                return {"id": end.get("id", "?"), "title": end.get("title", ""), "desc": end.get("desc", "")}
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
