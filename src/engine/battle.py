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

# Jenis teknik yang didukung engine — satu sumber kebenaran untuk validator.
TECHNIQUE_KINDS = frozenset({"attack", "defend", "heal"})

# Jenis status effect yang didukung engine — satu sumber kebenaran untuk validator.
# dot = damage per turn, stun = skip turn, debuff = kurangi stat,
# hot = heal per turn, buff = tambah stat/damage reduction.
STATUS_KINDS = frozenset({"dot", "stun", "debuff", "hot", "buff"})

# Batas atas damage reduction (guard_pct + guard buff + passive) — mencegah invulnerability.
MAX_DAMAGE_REDUCTION = 75

# Himpunan elemen yang didukung engine — satu sumber kebenaran untuk validator.
SUPPORTED_ELEMENTS = frozenset({"logam", "kayu", "tanah", "air", "api", "angin", "petir", "kosong"})

# Elemen netral — tidak counter apapun, tidak dicounter.
NEUTRAL_ELEMENTS = frozenset({"angin", "petir", "kosong"})




def companion_stats(state: GameState, registry: DataRegistry) -> dict | None:
    """Stat kompanion aktif — base + level × scale (ENGINE_ARCHITECTURE §9.4).

    level = level ranah pemain; HP disimpan di state (persisten antar battle).
    """
    # Use active_companion ID to find in companions list
    cid = state.active_companion
    c = next((x for x in state.companions if x.get("id") == cid), None)
    if not c or not c.get("active"):
        return None
    comp = next((x for x in registry.companions if x.get("id") == c["id"]), None)
    if not comp:
        return None
    scale = registry.config.get("companion", {})
    lvl = state.player.realm_level
    # F3 (adaptifitas): kolom opsional → default, jangan KeyError di tengah battle
    hp_max = int(comp.get("base_hp", 10)) + lvl * int(scale.get("hp_per_level", 12))
    return {
        "id": c["id"],
        "name": comp["name"],
        "element": comp.get("element"),
        # Bug #2 (audit Claude): 0 adalah nilai HP sah (KO) — jangan jatuh ke
        # hp_max karena 0 falsy di Python. Cek eksplisit None.
        "hp": min(hp_max if c.get("hp") is None else int(c.get("hp")), hp_max),
        "hp_max": hp_max,
        "attack": int(comp.get("base_attack", 3)) + lvl * int(scale.get("attack_per_level", 2)),
        "defense": int(comp.get("base_defense", 1)) + lvl * int(scale.get("defense_per_level", 1)),
        "speed": int(comp.get("base_speed", 5)) + round(lvl * float(scale.get("speed_per_level", 0.5))),
    }


def companion_stats_for(state: GameState, registry: DataRegistry, companion_id: str) -> dict | None:
    """Stat kompanion berdasarkan ID — untuk team spar (bukan harus active)."""
    c = next((x for x in state.companions if x.get("id") == companion_id), None)
    if not c:
        return None
    comp = next((x for x in registry.companions if x.get("id") == c["id"]), None)
    if not comp:
        return None
    scale = registry.config.get("companion", {})
    lvl = state.player.realm_level
    hp_max = int(comp.get("base_hp", 10)) + lvl * int(scale.get("hp_per_level", 12))
    return {
        "id": c["id"],
        "name": comp["name"],
        "element": comp.get("element"),
        "hp": min(hp_max if c.get("hp") is None else int(c.get("hp")), hp_max),
        "hp_max": hp_max,
        "attack": int(comp.get("base_attack", 3)) + lvl * int(scale.get("attack_per_level", 2)),
        "defense": int(comp.get("base_defense", 1)) + lvl * int(scale.get("defense_per_level", 1)),
        "speed": int(comp.get("base_speed", 5)) + round(lvl * float(scale.get("speed_per_level", 0.5))),
    }


