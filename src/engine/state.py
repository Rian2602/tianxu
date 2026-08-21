"""State game — dataclass pemain & sesi.

State adalah satu-satunya sumber kebenaran runtime. Semua perubahan
dilakukan lewat sesi (session.py) yang juga menulis log.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

# Versi skema save (ENGINE_ARCHITECTURE §13). Naikkan saat format save berubah
# MAKNA (bukan sekadar field baru) — `from_dict` wajib migrasi/penolakan.
# Save tanpa key = versi legacy (v0): toleran via `.get(..., default)`.
#
# v1 → v2 (F2.3): `last_hunt_time` int (satu zona global) → dict[str, int]
# (timer per zona berburu). Migrator: int → {"legacy": int} agar timer v1
# tetap dihormati oleh zona legacy.
#
# v2 → v3: factions dari flags (rep_*) + memories string → dict{reliability}
SCHEMA_VERSION = 8


@dataclass
class PlayerState:
    """Data status pemain — semua stat yang berubah selama sesi.

    Attributes:
        name: Nama karakter pemain.
        hp: Poin kesehatan saat ini.
        qi: Energi qi saat ini.
        realm: ID ranah kultivasi aktif.
        level: Level (tier) dalam ranah saat ini.
        gold: Jumlah emas.
        roots: Tipe akar spiritual.
        academy: ID akademi (opsional).
        equipment: Peralatan yang dipasang.
        exp: Pengalaman total yang dimiliki.
        dantian_exp: Exp di dantian (mengisi ke dantian_capacity untuk breakthrough).
        morality: Skor moralitas.
        techniques: Daftar ID teknik yang dimiliki.
        technique_levels: Level per teknik {id: level}.
    """
    name: str
    hp: int
    qi: int
    realm: str
    realm_level: int
    gold: int
    roots: str
    academy: str | None = None
    equipment: dict = field(default_factory=lambda: {"weapon": None})
    exp: int = 0
    dantian_exp: int = 0  # exp in dantian, fills toward dantian_capacity
    morality: int = 0
    techniques: list[str] = field(default_factory=list)
    technique_levels: dict[str, int] = field(default_factory=dict)


class UIState:
    """Proxy untuk state.ui.mode dan state.ui.battle — akses/ubah UI state.

    Attributes:
        mode: Mode UI saat ini ('explore', 'battle', 'dialog').
        battle: Data battle aktif (dict atau kosong).
    """

    def __init__(self, state: "GameState") -> None:
        self._state = state
        self._mode: str = "explore"
        self._battle: dict = {}

    @property
    def mode(self) -> str:
        if self._state.pending_battle:
            return "battle"
        if self._state.pending_dialog:
            return "dialog"
        return self._mode

    @mode.setter
    def mode(self, val: str) -> None:
        self._mode = val
        if val == "battle" and not self._state.pending_battle:
            self._state.pending_battle = {"active": True}
        elif val != "battle" and self._state.pending_battle:
            self._state.pending_battle = None

    @property
    def battle(self) -> dict:
        if self._state.pending_battle:
            return self._state.pending_battle
        return self._battle

    @battle.setter
    def battle(self, val: dict) -> None:
        self._battle = val if isinstance(val, dict) else {}
        if self._battle and self._battle.get("active"):
            self._state.pending_battle = self._battle
        elif not self._battle and self._state.pending_battle:
            self._state.pending_battle = None


@dataclass
class GameState:
    """State utama game — satu-satunya sumber kebenaran runtime.

    Semua perubahan state dilakukan lewat GameSession (session.py)
    yang juga menulis log. State ini di-serialize/deserialize
    untuk save/load game.
    """
    player: PlayerState
    location: str
    day: int
    hour: int
    current_quest: str | None
    completed_quests: list = field(default_factory=list)
    failed_quests: list = field(default_factory=list)  # G3-T1: quest gagal (timeout)
    active_side_quests: dict = field(default_factory=dict)  # qid -> progress
    side_quest_cooldowns: dict = field(default_factory=dict)  # qid -> absolute hour
    inventory: dict = field(default_factory=dict)  # item_id -> count
    flags: dict = field(default_factory=dict)
    relations: dict = field(default_factory=dict)  # npc_id -> skor
    memories: list = field(default_factory=list)  # list of dicts: {id, reliability}
    talked_npcs: set = field(default_factory=set)  # npc_id yang pernah diajak bicara (routing dialog)
    log: list = field(default_factory=list)
    last_safe_location: str | None = None
    last_hunt_time: dict[str, int] | None = None  # hunt_id -> jam absolut (F2.3)
    grounding_hours_today: int = 0
    exp_grind_today: int = 0  # cap exp grinding harian (berburu/spar/side quest)
    daily_spar_counts: dict = field(default_factory=dict)
    branch_pending: str | None = None  # dialog id untuk pilih cabang quest
    branch_quest: str | None = None  # quest id yang memicu branch (bukti eksplisit,
    #                                   hindari pencarian mundur di completed_quests)
    pending_dialog: str | None = None
    pending_battle: dict | None = None  # data battle aktif (dict, lihat battle.py)
    companion: dict | None = None  # {"id", "hp", "active"} — backward compat (v3 save)
    companions: list = field(default_factory=list)  # [{"id", "hp", "active"}] — all owned companions
    active_companion: str | None = None  # ID of companion in battle
    npc_states: dict = field(default_factory=dict)  # npc_id -> {"location"?, "available"?} — efek npc_state
    factions: dict = field(default_factory=dict)  # faksi_id -> skor (orthodox, reformation, dll.)
    realms_unlocked: list = field(default_factory=list)  # list of realm IDs with bonus unlocked
    status_effects: list = field(default_factory=list)  # [{"type", "days_left", ...}] — temporary buffs/debuffs
    meditate_week_count: int = 0  # berapa kali meditasi minggu ini
    meditate_week_start: int = 1  # hari pertama minggu ini (reset when day - start >= 7)
    pil_sukses_active: bool = False  # +30% success rate meditasi
    pil_aman_active: bool = False  # batalkan debuff gagal meditasi
    fatigue_days: int = 0  # hari berturut-turut tanpa istirahat
    rested_today: bool = False  # apakah sudah istirahat hari ini
    element_mastery: dict = field(default_factory=lambda: {"logam": 0, "kayu": 0, "tanah": 0, "air": 0, "api": 0})
    _ui_proxy: UIState | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._ui_proxy = UIState(self)

    @property
    def ui(self) -> UIState:
        if self._ui_proxy is None:
            self._ui_proxy = UIState(self)
        return self._ui_proxy


    @property
    def absolute_hours(self) -> int:
        return self.day * 24 + self.hour

    # ---------- waktu: bulan (derived — C2, GDD §7) ----------

    def month(self, registry) -> int:
        """Hitung nomor bulan berdasarkan hari saat ini."""
        mld = int((registry.config.get("time", {}) or {}).get("month_length_days", 30))
        return max(1, (self.day - 1) // mld + 1)

    def month_name(self, registry) -> str:
        """Nama bulan dari config (opsional, fallback ke 'Bulan N')."""
        names = (registry.config.get("time", {}) or {}).get("month_names")
        if isinstance(names, list) and len(names) >= self.month(registry):
            return names[self.month(registry) - 1]
        return f"Bulan {self.month(registry)}"

    # ---------- batas stat ----------

    def max_hp(self, registry) -> int:
        """HP maksimum = base_hp + (tier-1) × hp_per_tier dari ranah, dikurangi fatigue."""
        r = registry.realm_by_id(self.player.realm)
        if not r or not r.get("base_hp"):
            return 50
        base = int(r["base_hp"])
        per = int(r.get("hp_per_tier", 0) or 0)
        lvl = max(1, self.player.realm_level)
        result = base + (lvl - 1) * per
        for eff in self.status_effects:
            if "hp_mult" in eff:
                result = int(result * eff["hp_mult"])
        rest_cfg = (registry.config.get("rest") or {})
        hp_penalty = int(rest_cfg.get("hp_penalty_per_day", 2))
        max_penalty = int(rest_cfg.get("max_hp_penalty", 20))
        fatigue_penalty = min(self.fatigue_days * hp_penalty, max_penalty)
        result -= fatigue_penalty
        return max(1, result)

    def max_qi(self, registry) -> int:
        """Qi maksimum = base_qi + (tier-1) × qi_per_tier dari ranah, dikurangi fatigue."""
        r = registry.realm_by_id(self.player.realm)
        if not r or not r.get("base_qi"):
            return 30
        base = int(r["base_qi"])
        per = int(r.get("qi_per_tier", 0) or 0)
        lvl = max(1, self.player.realm_level)
        result = base + (lvl - 1) * per
        for eff in self.status_effects:
            if "qi_mult" in eff:
                result = int(result * eff["qi_mult"])
        rest_cfg = (registry.config.get("rest") or {})
        qi_penalty = int(rest_cfg.get("qi_penalty_per_day", 1))
        max_penalty = int(rest_cfg.get("max_qi_penalty", 10))
        fatigue_penalty = min(self.fatigue_days * qi_penalty, max_penalty)
        result -= fatigue_penalty
        return max(1, result)

    def exp_next(self, registry) -> int:
        """Dantian capacity — exp needed to fill dantian for breakthrough."""
        r = registry.realm_by_id(self.player.realm)
        if r and r.get("dantian_capacity"):
            return int(r["dantian_capacity"])
        return 20  # sane default

    def exp_multiplier(self, registry) -> float:
        """Multiplier exp berdasarkan tier akar spiritual."""
        tier = registry.roots_tier.get(self.player.roots)
        return tier.get("exp_multiplier", 1.0) if tier else 1.0

    # ---------- serialisasi ----------

    def to_dict(self) -> dict:
        """Serialisasi state ke dict untuk save file (JSON-safe)."""
        return {
            "schema_version": SCHEMA_VERSION,
            "player": {
                "name": self.player.name,
                "hp": self.player.hp,
                "qi": self.player.qi,
                "realm": self.player.realm,
                "realm_level": self.player.realm_level,
                "gold": self.player.gold,
                "roots": self.player.roots,
                "academy": self.player.academy,
                "equipment": copy.deepcopy(self.player.equipment),
                "exp": self.player.exp,
                "dantian_exp": self.player.dantian_exp,
                "morality": self.player.morality,
                "techniques": copy.deepcopy(self.player.techniques),
                "technique_levels": copy.deepcopy(self.player.technique_levels),
            },
            "location": self.location,
            "day": self.day,
            "hour": self.hour,
            "current_quest": self.current_quest,
            "completed_quests": copy.deepcopy(self.completed_quests),
            "failed_quests": copy.deepcopy(self.failed_quests),
            "active_side_quests": copy.deepcopy(self.active_side_quests),
            "side_quest_cooldowns": copy.deepcopy(self.side_quest_cooldowns),
            "inventory": copy.deepcopy(self.inventory),
            "flags": copy.deepcopy(self.flags),
            "relations": copy.deepcopy(self.relations),
            "memories": copy.deepcopy(self.memories),
            "talked_npcs": sorted(self.talked_npcs),
            "last_safe_location": self.last_safe_location,
            "last_hunt_time": self.last_hunt_time,
            "grounding_hours_today": self.grounding_hours_today,
            "exp_grind_today": self.exp_grind_today,
            "daily_spar_counts": {
                k: v for k, v in self.daily_spar_counts.items()
                if isinstance(k, str) and isinstance(v, int) and v >= 0
            } if isinstance(self.daily_spar_counts, dict) else {},
            "branch_pending": self.branch_pending,
            "branch_quest": self.branch_quest,
            "pending_dialog": self.pending_dialog,
            "pending_battle": copy.deepcopy(self.pending_battle) if self.pending_battle else None,
            "companion": copy.deepcopy(self.companion) if self.companion else None,
            "companions": copy.deepcopy(self.companions),
            "active_companion": self.active_companion,
            "npc_states": copy.deepcopy(self.npc_states),
            "factions": copy.deepcopy(self.factions),
            "realms_unlocked": copy.deepcopy(self.realms_unlocked),
            "status_effects": copy.deepcopy(self.status_effects),
            "meditate_week_count": self.meditate_week_count,
            "meditate_week_start": self.meditate_week_start,
            "pil_sukses_active": self.pil_sukses_active,
            "pil_aman_active": self.pil_aman_active,
            "fatigue_days": self.fatigue_days,
            "rested_today": self.rested_today,
            "element_mastery": copy.deepcopy(self.element_mastery),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        """Deserialisasi state dari dict — handle migrasi save lama (v0→v3)."""
        ver = d.get("schema_version")
        if ver is not None and ver > SCHEMA_VERSION:
            raise ValueError(f"save versi {ver} lebih baru dari engine (v{SCHEMA_VERSION}) — perbarui game dulu")

        # Migrasi v0/v1 → v2: last_hunt_time int → dict per zona
        raw_lht = d.get("last_hunt_time")
        if isinstance(raw_lht, dict):
            lht = {k: v for k, v in raw_lht.items()
                   if isinstance(k, str) and isinstance(v, int) and v >= 0}
        elif isinstance(raw_lht, int) and raw_lht >= 0:
            lht = {"legacy": raw_lht}
        else:
            lht = {}

        # v0/v1/v2 → v3: factions dari flags + memories string → dict
        v = ver or 0
        raw_flags = copy.deepcopy(d.get("flags", {}))
        factions = copy.deepcopy(d.get("factions", {}))
        if v < 3:
            for key in list(raw_flags):
                if key.startswith("rep_"):
                    faksi = key[4:]
                    factions[faksi] = factions.get(faksi, 0) + raw_flags.pop(key)

        raw_mems = d.get("memories", [])
        if v < 3:
            memories = [
                {"id": m, "reliability": "unknown"} if isinstance(m, str) else m
                for m in raw_mems
            ]
        else:
            memories = copy.deepcopy(raw_mems)

        # v3 → v4: companion single → companions list
        companions = copy.deepcopy(d.get("companions", []))
        active_companion = d.get("active_companion")
        if v < 4:
            old_comp = d.get("companion")
            if old_comp and isinstance(old_comp, dict) and old_comp.get("id"):
                if not companions:
                    companions = [copy.deepcopy(old_comp)]
                if not active_companion:
                    active_companion = old_comp["id"]

        # v4 → v5: dantian system, realms_unlocked, status_effects
        # Map old realm IDs to new ones
        _realm_map = {
            "realm_awal": "realm_chuji",
            "realm_tengah": "realm_xuanshi",
            "realm_atas": "realm_dishi",
        }
        p = d["player"]
        if v < 5 and p.get("realm") in _realm_map:
            p["realm"] = _realm_map[p["realm"]]
        raw_spar = d.get("daily_spar_counts")
        cleaned_spar = {k: v for k, v in raw_spar.items() if isinstance(k, str) and isinstance(v, int) and v >= 0} if isinstance(raw_spar, dict) else {}
        return cls(
            player=PlayerState(
                name=p["name"],
                hp=p["hp"],
                qi=p["qi"],
                realm=p["realm"],
                realm_level=p["realm_level"],
                gold=p.get("gold", 0),
                roots=p.get("roots", "akar_mid"),
                academy=p.get("academy"),
                equipment=copy.deepcopy(p.get("equipment", {"weapon": None})),
                exp=p.get("exp", 0),
                dantian_exp=p.get("dantian_exp", 0),
                morality=p.get("morality", 0),
                techniques=copy.deepcopy(p.get("techniques", [])),
                technique_levels=copy.deepcopy(p.get("technique_levels", {})),
            ),
            location=d["location"],
            day=d["day"],
            hour=d["hour"],
            current_quest=d.get("current_quest"),
            completed_quests=copy.deepcopy(d.get("completed_quests", [])),
            failed_quests=copy.deepcopy(d.get("failed_quests", [])),
            active_side_quests=copy.deepcopy(d.get("active_side_quests", {})),
            side_quest_cooldowns=copy.deepcopy(d.get("side_quest_cooldowns", {})),
            inventory=copy.deepcopy(d.get("inventory", {})),
            flags=raw_flags,
            relations=copy.deepcopy(d.get("relations", {})),
            memories=memories,
            talked_npcs=set(d.get("talked_npcs", [])),
            last_safe_location=d.get("last_safe_location"),
            last_hunt_time=lht,
            grounding_hours_today=d.get("grounding_hours_today", 0),
            exp_grind_today=d.get("exp_grind_today", 0),
            daily_spar_counts=cleaned_spar,
            branch_pending=d.get("branch_pending"),
            branch_quest=d.get("branch_quest"),  # None utk save lama → fallback pencarian
            pending_dialog=d.get("pending_dialog"),
            pending_battle=copy.deepcopy(d.get("pending_battle")),
            companion=copy.deepcopy(d.get("companion")),
            companions=companions,
            active_companion=active_companion,
            npc_states=copy.deepcopy(d.get("npc_states", {})),
            factions=factions,
            realms_unlocked=copy.deepcopy(d.get("realms_unlocked", [])),
            status_effects=copy.deepcopy(d.get("status_effects", [])),
            meditate_week_count=d.get("meditate_week_count", 0),
            meditate_week_start=d.get("meditate_week_start", 1),
            pil_sukses_active=d.get("pil_sukses_active", False),
            pil_aman_active=d.get("pil_aman_active", False),
            fatigue_days=d.get("fatigue_days", 0),
            rested_today=d.get("rested_today", False),
            element_mastery=copy.deepcopy(d.get("element_mastery", {"logam": 0, "kayu": 0, "tanah": 0, "air": 0, "api": 0})),
        )
