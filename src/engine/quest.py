"""Quest engine (DAG) — ENGINE_ARCHITECTURE §6.

Invariant:
- Tepat satu quest utama aktif; quest berikutnya muncul setelah yang aktif selesai.
- Quest dengan >1 sisi `next` = titik percabangan → dialog pilihan (choice_id);
  opsi yang dipilih menentukan cabang. Beberapa quest menunjuk quest sama = konvergensi.
- Quest sampingan boleh aktif bersamaan; quest utama sampingan dilarang bertabrakan
  dengan quest utama (diverifikasi validator).
"""

from __future__ import annotations

from ..loader import DataRegistry
from .cultivation import gain_exp, gain_grind_exp
from .effects import apply as apply_effects
from .events import add_log
from .memory import unlock as unlock_memory
from .state import GameState

OBJECTIVE_KINDS = {"talk", "defeat", "gather", "reach", "choose", "spar", "advance_time"}


class QuestEngine:
    def __init__(self, registry: DataRegistry, state: GameState) -> None:
        self.reg = registry
        self.state = state

    # ---------- akses ----------

    def current_main(self) -> dict | None:
        if not self.state.current_quest:
            return None
        return self.reg.quest(self.state.current_quest)

    def active_side(self) -> list[dict]:
        # catatan progres quest utama (mis. talk/advance_time) juga ada di
        # active_side_quests — hanya quest ber-kind side yang ditampilkan
        return [self.reg.quest(qid) for qid in self.state.active_side_quests
                if (self.reg.quest(qid) or {}).get("kind") == "side"]

    def objective_text(self, quest: dict) -> str:
        obj = quest.get("objective", {})
        hint = obj.get("hint", "")
        kind = obj.get("kind")
        if kind == "talk":
            npc = self.reg.npc(obj.get("npc", ""))
            return f"{hint} ({self._talk_count(quest)}/{obj.get('target', 1)})"
        if kind == "defeat":
            base = f"{hint} ({self.state.active_side_quests.get(quest['id'], {}).get('defeated', 0)}/{obj.get('target', 1)})"
            if obj.get("report_to"):
                npc = self.reg.npc(obj["report_to"])
                nama = npc["name"] if npc else obj["report_to"]
                lapor = "✓" if self.state.active_side_quests.get(quest["id"], {}).get("talk", 0) else "—"
                return f"{base} · lapor ke {nama} ({lapor})"
            return base
        if kind == "gather":
            return f"{hint} ({self.state.inventory.get(obj.get('item', ''), 0)}/{obj.get('target', 1)})"
        if kind == "reach":
            return hint
        if kind == "advance_time":
            return hint
        if kind == "choose":
            return hint
        if kind == "spar":
            return hint
        return hint

    def _talk_count(self, quest: dict) -> int:
        return self.state.active_side_quests.get(quest["id"], {}).get("talk", 0)

    # ---------- selesaikan quest utama ----------

    def notify_dialog_ended(self, npc_id: str) -> None:
        """Dipanggil sesi saat dialog berakhir — memeriksa objektif talk & lapor side quest."""
        q = self.current_main()
        if q and q.get("objective", {}).get("kind") == "talk" and q.get("objective", {}).get("npc") == npc_id:
            qid = q["id"]
            prog = self.state.active_side_quests.setdefault(qid, {})
            prog["talk"] = prog.get("talk", 0) + 1
            if prog["talk"] >= q["objective"].get("target", 1):
                self._complete_main(qid)
        # A2 (keputusan §17): side quest defeat dengan `report_to` selesai saat lapor ke pemberi
        for qid in list(self.state.active_side_quests):
            sq = self.reg.quest(qid)
            obj = sq.get("objective", {})
            if obj.get("kind") == "defeat" and obj.get("report_to") == npc_id:
                prog = self.state.active_side_quests[qid]
                prog["talk"] = prog.get("talk", 0) + 1
                if prog.get("defeated", 0) >= obj.get("target", 1):
                    self._complete_side(qid)

    def notify_spar_won(self, npc_id: str) -> None:
        """Objektif `spar` selesai saat pemain MENANG battle melawan NPC itu."""
        q = self.current_main()
        if q and q.get("objective", {}).get("kind") == "spar" and q.get("objective", {}).get("npc") == npc_id:
            self._complete_main(q["id"])

    def notify_spar_loss(self, npc_id: str) -> None:
        """G4a: kalah sparring tetap menyelesaikan objektif `spar` (dialog berbeda,
        sesuai STORY_FASE1 #19) — tanpa game over permanen; penalti KO tetap berlaku."""
        q = self.current_main()
        if q and q.get("objective", {}).get("kind") == "spar" and q.get("objective", {}).get("npc") == npc_id:
            self.state.flags["spar_kalah"] = True
            self._complete_main(q["id"])

    def notify_move(self) -> None:
        q = self.current_main()
        if not q or q.get("objective", {}).get("kind") != "reach":
            return
        obj = q["objective"]
        if obj.get("location") != self.state.location:
            return
        tw = obj.get("time_window")
        if tw and not self._in_window(tw):
            return
        self._complete_main(q["id"])

    def notify_battle_won(self, defeated_enemy_ids: list[str]) -> None:
        """Pembunuhan musuh (berburu) — progres objektif defeat side quest."""
        q = self.current_main()
        if q and q.get("objective", {}).get("kind") == "defeat":
            self._complete_main(q["id"])
        for qid in list(self.state.active_side_quests):
            sq = self.reg.quest(qid)
            obj = sq.get("objective", {})
            if obj.get("kind") != "defeat":
                continue
            allowed = obj.get("enemies", [])
            killed = [e for e in defeated_enemy_ids if e in allowed]
            if killed:
                prog = self.state.active_side_quests[qid]
                prog["defeated"] = prog.get("defeated", 0) + len(killed)
                # A2: dengan `report_to`, selesaian butuh lapor ke pemberi — bukan langsung selesai
                if not obj.get("report_to") and prog["defeated"] >= obj.get("target", 1):
                    self._complete_side(qid)

    def notify_gather(self) -> None:
        for qid in list(self.state.active_side_quests):
            sq = self.reg.quest(qid)
            obj = sq.get("objective", {})
            if obj.get("kind") == "gather":
                have = self.state.inventory.get(obj.get("item", ""), 0)
                if have >= obj.get("target", 1):
                    self._complete_side(qid)

    def _in_window(self, tw: dict) -> bool:
        start = tw.get("hour_start", 0)
        end = tw.get("hour_end", 24)
        h = self.state.hour
        if start <= end:
            return start <= h < end
        return h >= start or h < end  # lintas tengah malam (mis. 19 → 6)

    # ---------- lanjutkan DAG ----------

    def resolve_choose(self, option: str) -> None:
        """Objektif `choose` (mis. pilih akademi) — set nilai lalu selesaikan."""
        q = self.current_main()
        if not q or q.get("objective", {}).get("kind") != "choose":
            return
        obj = q["objective"]
        matched = False
        if obj.get("options"):
            for o in obj["options"]:
                if o.get("value") == option:
                    self.state.player.academy = option
                    matched = True
                    break
        if matched:
            self._grant_companion(option)
            self._complete_main(q["id"])
        else:
            add_log(self.state, "system", "Pilihan tidak valid.")

    def _grant_companion(self, academy: str) -> None:
        """Akademi dengan field `companion` di config (data-driven) memberi binatang roh."""
        cid = None
        for a in self.reg.config.get("academies", []):
            if a["id"] == academy:
                cid = a.get("companion")
                break
        if not cid:
            return
        comp = next((c for c in self.reg.companions if c["id"] == cid), None)
        if not comp:
            return
        scale = self.reg.config.get("companion", {})
        hp_max = int(comp["base_hp"]) + self.state.player.realm_level * int(scale.get("hp_per_level", 12))
        self.state.companion = {"id": cid, "hp": hp_max, "active": True}
        add_log(self.state, "narration", f"{comp['name']} mendekat dan menempel padamu — binatang roh akademimu.")

    def advance_time_target_met(self) -> None:
        q = self.current_main()
        if not q or q.get("objective", {}).get("kind") != "advance_time":
            return
        obj = q["objective"]
        qid = q["id"]
        prog = self.state.active_side_quests.get(qid)
        if prog is None:
            self._note_main_start(qid)
            prog = self.state.active_side_quests[qid]
        elapsed_hours = (self.state.day - prog["start_day"]) * 24 + (self.state.hour - prog["start_hour"])
        required_hours = obj.get("day_offset", 0) * 24
        if elapsed_hours >= required_hours and self.state.hour >= obj.get("hour", 0):
            self._complete_main(qid)

    def _complete_main(self, qid: str) -> None:
        if self.state.current_quest != qid:
            return
        q = self.reg.quest(qid)
        oc = q.get("on_complete", {})
        apply_effects(self.state, self.reg, oc.get("effects"))
        unlock_memory(self.state, self.reg, oc.get("memory_unlock"))
        rewards = oc.get("rewards", {})
        gain_exp(self.state, self.reg, rewards.get("exp", 0))
        self.state.player.gold += rewards.get("gold", 0)
        if oc.get("system_msg"):
            add_log(self.state, "system", oc["system_msg"])
        add_log(self.state, "narration", f"✓ Quest selesai: {q['title']}.")
        self.state.completed_quests.append(qid)
        self.state.active_side_quests.pop(qid, None)
        if q.get("kind") == "main":
            self.state.current_quest = None
            self._advance_main(q)

    def _advance_main(self, q: dict) -> None:
        nexts = q.get("next", [])
        if not nexts:
            return
        if len(nexts) == 1:
            self.state.current_quest = nexts[0]["quest"]
            self._note_main_start(self.state.current_quest)
            return
        # percabangan: minta dialog pilihan; opsi = cabang
        cid = nexts[0].get("choice_id")
        self.state.branch_pending = cid

    def _note_main_start(self, qid: str) -> None:
        """Catat hari/jam quest utama mulai aktif (untuk objektif advance_time)."""
        self.state.active_side_quests[qid] = {
            "start_day": self.state.day,
            "start_hour": self.state.hour,
        }

    def select_branch(self, option: str) -> None:
        """Setelah dialog percabangan selesai — pilih cabang berdasarkan opsi."""
        q = self.reg.quest(self.state.completed_quests[-1]) if self.state.completed_quests else None
        if not q:
            return
        for edge in q.get("next", []):
            if edge.get("option") == option:
                self.state.current_quest = edge["quest"]
                self._note_main_start(self.state.current_quest)
                self.state.branch_pending = None
                return
        self.state.branch_pending = None

    # ---------- quest sampingan ----------

    def is_offerable(self, qid: str) -> bool:
        sq = self.reg.quest(qid)
        if not sq or sq.get("kind") != "side":
            return False
        if qid in self.state.active_side_quests:
            return False
        if qid in self.state.completed_quests and not sq.get("repeatable"):
            return False
        cd = sq.get("cooldown", 0)
        if cd > 0 and qid in self.state.side_quest_cooldowns:
            now_abs_hours = self.state.absolute_hours
            last_completed = self.state.side_quest_cooldowns[qid]
            if (now_abs_hours - last_completed) < cd:
                return False
        af = sq.get("available_from")
        if af:
            if self.state.day < af.get("day", 1):
                return False
            if self.state.day == af.get("day", 1) and self.state.hour < af.get("hour", 0):
                return False
        return True

    def start_side(self, qid: str) -> bool:
        if not self.is_offerable(qid):
            return False
        self.state.active_side_quests[qid] = {}
        sq = self.reg.quest(qid)
        add_log(self.state, "narration", f"→ Quest sampingan aktif: {sq['title']}.")
        return True

    def _complete_side(self, qid: str) -> None:
        if qid not in self.state.active_side_quests:
            return
        now_abs_hours = self.state.absolute_hours
        self.state.side_quest_cooldowns[qid] = now_abs_hours
        q = self.reg.quest(qid)
        oc = q.get("on_complete", {})
        apply_effects(self.state, self.reg, oc.get("effects"))
        rewards = oc.get("rewards", {})
        gain_grind_exp(self.state, self.reg, rewards.get("exp", 0))  # A2: cap grind harian
        self.state.player.gold += rewards.get("gold", 0)
        if oc.get("system_msg"):
            add_log(self.state, "system", oc["system_msg"])
        add_log(self.state, "narration", f"✓ Quest sampingan selesai: {q['title']}.")
        self.state.completed_quests.append(qid)
        del self.state.active_side_quests[qid]