def player_combat(state: GameState, registry: DataRegistry) -> dict:
    lvl = state.player.realm_level
    weapon = state.player.equipment.get("weapon")
    wpower = int(registry.item(weapon)["power"]) if weapon and registry.item(weapon) else 0
    atk = 6 + lvl + wpower
    dfn = 3 + lvl // 2
    for eff in state.status_effects:
        if "atk_mult" in eff:
            atk = int(atk * eff["atk_mult"])
    return {
        "hp": state.player.hp,
        "hp_max": state.max_hp(registry),
        "qi": state.player.qi,
        "qi_max": state.max_qi(registry),
        "attack": max(1, atk),
        "defense": max(0, dfn),
        "speed": 8 + lvl,
        "element": None,
    }


REALM_BONUS = {
    "realm_xuanshi": "tahan_racun",
    "realm_dishi": "perisai_jiwa",
    "realm_tianshi": "kuasa_domain",
    "realm_shenwu": "kekal_awet_muda",
}


def has_realm_bonus(state: GameState, bonus: str) -> bool:
    """Cek apakah pemain memiliki bonus ranah tertentu."""
    for rid in state.realms_unlocked:
        if REALM_BONUS.get(rid) == bonus:
            return True
    return False


DEFAULT_ELEMENT_ADVANTAGE = {
    "logam": "kayu",
    "kayu": "tanah",
    "tanah": "air",
    "air": "api",
    "api": "logam",
}
# Neutral elements: not in advantage map → mult stays 1.0 (handled by _calc_damage)



def _calc_damage(
    attack: int,
    defense: int,
    elem_att: str | None = None,
    elem_def: str | None = None,
    registry: DataRegistry | None = None,
    config: dict | None = None,
) -> tuple[int, bool]:
    cfg = config if config is not None else (registry.config.get("battle", {}) if registry else {})
    mult = 1.0
    if elem_att and elem_def:
        adv = registry.element_advantage if registry else DEFAULT_ELEMENT_ADVANTAGE
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


