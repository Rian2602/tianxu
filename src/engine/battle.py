"""Battle engine (giliran menu) — ENGINE_ARCHITECTURE §8.

Mekanik disahkan:
- Urutan tetap: pemain → musuh.
- Damage = attack × (100 / (100 + defense)), min 1, variasi ±10–20%.
- Elemen 五行: 克制 1.5× / 被克 0.67×.
- Kritikal: peluang `crit_chance`, damage ×`crit_multiplier`.
- Regen Qi 5% Qi maks di awal giliran masing-masing.
- KO → respawn titik aman + penalti exp ringan (10% progres tingkat).
"""

from __future__ import annotations

import random

from ..loader import DataRegistry
from .cultivation import gain_exp
from .events import add_log
from .state import GameState


def companion_stats(state: GameState, registry: DataRegistry) -> dict | None:
    """Stat kompanion aktif — base + level × scale (ENGINE_ARCHITECTURE §9.4).

    level = level ranah pemain; HP disimpan di state (persisten antar battle).
    """
    c = state.companion
    if not c or not c.get("active"):
        return None
    comp = next((x for x in registry.companions if x["id"] == c["id"]), None)
    if not comp:
        return None
    scale = registry.config.get("companion", {})
    lvl = state.player.realm_level
    hp_max = int(comp["base_hp"]) + lvl * int(scale.get("hp_per_level", 12))
    return {
        "id": c["id"],
        "name": comp["name"],
        "element": comp.get("element"),
        "hp": min(c.get("hp") or hp_max, hp_max),
        "hp_max": hp_max,
        "attack": int(comp["base_attack"]) + lvl * int(scale.get("attack_per_level", 2)),
        "defense": int(comp["base_defense"]) + lvl * int(scale.get("defense_per_level", 1)),
        "speed": int(comp["base_speed"]) + round(lvl * float(scale.get("speed_per_level", 0.5))),
    }


def player_combat(state: GameState, registry: DataRegistry) -> dict:
    lvl = state.player.realm_level
    weapon = state.player.equipment.get("weapon")
    wpower = int(registry.item(weapon)["power"]) if weapon and registry.item(weapon) else 0
    return {
        "hp": state.player.hp,
        "hp_max": state.max_hp(registry),
        "qi": state.player.qi,
        "qi_max": state.max_qi(registry),
        "attack": 6 + lvl + wpower,
        "defense": 3 + lvl // 2,
        "speed": 8 + lvl,
        "element": None,
    }


