"""State game — dataclass pemain & sesi.

State adalah satu-satunya sumber kebenaran runtime. Semua perubahan
dilakukan lewat sesi (session.py) yang juga menulis log.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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


@dataclass
class GameState:
    player: PlayerState
    location: str
    day: int
    hour: int
    current_quest: str | None
    completed_quests: list = field(default_factory=list)
    active_side_quests: dict = field(default_factory=dict)  # qid -> progress
    inventory: dict = field(default_factory=dict)  # item_id -> count
    flags: dict = field(default_factory=dict)
    relations: dict = field(default_factory=dict)  # npc_id -> skor
    memories: list = field(default_factory=list)  # id ingatan terbuka
    log: list = field(default_factory=list)
    last_safe_location: str | None = None
    grounding_hours_today: int = 0
    branch_pending: str | None = None  # dialog id untuk pilih cabang quest
    pending_dialog: str | None = None
    pending_battle: dict | None = None  # data battle aktif (dict, lihat battle.py)
    companion: dict | None = None  # {"id", "hp", "active"} — jalur Summoning (ENGINE §9.4)

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
            "player": {
                "name": self.player.name,
                "hp": self.player.hp,
                "qi": self.player.qi,
                "realm": self.player.realm,
                "realm_level": self.player.realm_level,
                "gold": self.player.gold,
                "roots": self.player.roots,
                "academy": self.player.academy,
                "equipment": self.player.equipment,
                "exp": self.player.exp,
                "morality": self.player.morality,
            },
            "location": self.location,
            "day": self.day,
            "hour": self.hour,
            "current_quest": self.current_quest,
            "completed_quests": self.completed_quests,
            "active_side_quests": self.active_side_quests,
            "inventory": self.inventory,
            "flags": self.flags,
            "relations": self.relations,
            "memories": self.memories,
            "last_safe_location": self.last_safe_location,
            "grounding_hours_today": self.grounding_hours_today,
            "branch_pending": self.branch_pending,
            "pending_dialog": self.pending_dialog,
            "pending_battle": self.pending_battle,
            "companion": self.companion,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        p = d["player"]
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
                equipment=p.get("equipment", {"weapon": None}),
                exp=p.get("exp", 0),
                morality=p.get("morality", 0),
            ),
            location=d["location"],
            day=d["day"],
            hour=d["hour"],
            current_quest=d.get("current_quest"),
            completed_quests=d.get("completed_quests", []),
            active_side_quests=d.get("active_side_quests", {}),
            inventory=d.get("inventory", {}),
            flags=d.get("flags", {}),
            relations=d.get("relations", {}),
            memories=d.get("memories", []),
            last_safe_location=d.get("last_safe_location"),
            grounding_hours_today=d.get("grounding_hours_today", 0),
            branch_pending=d.get("branch_pending"),
            pending_dialog=d.get("pending_dialog"),
            pending_battle=d.get("pending_battle"),
            companion=d.get("companion"),
        )
