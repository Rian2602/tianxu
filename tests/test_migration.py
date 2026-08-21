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