class BattleEngine:
    def __init__(self, registry: DataRegistry, state: GameState, quest_engine) -> None:
        self.reg = registry
        self.state = state
        self.quest_engine = quest_engine

    # ---------- mulai ----------

    def start(self, foes: list[dict], context: str = "hunt") -> dict:
        """foes = daftar stat musuh (baris enemies.csv atau npc['combat'])."""
        b = {
            "foes": [dict(f) for f in foes],
            "context": context,
            "spar_npc": None,
            "player_guard": False,
            "over": False,
            "won": False,
            "player_fled": False,
        }
        self.state.pending_battle = b
        for f in b["foes"]:
            # normalisasi angka (CSV dibaca sebagai string)
            f["hp"] = int(f["hp"])
            f["qi"] = int(f.get("qi", 0) or 0)
            f["attack"] = int(f.get("attack", 1))
            f["defense"] = int(f.get("defense", 0))
            f["speed"] = int(f.get("speed", 5))
            f["hp_max"] = f["hp"]
            f["qi_max"] = f["qi"]
        add_log(self.state, "battle", f"⚔️  Pertarungan dimulai melawan {self._foe_names(b)}!")
        return self.view()

    def _foe_names(self, b: dict) -> str:
        return " & ".join(f["name"] for f in b["foes"])

    # ---------- aksi pemain ----------

    def player_action(self, action: dict) -> dict:
        b = self.state.pending_battle
        if not b or b["over"]:
            return self.view()
        pc = player_combat(self.state, self.reg)
        a = action.get("action")
        if a == "attack":
            self._attack(pc, b, b["foes"][0])
        elif a == "technique":
            self._technique(pc, b, action.get("technique"))
        elif a == "item":
            self._use_item(pc, b, action.get("item"))
        elif a == "guard":
            b["player_guard"] = True
            add_log(self.state, "battle", "Kau bertahan — damage masuk dikurangi setengah.")
        elif a == "flee":
            if self._try_flee(pc, b):
                b["over"] = True
                b["player_fled"] = True
                self.state.pending_battle = None
                add_log(self.state, "battle", "Kau berhasil kabur dari pertarungan.")
                return self.view()
            add_log(self.state, "battle", "Kau gagal kabur!")
        self._companion_turn(b)
        self._regen(pc, b)
        if not b["over"] and self._all_dead(b):
            return self._victory(b, pc)
        if not b["over"]:
            self._enemy_turn(pc, b)
        self._regen_foes(b)
        if not b["over"] and self._all_dead(b):
            return self._victory(b, pc)
        if not b["over"] and pc["hp"] <= 0:
            return self._ko(b)
        self._sync_player(pc)
        return self.view()

    # ---------- serangan ----------

    def _attack(self, pc: dict, b: dict, foe: dict) -> None:
        dmg, crit = self._calc_damage(pc["attack"], foe["defense"], None, foe.get("element"))
        foe["hp"] -= dmg
        add_log(self.state, "battle", f"Serangan! {foe['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")

    def _technique(self, pc: dict, b: dict, tid: str | None) -> None:
        tek = self.reg.technique(tid or "")
        if not tek:
            add_log(self.state, "battle", "Teknik tidak dikenal.")
            return
        # validasi kepemilikan akademi (skill_pool) — ENGINE_ARCHITECTURE §5.6/§8
        allowed = [t["id"] for t in self.reg.player_techniques(self.state.player.academy or "")]
        if tid not in allowed:
            add_log(self.state, "battle", "Kau belum menguasai teknik itu.")
            return
        cost = int(tek["qi_cost"])
        if pc["qi"] < cost:
            add_log(self.state, "battle", "Qi tidak cukup untuk teknik itu!")
            return
        pc["qi"] -= cost
        kind = tek["kind"]
        power = int(tek["power"])
        if kind == "attack":
            dmg, crit = self._calc_damage(pc["attack"] + power, b["foes"][0]["defense"], tek.get("element"), b["foes"][0].get("element"))
            b["foes"][0]["hp"] -= dmg
            add_log(self.state, "battle", f"{tek['name']}! {b['foes'][0]['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
        elif kind == "defend":
            b["player_guard"] = True
            add_log(self.state, "battle", f"{tek['name']} — damage masuk dikurangi {power}%.")
        elif kind == "heal":
            heal = min(power, pc["hp_max"] - pc["hp"])
            pc["hp"] += heal
            add_log(self.state, "battle", f"{tek['name']} memulihkan {heal} HP.")

    def _use_item(self, pc: dict, b: dict, iid: str | None) -> None:
        if not iid or self.state.inventory.get(iid, 0) < 1:
            add_log(self.state, "battle", "Item tidak tersedia.")
            return
        it = self.reg.item(iid)
        if not it or it.get("type") != "consumable":
            add_log(self.state, "battle", "Item itu tidak bisa dipakai di battle.")
            return
        self.state.inventory[iid] -= 1
        if self.state.inventory[iid] <= 0:
            del self.state.inventory[iid]
        hp = int(it.get("hp_restore", 0))
        qi = int(it.get("qi_restore", 0))
        pc["hp"] = min(pc["hp_max"], pc["hp"] + hp)
        pc["qi"] = min(pc["qi_max"], pc["qi"] + qi)
        add_log(self.state, "battle", f"Memakai {it['name']} (+{hp} HP, +{qi} Qi).")

    def _try_flee(self, pc: dict, b: dict) -> bool:
        foe = b["foes"][0]
        chance = 0.5 + (pc["speed"] - foe["speed"]) * 0.02
        chance = max(0.2, min(0.9, chance))
        return random.random() < chance

    # ---------- giliran musuh ----------

    def _enemy_turn(self, pc: dict, b: dict) -> None:
        comp = companion_stats(self.state, self.reg)
        for foe in b["foes"]:
            if foe["hp"] <= 0:
                continue
            # musuh 50% menarget kompanion bila aktif (punya HP sendiri)
            if comp and comp["hp"] > 0 and random.random() < 0.5:
                dmg, crit = self._calc_damage(foe["attack"], comp["defense"], foe.get("element"), comp.get("element"))
                comp["hp"] -= dmg
                if comp["hp"] <= 0:
                    comp["hp"] = 0
                    self.state.companion["active"] = False
                    add_log(self.state, "battle", f"{comp['name']} KO — tidak akan bertarung sampai kau istirahat di titik aman!")
                else:
                    add_log(self.state, "battle", f"{foe['name']} menyerang {comp['name']}! {comp['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
                self.state.companion["hp"] = comp["hp"]
            else:
                dmg, crit = self._calc_damage(foe["attack"], pc["defense"], foe.get("element"), None)
                if b["player_guard"]:
                    dmg = max(1, dmg // 2)
                pc["hp"] -= dmg
                add_log(self.state, "battle", f"{foe['name']} menyerang! Kau kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
        b["player_guard"] = False

    def _companion_turn(self, b: dict) -> None:
        """Kompanion aktif bertindak otomatis tiap giliran pemain (§9.4)."""
        comp = companion_stats(self.state, self.reg)
        if not comp or comp["hp"] <= 0:
            return
        foe = next((f for f in b["foes"] if f["hp"] > 0), None)
        if not foe:
            return
        dmg, crit = self._calc_damage(comp["attack"], foe["defense"], comp.get("element"), foe.get("element"))
        foe["hp"] -= dmg
        add_log(self.state, "battle", f"{comp['name']} menerjang! {foe['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")

    def _regen(self, pc: dict, b: dict) -> None:
        pct = self.reg.config.get("battle", {}).get("qi_regen_percent_per_turn", 5)
        pc["qi"] = min(pc["qi_max"], pc["qi"] + round(pc["qi_max"] * pct / 100))

    def _regen_foes(self, b: dict) -> None:
        pct = self.reg.config.get("battle", {}).get("qi_regen_percent_per_turn", 5)
        for f in b["foes"]:
            f["qi"] = min(f["qi_max"], f.get("qi", 0) + round(f["qi_max"] * pct / 100))

    # ---------- perhitungan damage ----------

    def _calc_damage(self, attack: int, defense: int, elem_att, elem_def) -> tuple[int, bool]:
        cfg = self.reg.config.get("battle", {})
        mult = 1.0
        if elem_att and elem_def:
            adv = self.reg.element_advantage
            if adv.get(elem_att) == elem_def:
                mult = 1.5
            elif adv.get(elem_def) == elem_att:
                mult = 0.67
        base = attack * (100 / (100 + defense)) * mult
        base *= random.uniform(0.8, 1.2)
        crit = random.random() < cfg.get("crit_chance", 0.08)
        if crit:
            base *= cfg.get("crit_multiplier", 1.5)
        return max(1, round(base)), crit

    # ---------- akhir battle ----------

    def _all_dead(self, b: dict) -> bool:
        return all(f["hp"] <= 0 for f in b["foes"])

    def _victory(self, b: dict, pc: dict) -> dict:
        b["over"] = True
        b["won"] = True
        self.state.pending_battle = None
        killed = [f["id"] for f in b["foes"] if f.get("id")]
        # exp
        if b["context"] == "spar":
            gain_exp(self.state, self.reg, self.reg.config["cultivation"]["spar_win_exp"])
            if b.get("spar_npc"):
                self.quest_engine.notify_spar_won(b["spar_npc"])
        else:
            total = sum(int(f.get("exp_reward", 0)) for f in b["foes"])
            gain_exp(self.state, self.reg, total)
        # drop
        for f in b["foes"]:
            di = f.get("drop_item")
            dc = float(f.get("drop_chance", 0) or 0)
            if di and random.random() < dc:
                self.state.inventory[di] = self.state.inventory.get(di, 0) + 1
                it = self.reg.item(di)
                add_log(self.state, "battle", f"Menemukan: {it['name'] if it else di}.")
        add_log(self.state, "battle", f"🏆 Kemenangan! (+{self._last_exp(b)} exp)")
        self.quest_engine.notify_battle_won(killed)
        # sinkronkan HP/Qi yang benar-benar bertarung (bukan stat segar)
        self._sync_player(pc)
        return self.view()

    def _last_exp(self, b: dict) -> int:
        if b["context"] == "spar":
            return self.reg.config["cultivation"]["spar_win_exp"]
        return sum(int(f.get("exp_reward", 0)) for f in b["foes"])

    def _ko(self, b: dict) -> dict:
        b["over"] = True
        b["won"] = False
        self.state.pending_battle = None
        # penalti exp ringan
        ratio = self.reg.config.get("ko_penalty", {}).get("exp_loss_ratio", 0.1)
        loss = round(self.state.exp_next(self.reg) * ratio)
        self.state.player.exp = max(0, self.state.player.exp - loss)
        if b["context"] == "spar":
            gain_exp(self.state, self.reg, self.reg.config["cultivation"]["spar_loss_exp"])
        # respawn titik aman
        safe = self.state.last_safe_location or "loc_asrama"
        self.state.location = safe
        self.state.player.hp = self.state.max_hp(self.reg)
        self.state.player.qi = self.state.max_qi(self.reg)
        add_log(self.state, "battle", f"💀 Kau KO! Respawn di {self.reg.location(safe)['name']} (−{loss} exp).")
        return self.view()

    def _sync_player(self, pc: dict) -> None:
        self.state.player.hp = pc["hp"]
        self.state.player.qi = pc["qi"]

    # ---------- tampilan ----------

    def view(self) -> dict:
        b = self.state.pending_battle
        if not b:
            return {"mode": "explore"}
        pc = player_combat(self.state, self.reg)
        return {
            "mode": "battle",
            "player": {"hp": pc["hp"], "hp_max": pc["hp_max"], "qi": pc["qi"], "qi_max": pc["qi_max"]},
            "foes": [
                {"name": f["name"], "hp": f["hp"], "hp_max": f["hp_max"], "element": f.get("element")}
                for f in b["foes"]
            ],
            "companion": companion_stats(self.state, self.reg),
            "over": b["over"],
            "won": b["won"],
            "fled": b.get("player_fled", False),
        }
