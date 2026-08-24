"""Test quest completion log shows unique messages for sequential quests.

TDD Cycle 1: RED phase — test should fail because all three quests
have the same title "Kenali Teman Sekelas".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_quest_titles_unique_for_sequential_quests():
    """Quest titles should be unique for sequential quests in the same chain."""
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Sequential quests in Arc 1 (kenalan 3 murid)
    sequential_quests = [
        "quest_a01_c02_003b",
        "quest_a01_c02_003c", 
        "quest_a01_c02_003d",
    ]
    
    titles = []
    for qid in sequential_quests:
        q = reg.quest(qid)
        assert q is not None, f"Quest {qid} not found"
        titles.append(q.get("title", ""))
    
    # All titles should be unique
    assert len(titles) == len(set(titles)), \
        f"Quest titles should be unique, but got: {titles}"
    
    # Each title should contain the NPC name for clarity
    expected_npcs = ["Lin Yue", "Shen Luo", "Gu Han"]
    for title, npc in zip(titles, expected_npcs):
        assert npc.lower() in title.lower(), \
            f"Quest title '{title}' should contain NPC name '{npc}'"


def test_quest_completion_log_shows_npc_name():
    """Quest completion log should show which NPC was just met."""
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Check that quest titles differentiate NPCs
    quests = {
        "quest_a01_c02_003b": "Lin Yue",
        "quest_a01_c02_003c": "Shen Luo",
        "quest_a01_c02_003d": "Gu Han",
    }
    
    for qid, expected_npc in quests.items():
        q = reg.quest(qid)
        assert q is not None, f"Quest {qid} not found"
        title = q.get("title", "")
        assert expected_npc.lower() in title.lower(), \
            f"Quest {qid} title '{title}' should contain '{expected_npc}'"
