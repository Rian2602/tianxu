"""Test memory web — verify that all memories have investigation quests
and their resulting flags are consumed.

Phase 6: Memory Web
- Every unlocked memory should have an investigation quest
- Investigation flags should be consumed by reactive dialogs
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _find_unlocked_memories(reg):
    """Find all memories unlocked by quests via memory_unlock field."""
    memories = {}
    for q in reg.quests:
        # Check on_complete.memory_unlock
        oc = q.get("on_complete", {})
        mu = oc.get("memory_unlock", "")
        if mu:
            memories[mu] = q["id"]
        # Check available_from.memory_unlock
        af = q.get("available_from", {})
        mu2 = af.get("memory_unlock", "")
        if mu2:
            memories[mu2] = q["id"]
    return memories


def _find_investigation_quests(reg):
    """Find all investigation quests and which memory they investigate."""
    inv = {}
    for q in reg.quests:
        qid = q.get("id", "")
        if "memory" in qid and "investigat" in qid:
            af = q.get("available_from", {})
            has_mem = af.get("has_memory", "")
            if has_mem:
                inv[has_mem] = qid
    return inv


def _find_investigation_flags_consumed(reg):
    """Find which investigation flags are consumed by dialog conditions."""
    consumed = set()
    for d in reg.dialogs:
        nodes = d.get("nodes", {})
        if not isinstance(nodes, dict):
            continue
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            cond = node.get("condition")
            if cond and isinstance(cond, dict):
                flag = cond.get("flag", {})
                if isinstance(flag, dict) and flag.get("key", "").startswith("flag_memory_"):
                    consumed.add(flag["key"])
    return consumed


def test_all_memories_have_investigation_quests():
    """Every memory unlocked by a quest should have a corresponding
    investigation quest (quest_memory_xxx_investigate).

    TDD Cycle 1: RED phase — should FAIL because 3 memories
    (m03, m05_m01, m06_m01) have no investigation quest.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    unlocked = _find_unlocked_memories(reg)
    investigations = _find_investigation_quests(reg)

    missing = set(unlocked.keys()) - set(investigations.keys())
    assert len(missing) == 0, (
        f"Memories without investigation quests: {sorted(missing)}"
    )


def test_investigation_flags_consumed():
    """Investigation flags (flag_memory_xxx_investigated) set by investigation
    quests should be consumed by at least one dialog condition.

    TDD Cycle 1: RED phase — should FAIL because only m01 flag is consumed.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    investigations = _find_investigation_quests(reg)
    consumed = _find_investigation_flags_consumed(reg)

    # Build expected flags from investigation quests
    expected_flags = set()
    for mem, qid in investigations.items():
        # Derive flag name from memory name
        flag_name = f"flag_{mem}_investigated"
        expected_flags.add(flag_name)

    missing = expected_flags - consumed
    assert len(missing) == 0, (
        f"Investigation flags set but never consumed: {sorted(missing)}"
    )