class BattleEngine:
    """Mesin battle giliran — mengelola serangan, status, dan resolusi."""

    def __init__(self, registry: DataRegistry, state: GameState, quest_engine) -> None:
        self.reg = registry
        self.state = state
        self.quest_engine = quest_engine

    # ---------- mulai ----------

    def start(self, foes: list[dict], context: str = "hunt", allies: list[dict] | None = None,
              use_companion: bool = True) -> dict:
        """foes = daftar stat musuh (baris enemies.csv atau npc['combat']).
        allies = stat sekutu quest untuk spar_team — menyerang otomatis."""
        b = {
            "foes": [dict(f) for f in foes],
            "context": context,
            "spar_npc": None,
            "player_guard": False,
            "over": False,
            "won": False,
            "player_fled": False,
            "allies": allies or [],
            "ally_turn_index": 0,
            "use_companion": use_companion,
        }
        self.state.pending_battle = b
        for f in b["foes"]:
            # normalisasi angka (CSV dibaca sebagai string) — F3: kolom opsional
            # diberi default, bukan KeyError di tengah battle
            f["hp"] = int(f["hp"]) if f.get("hp") is not None else 10
            f["qi"] = int(f["qi"]) if f.get("qi") is not None else 0
            f["attack"] = int(f.get("attack", 1))
            f["defense"] = int(f.get("defense", 0))
            f["speed"] = int(f.get("speed", 5))
            f["hp_max"] = int(f.get("hp_max") or f["hp"])
            f["qi_max"] = int(f.get("qi_max") or f["qi"])
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
        # status effect (Task 1): proses dot & cek stun di awal giliran pemain;
        # status yang ADA sebelum giliran ini yang di-tick (yang baru kena giliran ini
        # menunggu giliran berikutnya — durasi = jumlah giliran pemain yang terpengaruh)
        pre_round = set(b.get("player_statuses", {}))
        stunned = self._apply_player_statuses(pc, b)
        if pc["hp"] <= 0:
            return self._ko(b)
        # A2 (keputusan §17): turn_order "speed" — yang lebih cepat bertindak dulu tiap ronde
        speed_order = self.reg.config.get("battle", {}).get("turn_order") == "speed"
        foe_speed = max((f.get("speed", 0) for f in b["foes"] if f["hp"] > 0), default=0)
        foe_first = speed_order and foe_speed > pc["speed"]
        if foe_first:
            for foe in b["foes"]:
                if foe["hp"] > 0:
                    self._apply_foe_statuses(foe, b)
            self._enemy_turn(pc, b)
            if pc["hp"] <= 0:
                self._regen_foes(b)
                return self._ko(b)
        if not stunned:
            a = action.get("action")
            if a == "attack":
                self._attack(pc, b, b["foes"][0])
            elif a == "technique":
                self._technique(pc, b, action.get("technique"))
            elif a == "item":
                self._use_item(pc, b, action.get("item"))
            elif a == "guard":
                b["player_guard"] = 50
                add_log(self.state, "battle", "Kau bertahan — damage masuk dikurangi setengah.")
            elif a == "flee":
                if self._try_flee(pc, b):
                    b["over"] = True
                    b["player_fled"] = True
                    self.state.pending_battle = None
                    add_log(self.state, "battle", "Kau berhasil kabur dari pertarungan.")
                    return self.view()
                add_log(self.state, "battle", "Kau gagal kabur!")
        else:
            add_log(self.state, "battle", "Kau terpana — tidak bisa bergerak giliran ini!")
        self._companion_turn(b)
        self._ally_turns(b)
        self._regen(pc, b)
        if not b["over"] and self._all_dead(b):
            return self._victory(b, pc)
        if not b["over"] and not foe_first:
            for foe in b["foes"]:
                if foe["hp"] > 0:
                    self._apply_foe_statuses(foe, b)
            self._enemy_turn(pc, b)
        self._regen_foes(b)
        if not b["over"] and pc["hp"] <= 0:
            return self._ko(b)
        self._tick_player_statuses(b, pre_round)
        self._sync_player(pc)
        return self.view()

    # ---------- serangan ----------

    def _attack(self, pc: dict, b: dict, foe: dict) -> None:
        atk = pc["attack"]
        if has_realm_bonus(self.state, "kuasa_domain"):
            atk = int(atk * 1.15)
        dmg, crit = self._calc_damage(atk, foe["defense"], None, foe.get("element"))
        foe["hp"] -= dmg
        add_log(self.state, "battle", f"Serangan! {foe['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")

    def _technique(self, pc: dict, b: dict, tid: str | None) -> None:
        tek = self.reg.technique(tid or "")
        if not tek:
            add_log(self.state, "battle", "Teknik tidak dikenal.")
            return
        # H4: ranah teknik tidak boleh melebihi ranah pemain (bandingkan order realm)
        req_id = tek.get("realm_required")
        if req_id:
            req_r = self.reg.realms.get(req_id)
            cur_r = self.reg.realms.get(self.state.player.realm)
            if req_r and cur_r and int(req_r["order"]) > int(cur_r["order"]):
                add_log(self.state, "battle", "Ranahmu belum cukup untuk teknik itu.")
                return
        # validasi kepemilikan (skill_pool + unlock_arc + teknik reward C1) — ENGINE §5.6/§8
        allowed = [t["id"] for t in self.reg.player_techniques(
            self.state.player.academy or "", self.state.player.realm,
            frozenset(self.state.completed_quests),
            owned=tuple(self.state.player.techniques))]
        if tid not in allowed:
            add_log(self.state, "battle", "Kau belum menguasai teknik itu.")
            return
        kind = tek.get("kind")
        # Fix audit v3 §1.4: kind tak dikenal TIDAK boleh menghanguskan Qi —
        # dilaporkan lalu diabaikan (defense-in-depth setelah validator).
        if kind not in TECHNIQUE_KINDS:
            add_log(self.state, "battle",
                    f"Teknik '{tek['name']}' (kind '{kind}') tak dikenal — tidak terjadi apa-apa.")
            return
        cost = int(tek["qi_cost"])
        if pc["qi"] < cost:
            add_log(self.state, "battle", "Qi tidak cukup untuk teknik itu!")
            return
        pc["qi"] -= cost
        # C1: power naik sesuai level teknik (power × (1 + (level−1) × growth))
        lvl = int(self.state.player.technique_levels.get(tid, 1))
        growth = float(self.reg.config.get("cultivation", {}).get("technique_power_growth_per_level", 0.0))
        power = int(int(tek["power"]) * (1 + (lvl - 1) * growth))
        if kind == "attack":
            # Apply weaken debuff to attack
            atk = pc["attack"] + power
            pst = b.get("player_statuses", {})
            cfg = self._status_config()
            if "weaken" in pst:
                weaken_cfg = cfg.get("weaken", {})
                atk = max(1, int(atk * float(weaken_cfg.get("atk_mult", 1.0))))
            # Apply focus buff to power
            if "focus" in pst:
                focus_cfg = cfg.get("focus", {})
                atk = int(atk * float(focus_cfg.get("power_mult", 1.0)))
                del pst["focus"]  # consumed
                add_log(self.state, "battle", "Fokus terpakai!")
            # Apply expose debuff to foe defense
            foe_def = b["foes"][0]["defense"]
            if "expose" in b.get("foe_statuses", {}):
                expose_cfg = cfg.get("expose", {})
                foe_def = max(0, int(foe_def * float(expose_cfg.get("def_mult", 1.0))))
            dmg, crit = self._calc_damage(atk, foe_def, tek.get("element"), b["foes"][0].get("element"))
            b["foes"][0]["hp"] -= dmg
            add_log(self.state, "battle", f"{tek['name']}! {b["foes"][0]["name"]} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
            # Secondary effect: apply status dari data teknik
            self._apply_technique_status(b, b["foes"][0], tek)
        elif kind == "defend":
            # guard_pct dibaca langsung dari data — TIDAK scale dengan level.
            # Alasan: guard_pct=55 × 1.15^4 = 88% → near invulnerability.
            pct = int(tek.get("guard_pct", 0)) or power
            pct = min(pct, 80)  # cap individual guard_pct
            b["player_guard"] = pct
            add_log(self.state, "battle", f"{tek['name']} — damage masuk dikurangi {pct}%.")
        elif kind == "heal":
            heal = min(power, pc["hp_max"] - pc["hp"])
            pc["hp"] += heal
            add_log(self.state, "battle", f"{tek['name']} memulihkan {heal} HP.")
            # Secondary effect: apply status dari data teknik (regen, dst)
            self._apply_technique_status(b, pc, tek, target_is_player=True)

    def _apply_technique_status(self, b: dict, target: dict, tek: dict,
                                 target_is_player: bool = False) -> None:
        """Apply secondary effect dari teknik (apply_status field di CSV).
        Stacking rules: tidak stack magnitude; reapply → refresh duration."""
        sid = tek.get("apply_status", "")
        if not sid:
            return
        chance = float(tek.get("status_chance", 0) or 0)
        if chance > 0 and random.random() * 100 >= chance:
            return
        sc = self._status_config().get(sid)
        if not sc:
            return
        duration = int(tek.get("status_duration", 0) or sc.get("max_duration", 1))
        max_dur = int(sc.get("max_duration", duration))
        duration = min(duration, max_dur)
        # Stacking: refresh duration (tidak stack magnitude)
        if target_is_player:
            st = b.setdefault("player_statuses", {})
        else:
            st = b.setdefault("foe_statuses", {})
        if sid in st:
            st[sid] = max(st[sid], duration)  # refresh ke max
        else:
            st[sid] = duration
        add_log(self.state, "battle", f"{target.get('name', 'Target')} terkena {sc.get('name', sid)}!")

    def _apply_foe_statuses(self, foe: dict, b: dict) -> None:
        """Proses status aktif di awal giliran musuh. Tick durasi + apply effects."""
        st = b.get("foe_statuses", {})
        if not st:
            return
        cfg = self._status_config()
        for sid in list(st.keys()):
            sc = cfg.get(sid)
            if not sc:
                continue
            kind = sc.get("kind")
            if kind not in STATUS_KINDS:
                del st[sid]
                continue
            if kind == "dot":
                dmg = int(sc.get("power", 0))
                foe["hp"] -= dmg
                add_log(self.state, "battle", f"{foe['name']} Terbakar! Kehilangan {dmg} HP.")
            elif kind == "hot":
                heal_pct = float(sc.get("heal_pct", 0))
                heal = max(1, int(foe.get("hp_max", foe["hp"]) * heal_pct / 100))
                foe["hp"] = min(foe.get("hp_max", foe["hp"]), foe["hp"] + heal)
                add_log(self.state, "battle", f"{foe['name']} Regenerasi! Memulihkan {heal} HP.")
            # Tick durasi
            st[sid] -= 1
            if st[sid] <= 0:
                del st[sid]

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

    # ---------- status effect (Task 1, data-driven) ----------

    def _status_config(self) -> dict:
        return self.reg.config.get("battle", {}).get("statuses", {}) or {}

    def _apply_player_statuses(self, pc: dict, b: dict) -> bool:
        """Proses status aktif di awal giliran pemain. Return True bila terpana (stun).

        Stacking rules (Fase 1):
        - DoT (dot): tidak stack damage; reapply → duration diperpanjang; max = max_duration
        - Debuff: tidak stack magnitude; reapply → refresh duration ke max
        - Stun: tidak stack; refresh duration
        - Buff: tidak stack magnitude; reapply → refresh duration
        - Duration tick: kurangi 1 setiap turn, hapus saat <= 0
        """
        st = b.get("player_statuses", {})
        if not st:
            return False
        cfg = self._status_config()
        stunned = False
        for sid in list(st.keys()):
            sc = cfg.get(sid)
            if not sc:
                continue
            kind = sc.get("kind")
            # Fix audit v3 §1.5: status kind tak dikenal dilaporkan + diabaikan.
            if kind not in STATUS_KINDS:
                add_log(self.state, "battle",
                        f"Efek '{sc.get('name', sid)}' (kind '{kind}') tak dikenal — diabaikan.")
                del st[sid]
                continue
            if kind == "dot":
                dmg = int(sc.get("power", 0))
                pc["hp"] -= dmg
                add_log(self.state, "battle", f"{sc.get('name', sid)}! Kehilangan {dmg} HP.")
            elif kind == "stun":
                stunned = True
            elif kind == "hot":
                heal_pct = float(sc.get("heal_pct", 0))
                heal = max(1, int(pc["hp_max"] * heal_pct / 100))
                pc["hp"] = min(pc["hp_max"], pc["hp"] + heal)
                add_log(self.state, "battle", f"{sc.get('name', sid)}! Memulihkan {heal} HP.")
            # debuff/buff: efek diterapkan saat damage calculation, bukan di sini
        return stunned

    def _tick_player_statuses(self, b: dict, pre_round: set) -> None:
        """Kurangi durasi status yang sudah aktif SEBELUM giliran ini; hapus yang habis.
        Hanya tick status yang sudah ada sebelum giliran ini (pre_round).
        Status baru (dari serangan musuh di giliran ini) menunggu giliran berikutnya."""
        st = b.get("player_statuses")
        if not st:
            return
        for sid in [k for k in st if k in pre_round]:
            st[sid] -= 1
            if st[sid] <= 0:
                del st[sid]
                sc = self._status_config().get(sid)
                add_log(self.state, "battle", f"Efek {sc.get('name', sid) if sc else sid} hilang.")

    def _maybe_apply_status(self, b: dict, foe: dict) -> None:
        """Serangan musuh yang kena ke pemain berpeluang menerapkan status (data-driven).
        Stacking rules: tidak stack magnitude; reapply → refresh duration."""
        sid = foe.get("status")
        chance = float(foe.get("status_chance", 0) or 0)
        if not sid or random.random() >= chance:
            return
        sc = self._status_config().get(sid)
        if not sc:
            return
        duration = int(sc.get("duration", 1))
        max_dur = int(sc.get("max_duration", duration))
        duration = min(duration, max_dur)
        st = b.setdefault("player_statuses", {})
        # Stacking: refresh duration (tidak stack magnitude)
        if sid in st:
            st[sid] = max(st[sid], duration)
        else:
            st[sid] = duration
        add_log(self.state, "battle", f"Kau terkena {sc.get('name', sid)}!")

    # ---------- giliran musuh ----------

    def _enemy_turn(self, pc: dict, b: dict) -> None:
        comp = companion_stats(self.state, self.reg) if b.get("use_companion", True) else None
        # Kumpulan target: pemain selalu ada; kompanion/sekutu hanya bila hidup.
        targets = ["player"]
        if comp and comp["hp"] > 0:
            targets.append(("companion", comp))
        for i, ally in enumerate(b.get("allies", [])):
            if ally["hp"] > 0:
                targets.append(("ally", i))
        for foe in b["foes"]:
            if foe["hp"] <= 0:
                continue
            target = random.choice(targets)
            if target == "player":
                # Hitung defense dengan debuff (expose)
                pc_def = pc["defense"]
                pst = b.get("player_statuses", {})
                cfg = self._status_config()
                if "expose" in pst:
                    expose_cfg = cfg.get("expose", {})
                    pc_def = max(0, int(pc_def * float(expose_cfg.get("def_mult", 1.0))))
                dmg, crit = self._calc_damage(foe["attack"], pc_def, foe.get("element"), None)
                # Mitigation: multiplicative stacking (guard_pct + guard buff + passive)
                reductions = []
                if b["player_guard"]:
                    reductions.append(b["player_guard"] / 100)
                if "guard" in pst:
                    guard_cfg = cfg.get("guard", {})
                    reductions.append(float(guard_cfg.get("dmg_reduction", 0)) / 100)
                if reductions:
                    total_reduction = 1.0
                    for r in reductions:
                        total_reduction *= (1 - r)
                    total_reduction = max(1 - MAX_DAMAGE_REDUCTION / 100, total_reduction)
                    dmg = max(1, int(dmg * total_reduction))
                pc["hp"] -= dmg
                add_log(self.state, "battle", f"{foe['name']} menyerang! Kau kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
                self._maybe_apply_status(b, foe)
            elif target[0] == "companion":
                c = target[1]
                dmg, crit = self._calc_damage(foe["attack"], c["defense"], foe.get("element"), c.get("element"))
                c["hp"] -= dmg
                if c["hp"] <= 0:
                    c["hp"] = 0
                    for sc in self.state.companions:
                        if sc.get("id") == c["id"]:
                            sc["active"] = False
                            break
                    add_log(self.state, "battle", f"{c['name']} KO — tidak akan bertarung sampai kau istirahat di titik aman!")
                else:
                    add_log(self.state, "battle", f"{foe['name']} menyerang {c['name']}! {c['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
                for sc in self.state.companions:
                    if sc.get("id") == c["id"]:
                        sc["hp"] = c["hp"]
                        break
            elif target[0] == "ally":
                ally = b["allies"][target[1]]
                dmg, crit = self._calc_damage(foe["attack"], ally["defense"], foe.get("element"), ally.get("element"))
                ally["hp"] -= dmg
                if ally["hp"] <= 0:
                    ally["hp"] = 0
                    add_log(self.state, "battle", f"{ally['name']} KO — gugur dalam ujian!")
                else:
                    add_log(self.state, "battle", f"{foe['name']} menyerang {ally['name']}! {ally['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
                # Sinkronkan bila ally ini ternyata berasal dari state kompanion lama.
                for sc in self.state.companions:
                    if sc.get("id") == ally["id"]:
                        sc["hp"] = ally["hp"]
                        break
        b["player_guard"] = False

    def _companion_turn(self, b: dict) -> None:
        """Kompanion aktif bertindak otomatis tiap giliran pemain (§9.4)."""
        if not b.get("use_companion", True):
            return
        comp = companion_stats(self.state, self.reg)
        if not comp or comp["hp"] <= 0:
            return
        foe = next((f for f in b["foes"] if f["hp"] > 0), None)
        if not foe:
            return
        dmg, crit = self._calc_damage(comp["attack"], foe["defense"], comp.get("element"), foe.get("element"))
        foe["hp"] -= dmg
        add_log(self.state, "battle", f"{comp['name']} menerjang! {foe['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")

    def _ally_turns(self, b: dict) -> None:
        """Sekutu quest (spar_team) — satu sekutu menyerang per giliran, bergantian."""
        allies = b.get("allies", [])
        if not allies:
            return
        idx = b.get("ally_turn_index", 0)
        for _ in range(len(allies)):
            ally = allies[idx % len(allies)]
            if ally["hp"] > 0:
                foe = next((f for f in b["foes"] if f["hp"] > 0), None)
                if not foe:
                    break
                dmg, crit = self._calc_damage(ally["attack"], foe["defense"], ally.get("element"), foe.get("element"))
                foe["hp"] -= dmg
                add_log(self.state, "battle", f"{ally['name']} menyerang! {foe['name']} kehilangan {dmg} HP{' (KRITIS!)' if crit else ''}.")
                b["ally_turn_index"] = (idx + 1) % len(allies)
                break
            idx += 1

    def _regen(self, pc: dict, b: dict) -> None:
        pct = self.reg.config.get("battle", {}).get("qi_regen_percent_per_turn", 5)
        pc["qi"] = min(pc["qi_max"], pc["qi"] + round(pc["qi_max"] * pct / 100))
        # Kekal Awet Muda: +5% HP regen per turn
        if has_realm_bonus(self.state, "kekal_awet_muda"):
            hp_regen = max(1, round(pc["hp_max"] * 0.05))
            pc["hp"] = min(pc["hp_max"], pc["hp"] + hp_regen)

    def _regen_foes(self, b: dict) -> None:
        pct = self.reg.config.get("battle", {}).get("qi_regen_percent_per_turn", 5)
        for f in b["foes"]:
            f["qi"] = min(f["qi_max"], f.get("qi", 0) + round(f["qi_max"] * pct / 100))

    # ---------- perhitungan damage ----------

    def _calc_damage(self, attack: int, defense: int, elem_att, elem_def) -> tuple[int, bool]:
        return _calc_damage(attack, defense, elem_att, elem_def, registry=self.reg)



    # ---------- akhir battle ----------

    def _all_dead(self, b: dict) -> bool:
        return all(f["hp"] <= 0 for f in b["foes"])

    def _victory(self, b: dict, pc: dict) -> dict:
        b["over"] = True
        b["won"] = True
        self.state.pending_battle = None
        # Bug #1 (audit Claude): sinkronkan HP/Qi yang benar-benar bertarung
        # SEBELUM grant exp — gain_grind_exp bisa memicu level-up yang full-heal
        # di cultivation._level_up; tanpa urutan ini snapshot pra-reward menimpa
        # heal level-up diam-diam.
        self._sync_player(pc)
        # Sinkronkan bila ally ini ternyata berasal dari state kompanion lama.
        for ally in b.get("allies", []):
            for sc in self.state.companions:
                if sc.get("id") == ally["id"]:
                    sc["hp"] = ally["hp"]
                    break
        killed = [f["id"] for f in b["foes"] if f.get("id")]
        if b["context"] in ("spar", "spar_team"):
            arr = self.reg.config.get("cultivation", {}).get("spar_relation_diminishing") or [5, 3, 1]
            if b.get("spar_npc"):
                npc_id = b["spar_npc"]
                if not hasattr(self.state, "daily_spar_counts") or not isinstance(self.state.daily_spar_counts, dict):
                    self.state.daily_spar_counts = {}
                count = self.state.daily_spar_counts.get(npc_id, 0)
                if not isinstance(count, int) or count < 0:
                    count = 0
                rel = arr[count] if count < len(arr) else 0
                self.state.daily_spar_counts[npc_id] = count + 1
                if rel > 0:
                    self.state.relations[npc_id] = self.state.relations.get(npc_id, 0) + rel
                    npc = self.reg.npc(npc_id)
                    npc_name = npc["name"] if npc else npc_id
                    add_log(self.state, "battle", f"Hubungan dengan {npc_name} membaik (+{rel}).")
                self.quest_engine.notify_spar_won(npc_id)
        # drop
        for f in b["foes"]:
            di = f.get("drop_item")
            dc = float(f.get("drop_chance", 0) or 0)
            if di and random.random() < dc:
                self.state.inventory[di] = self.state.inventory.get(di, 0) + 1
                it = self.reg.item(di)
                add_log(self.state, "battle", f"Menemukan: {it['name'] if it else di}.")
        add_log(self.state, "battle", "🏆 Kemenangan!")
        self.quest_engine.notify_battle_won(killed)
        return self.view()

    def _last_exp(self, b: dict) -> int:
        return 0

    def _ko(self, b: dict) -> dict:
        # Perisai Jiwa: one free KO recovery per battle
        if has_realm_bonus(self.state, "perisai_jiwa") and not b.get("ko_shield_used"):
            b["ko_shield_used"] = True
            recover = int(self.state.max_hp(self.reg) * 0.3)
            pc = player_combat(self.state, self.reg)
            pc["hp"] = max(1, recover)
            self._sync_player(pc)
            add_log(self.state, "battle", f"🛡️ Perisai Jiwa! Kau bertahan dari KO (+{recover} HP).")
            return self.view()
        b["over"] = True
        b["won"] = False
        self.state.pending_battle = None
        ratio = self.reg.config.get("ko_penalty", {}).get("exp_loss_ratio", 0.1)
        loss = round(self.state.exp_next(self.reg) * ratio)
        self.state.player.dantian_exp = max(0, self.state.player.dantian_exp - loss)
        if b["context"] in ("spar", "spar_team"):
            # G4a: kalah sparring tetap menyelesaikan objektif `spar`
            if b.get("spar_npc"):
                self.quest_engine.notify_spar_loss(b["spar_npc"])
        # respawn titik aman — data-driven (B2): last_safe → config.world.safe_fallback_location
        # → lokasi is_safe pertama dari data (bukan hardcode nama lokasi arc-1)
        safe = self.state.last_safe_location
        if not safe:
            safe = self.reg.config.get("world", {}).get("safe_fallback_location")
        if not safe:
            safe = next((l["id"] for l in self.reg.locations if l.get("is_safe")), None)
        if not safe and self.reg.locations:
            safe = self.reg.locations[0]["id"]  # lokasi pertama data (validator jamin ≥1 aman)
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
        """Tampilan battle untuk UI — player stats, foes, companion, status."""
        b = self.state.pending_battle
        if not b:
            return {"mode": "explore"}
        pc = player_combat(self.state, self.reg)
        st_cfg = self._status_config()
        return {
            "mode": "battle",
            "player": {"hp": pc["hp"], "hp_max": pc["hp_max"], "qi": pc["qi"], "qi_max": pc["qi_max"]},
            "player_statuses": [
                {"id": sid, "name": st_cfg.get(sid, {}).get("name", sid), "remaining": dur}
                for sid, dur in (b.get("player_statuses") or {}).items()
            ],
            "foes": [
                {"name": f["name"], "hp": f["hp"], "hp_max": f["hp_max"], "element": f.get("element")}
                for f in b.get("foes", [])
            ],
            "companion": companion_stats(self.state, self.reg) if b.get("use_companion", True) else None,
            "allies": [
                {"name": a["name"], "hp": a["hp"], "hp_max": a["hp_max"], "element": a.get("element")}
                for a in b.get("allies", [])
            ],
            "ally_turn_index": b.get("ally_turn_index", 0),
            "active_ally_index": self._active_ally_index(b),
            "over": b.get("over", False),
            "won": b.get("won", False),
            "fled": b.get("player_fled", False),
        }

    def _active_ally_index(self, b: dict) -> int | None:
        allies = b.get("allies", [])
        if not allies:
            return None
        idx = b.get("ally_turn_index", 0)
        for _ in range(len(allies)):
            current = idx % len(allies)
            if allies[current]["hp"] > 0:
                return current
            idx += 1
        return None
