"""Test that hunt spawns align with quest enemy requirements.

Bug #3: hunt_hutan_akademi has mini_boss=penjaga_formation, but
quest_a01_c04_005c only counts binatang_hutan kills. This means
a mini-boss kill doesn't advance the quest, making progress random.

Fix: remove mini-boss from hunt_hutan_akademi so quest is deterministic.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_config():
    with open(ROOT / "data" / "config.json") as f:
        return json.load(f)


def _load_quests(arc_file: str):
    with open(ROOT / f"data/quests/{arc_file}") as f:
        return json.load(f).get("quests", [])


def test_hunt_hutan_no_mini_boss():
    """hunt_hutan_akademi should not have a mini-boss that quest doesn't count."""
    config = _load_config()
    quests = _load_quests("arc01.json")

    # Find the hunt
    hunts = config.get("world", {}).get("hunts", [])
    hunt = next((h for h in hunts if h["id"] == "hunt_hutan_akademi"), None)
    assert hunt is not None, "hunt_hutan_akademi not found in config"

    # Find the quest that uses this hunt's location
    quest = next((q for q in quests if q["id"] == "quest_a01_c04_005c"), None)
    assert quest is not None, "quest_a01_c04_005c not found"

    quest_enemies = set(quest.get("objective", {}).get("enemies", []))

    # All possible spawns from this hunt must be in quest enemies
    all_spawns = set(hunt.get("pool", []))
    if hunt.get("mini_boss"):
        all_spawns.add(hunt["mini_boss"])

    unexpected = all_spawns - quest_enemies
    assert not unexpected, (
        f"Hunt spawns {unexpected} not counted by quest enemies {quest_enemies}. "
        f"Either add them to the quest or remove from hunt."
    )


def test_all_hunt_spawns_counted_by_quest():
    """Every hunt's pool + mini-boss should be countable by the quest at that location."""
    config = _load_config()
    hunts = config.get("world", {}).get("hunts", [])

    # Map: location -> quests with defeat objectives
    location_quests = {}
    for arc_file in ["arc01.json", "arc02.json", "arc03.json", "arc04.json",
                      "arc05.json", "arc06.json", "arc07.json"]:
        try:
            quests = _load_quests(arc_file)
        except FileNotFoundError:
            continue
        for q in quests:
            obj = q.get("objective", {})
            if obj.get("kind") == "defeat":
                loc = obj.get("location", "")
                enemies = set(obj.get("enemies", []))
                if loc:
                    location_quests[loc] = enemies

    # For each hunt, check if spawns align with quests at that location
    for hunt in hunts:
        loc = hunt.get("location", "")
        all_spawns = set(hunt.get("pool", []))
        if hunt.get("mini_boss"):
            all_spawns.add(hunt["mini_boss"])

        if loc in location_quests:
            quest_enemies = location_quests[loc]
            unexpected = all_spawns - quest_enemies
            assert not unexpected, (
                f"Hunt {hunt['id']} at {loc}: spawns {unexpected} "
                f"not counted by quest enemies {quest_enemies}"
            )
