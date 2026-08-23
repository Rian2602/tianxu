"""Migration tests — verify save backward compatibility (v7→v9).

Tests that old save files can be loaded and migrated correctly,
with all new fields getting proper defaults.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.state import GameState, PlayerState, SCHEMA_VERSION


def _make_v7_save():
    """Create a minimal v7 save dict (before element_mastery + passives)."""
    return {
        "schema_version": 7,
        "player": {
            "name": "Chen Xu",
            "hp": 50,
            "qi": 30,
            "realm": "realm_chuji",
            "realm_level": 1,
            "gold": 20,
            "roots": "akar_biasa",
            "academy": "pavilion_jianxin",
            "equipment": {"weapon": None},
            "exp": 0,
            "dantian_exp": 0,
            "morality": 0,
            "techniques": ["teknik_dasar", "teknik_jianxin"],
            "technique_levels": {"teknik_dasar": 2, "teknik_jianxin": 1},
        },
        "location": "loc_training_hall",
        "day": 5,
        "hour": 14,
        "current_quest": "quest_a02_c01_001",
        "completed_quests": ["quest_a01_c01_001", "quest_a01_c01_002"],
        "failed_quests": [],
        "active_side_quests": {},
        "side_quest_cooldowns": {},
        "inventory": {"pil_qi": 3, "herba_qi": 5},
        "flags": {"state_murid_status": "registered", "flag_first_lesson_done": True},
        "relations": {"npc_lin_yue": 3, "npc_shen_luo": 2},
        "memories": [{"id": "memory_a01_m01", "reliability": "uncertain"}],
        "talked_npcs": ["npc_lin_yue", "npc_shen_luo"],
        "last_safe_location": "loc_protagonist_room",
        "last_hunt_time": {},
        "grounding_hours_today": 0,
        "exp_grind_today": 0,
        "daily_spar_counts": {},
        "branch_pending": None,
        "branch_quest": None,
        "pending_dialog": None,
        "pending_battle": None,
        "companion": None,
        "companions": [],
        "active_companion": None,
        "npc_states": {},
        "factions": {},
        "realms_unlocked": [],
        "status_effects": [],
        "meditate_week_count": 0,
        "meditate_week_start": 1,
        "pil_sukses_active": False,
        "pil_aman_active": False,
        "fatigue_days": 0,
        "rested_today": False,
        # NOTE: element_mastery and passives are MISSING (v7 save)
    }


def test_v7_save_loads_without_crash():
    """V7 save (without element_mastery/passives) should load without error."""
    d = _make_v7_save()
    state = GameState.from_dict(d)
    assert state.player.name == "Chen Xu"
    assert state.player.realm == "realm_chuji"


def test_v7_migration_element_mastery_default():
    """V7 save should get default element_mastery (all zeros)."""
    d = _make_v7_save()
    state = GameState.from_dict(d)
    assert state.element_mastery == {"logam": 0, "kayu": 0, "tanah": 0, "air": 0, "api": 0}


def test_v7_migration_passives_default():
    """V7 save should get empty passives list."""
    d = _make_v7_save()
    state = GameState.from_dict(d)
    assert state.passives == []


def test_v7_migration_preserves_data():
    """V7 save migration should preserve all existing data."""
    d = _make_v7_save()
    state = GameState.from_dict(d)
    
    # Player data preserved
    assert state.player.name == "Chen Xu"
    assert state.player.hp == 50
    assert state.player.qi == 30
    assert state.player.realm == "realm_chuji"
    assert state.player.gold == 20
    assert state.player.academy == "pavilion_jianxin"
    assert state.player.techniques == ["teknik_dasar", "teknik_jianxin"]
    assert state.player.technique_levels == {"teknik_dasar": 2, "teknik_jianxin": 1}
    
    # Game state preserved
    assert state.location == "loc_training_hall"
    assert state.day == 5
    assert state.hour == 14
    assert state.current_quest == "quest_a02_c01_001"
    assert "quest_a01_c01_001" in state.completed_quests
    assert state.inventory.get("pil_qi") == 3
    assert state.flags.get("state_murid_status") == "registered"
    assert state.relations.get("npc_lin_yue") == 3
    assert len(state.memories) == 1


def test_v7_to_v9_round_trip():
    """V7 save → load → save → load should preserve all data."""
    d = _make_v7_save()
    
    # Load v7 save
    state1 = GameState.from_dict(d)
    
    # Save to dict (will be v9)
    d2 = state1.to_dict()
    assert d2["schema_version"] == SCHEMA_VERSION == 9
    
    # Load again
    state2 = GameState.from_dict(d2)
    
    # Verify round-trip
    assert state2.player.name == state1.player.name
    assert state2.player.techniques == state1.player.techniques
    assert state2.element_mastery == state1.element_mastery
    assert state2.passives == state1.passives
    assert state2.completed_quests == state1.completed_quests
    assert state2.flags == state1.flags


def test_v9_save_has_new_fields():
    """V9 save should include element_mastery and passives."""
    d = _make_v7_save()
    state = GameState.from_dict(d)
    state.element_mastery["logam"] = 50
    state.passives = ["passive_sword_intent"]
    
    d2 = state.to_dict()
    assert "element_mastery" in d2
    assert d2["element_mastery"]["logam"] == 50
    assert "passives" in d2
    assert "passive_sword_intent" in d2["passives"]


def test_schema_version_is_9():
    """SCHEMA_VERSION should be 9 after all migrations."""
    assert SCHEMA_VERSION == 9


# ---------- v2 → v3: factions dari flags + memories string → dict ----------

def _make_v2_save():
    """Create a minimal v2 save dict (before factions/memories format change)."""
    return {
        "schema_version": 2,
        "player": {
            "name": "X", "hp": 50, "qi": 30, "realm": "realm_chuji",
            "realm_level": 1, "gold": 10, "roots": "akar_biasa",
        },
        "location": "loc_start", "day": 1, "hour": 8,
        "current_quest": None,
        "flags": {"rep_orthodox": 5, "rep_reformists": -3, "flag_other": True},
        "memories": ["memory_a", "memory_b"],  # v2: plain strings
        "factions": {},
        "last_hunt_time": {},
    }


def test_v3_migration_factions_from_flags():
    """v2→v3: rep_* flags dipindah ke factions, flag non-rep tetap."""
    d = _make_v2_save()
    state = GameState.from_dict(d)
    assert state.factions == {"orthodox": 5, "reformists": -3}
    assert "rep_orthodox" not in state.flags
    assert "rep_reformists" not in state.flags
    assert state.flags.get("flag_other") is True  # flag non-rep terjaga


def test_v3_migration_memories_format():
    """v2→v3: memories string dibungkus {id, reliability}."""
    d = _make_v2_save()
    state = GameState.from_dict(d)
    assert state.memories == [
        {"id": "memory_a", "reliability": "unknown"},
        {"id": "memory_b", "reliability": "unknown"},
    ]


def test_v3_save_with_dict_memories_preserved():
    """Save v3 (memories sudah dict) tidak boleh double-wrap."""
    d = _make_v2_save()
    d["schema_version"] = 3
    d["memories"] = [{"id": "m1", "reliability": "confirmed"}]
    state = GameState.from_dict(d)
    assert state.memories == [{"id": "m1", "reliability": "confirmed"}]


# ---------- v3 → v4: companion single → companions list ----------

def _make_v3_companion_save():
    """Create a minimal v3 save dict (single companion, before list migration)."""
    return {
        "schema_version": 3,
        "player": {
            "name": "X", "hp": 50, "qi": 30, "realm": "realm_chuji",
            "realm_level": 1, "gold": 10, "roots": "akar_biasa",
        },
        "location": "loc_start", "day": 1, "hour": 8,
        "factions": {"orthodox": 5},
        "memories": [{"id": "m1", "reliability": "known"}],
        "companion": {"id": "serigala", "hp": 20, "active": True},
        "companions": [],
        "active_companion": None,
    }


def test_v4_migration_companion_to_list():
    """v3→v4: companion tunggal dimigrasi ke companions list + jadi aktif."""
    d = _make_v3_companion_save()
    state = GameState.from_dict(d)
    assert len(state.companions) == 1
    assert state.companions[0]["id"] == "serigala"
    assert state.active_companion == "serigala"


def test_v4_migration_preserves_existing_list():
    """companions yang sudah terisi TIDAK boleh tertimpa migrasi."""
    d = _make_v3_companion_save()
    d["companions"] = [{"id": "bangau", "hp": 15, "active": False}]
    d["active_companion"] = "bangau"
    state = GameState.from_dict(d)
    assert state.companions == [{"id": "bangau", "hp": 15, "active": False}]
    assert state.active_companion == "bangau"


def test_v4_no_companion_stays_empty():
    """v3 tanpa companion → list tetap kosong, tanpa active."""
    d = _make_v3_companion_save()
    d["companion"] = None
    state = GameState.from_dict(d)
    assert state.companions == []
    assert state.active_companion is None


# ---------- v4 → v5: realm rename + dantian/realms_unlocked/status_effects ----------

def _make_v4_save():
    """Create a minimal v4 save dict (old realm IDs, before dantian fields)."""
    return {
        "schema_version": 4,
        "player": {
            "name": "X", "hp": 50, "qi": 30, "realm": "realm_awal",
            "realm_level": 1, "gold": 10, "roots": "akar_biasa",
        },
        "location": "loc_start", "day": 1, "hour": 8,
        "factions": {}, "memories": [],
        "companion": None, "companions": [],
        "active_companion": None,
    }


def test_v5_migration_realm_rename():
    """v4→v5: ID ranah lama dipetakan ke nama baru."""
    d = _make_v4_save()
    state = GameState.from_dict(d)
    assert state.player.realm == "realm_chuji"


def test_v5_migration_all_old_realms_mapped():
    """Semua tiga ID lama terpetakan: awal→chuji, tengah→xuanshi, atas→dishi."""
    mapping = {"realm_tengah": "realm_xuanshi", "realm_atas": "realm_dishi"}
    for old, new in mapping.items():
        d = _make_v4_save()
        d["player"]["realm"] = old
        state = GameState.from_dict(d)
        assert state.player.realm == new, f"{old} → {new}"


def test_v5_migration_new_realm_id_untouched():
    """ID ranah yang sudah baru dilewati migrasi tanpa perubahan."""
    d = _make_v4_save()
    d["player"]["realm"] = "realm_xuanshi"
    state = GameState.from_dict(d)
    assert state.player.realm == "realm_xuanshi"


def test_v5_migration_dantian_fields_default():
    """Save v4 tanpa field dantian → default aman (0 / list kosong)."""
    d = _make_v4_save()
    state = GameState.from_dict(d)
    assert state.player.dantian_exp == 0
    assert state.realms_unlocked == []
    assert state.status_effects == []
