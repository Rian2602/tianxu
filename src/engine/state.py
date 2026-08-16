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
SCHEMA_VERSION = 1


@dataclass
class PlayerState:
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
    morality: int = 0
    techniques: list[str] = field(default_factory=list)  # C1: teknik yang dimiliki (reward quest/dialog)
    technique_levels: dict[str, int] = field(default_factory=dict)  # C1: level per teknik (default 1)


class UIState:
    """Helper proxy agar `state.ui.mode` dan `state.ui.battle` dapat diakses/diubah."""

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
    memories: list = field(default_factory=list)  # id ingatan terbuka
    talked_npcs: set = field(default_factory=set)  # npc_id yang pernah diajak bicara (routing dialog)
    log: list = field(default_factory=list)
    last_safe_location: str | None = None
    last_hunt_time: int | None = None
    grounding_hours_today: int = 0
    exp_grind_today: int = 0  # cap exp grinding harian (berburu/spar/side quest)
    daily_spar_counts: dict = field(default_factory=dict)
    branch_pending: str | None = None  # dialog id untuk pilih cabang quest
    pending_dialog: str | None = None
    pending_battle: dict | None = None  # data battle aktif (dict, lihat battle.py)
    companion: dict | None = None  # {"id", "hp", "active"} — jalur Summoning (ENGINE §9.4)
    npc_states: dict = field(default_factory=dict)  # npc_id -> {"location"?, "available"?} — efek npc_state
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
        """Bulan (1-based) dihitung dari `day` — derived, tidak diserialisasi,
        jadi save lama otomatis kompatibel tanpa migrasi. `month_length_days`
        dari `config.time` (default 30)."""
        mld = int((registry.config.get("time", {}) or {}).get("month_length_days", 30))
        # `(day−1) // mld + 1`: day 1..30 = Bulan 1, day 31..60 = Bulan 2, dst.
        # (deviasi 1 baris dari formula plan `day // mld + 1` — yang terakhir
        # off-by-one di kelipatan persis: day 30 → Bulan 2 padahal masih Bulan 1;
        # kasus plan day 1/31/61 tetap terpenuhi)
        return max(1, (self.day - 1) // mld + 1)

    def month_name(self, registry) -> str:
        """Nama tampilan bulan — dari `config.time.month_names` (bila ada 12
        nama); fallback `f"Bulan {month}"` (data arc berikutnya bisa isi nama)."""
        names = (registry.config.get("time", {}) or {}).get("month_names")
        if isinstance(names, list) and len(names) >= self.month(registry):
            return names[self.month(registry) - 1]
        return f"Bulan {self.month(registry)}"

    # ---------- batas stat ----------

    def max_hp(self, registry) -> int:
        r = registry.realm_by_id(self.player.realm)
        if not r:
            return self.player.hp
        base = int(r["base_hp"])
        per = int(r["hp_per_level"])
        return base + (self.player.realm_level - 1) * per

    def max_qi(self, registry) -> int:
        r = registry.realm_by_id(self.player.realm)
        if not r:
            return self.player.qi
        base = int(r["base_qi"])
        per = int(r["qi_per_level"])
        return base + (self.player.realm_level - 1) * per

    def exp_next(self, registry) -> int:
        """Exp yang dibutuhkan untuk naik dari tingkat saat ini ke berikutnya."""
        c = registry.config.get("cultivation", {})
        base = c.get("exp_per_level_base", 10)
        growth = c.get("exp_growth_per_level", 1.2)
        return round(base * (growth ** (self.player.realm_level - 1)))

    def exp_multiplier(self, registry) -> float:
        tier = registry.roots_tier.get(self.player.roots)
        return tier.get("exp_multiplier", 1.0) if tier else 1.0

    # ---------- serialisasi ----------

    def to_dict(self) -> dict:
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
            "daily_spar_counts": {k: v for k, v in self.daily_spar_counts.items() if isinstance(k, str) and isinstance(v, int) and v >= 0} if isinstance(self.daily_spar_counts, dict) else {},
            "branch_pending": self.branch_pending,
            "pending_battle": copy.deepcopy(self.pending_battle) if self.pending_battle else None,
            "companion": copy.deepcopy(self.companion) if self.companion else None,
            "npc_states": copy.deepcopy(self.npc_states),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        ver = d.get("schema_version")
        if ver is not None and ver > SCHEMA_VERSION:
            raise ValueError(f"save versi {ver} lebih baru dari engine (v{SCHEMA_VERSION}) — perbarui game dulu")
        p = d["player"]
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
            flags=copy.deepcopy(d.get("flags", {})),
            relations=copy.deepcopy(d.get("relations", {})),
            memories=copy.deepcopy(d.get("memories", [])),
            talked_npcs=set(d.get("talked_npcs", [])),
            last_safe_location=d.get("last_safe_location"),
            last_hunt_time=d.get("last_hunt_time"),
            grounding_hours_today=d.get("grounding_hours_today", 0),
            exp_grind_today=d.get("exp_grind_today", 0),
            daily_spar_counts=cleaned_spar,
            branch_pending=d.get("branch_pending"),
            pending_battle=copy.deepcopy(d.get("pending_battle")),
            companion=copy.deepcopy(d.get("companion")),
            npc_states=copy.deepcopy(d.get("npc_states", {})),
        )
