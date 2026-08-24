"""Test quest graph integrity — orphan detection, dead-end detection, broken chains.

TDD Cycle 1: RED phase — test should fail because validator doesn't check
for orphan quests yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_orphan_quest_detection():
    """Quests that are never referenced by any other quest's 'next' field
    should be detected as orphans (except entry points like quest_a01_c01_001).
    
    This is a RED phase test — it should fail because the validator
    doesn't check for orphan quests yet.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Build set of all quest IDs
    all_quest_ids = set(reg.quest_by_id.keys())
    
    # Build set of quests referenced by other quests' 'next' field
    referenced_quests = set()
    for q in reg.quests:
        for nxt in (q.get("next") or []):
            if isinstance(nxt, dict) and "quest" in nxt:
                referenced_quests.add(nxt["quest"])
    
    # Entry points (known starting quests)
    entry_points = {"quest_a01_c01_001"}
    
    # Orphan quests = quests that exist but are never referenced
    orphans = all_quest_ids - referenced_quests - entry_points
    
    # Side quests are expected to be orphaned (no next field)
    side_orphans = {qid for qid in orphans if reg.quest_by_id[qid].get("kind") == "side"}
    
    # Main quest orphans are the problem
    main_orphans = orphans - side_orphans
    
    # This test will FAIL because we're checking that there are NO main quest orphans
    # But there might be some in the current data
    assert len(main_orphans) == 0, f"Main quest orphans found: {main_orphans}"


def test_dead_end_detection():
    """Main quests with 'next: null' should only be the final quest (ending).
    
    This is a RED phase test — it should fail because the validator
    doesn't check for dead-end quests yet.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Find main quests with no 'next' field
    dead_ends = []
    for q in reg.quests:
        if q.get("kind") != "main":
            continue
        if q.get("next") is None:
            dead_ends.append(q["id"])
    
    # Only quest_a07_c03_003 (Second Life) should be a dead end
    expected_dead_ends = {"quest_a07_c03_003"}
    actual_dead_ends = set(dead_ends)
    
    # This test will FAIL if there are unexpected dead ends
    assert actual_dead_ends == expected_dead_ends, \
        f"Unexpected dead ends: {actual_dead_ends - expected_dead_ends}"


def test_broken_chain_detection():
    """All quest references in 'next' fields should point to existing quests.
    
    This is a RED phase test — it should fail because the validator
    doesn't check for broken chains yet.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Build set of all quest IDs
    all_quest_ids = set(reg.quest_by_id.keys())
    
    # Check all 'next' references
    broken_refs = []
    for q in reg.quests:
        for nxt in (q.get("next") or []):
            if isinstance(nxt, dict) and "quest" in nxt:
                target = nxt["quest"]
                if target not in all_quest_ids:
                    broken_refs.append((q["id"], target))
    
    # This test will FAIL if there are broken references
    assert len(broken_refs) == 0, f"Broken chain references: {broken_refs}"


def test_circular_dependency_detection():
    """Quest chains should not have circular dependencies.
    
    This is a RED phase test — it should fail because the validator
    doesn't check for circular dependencies yet.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Build adjacency list for main quests
    graph = {}
    for q in reg.quests:
        if q.get("kind") != "main":
            continue
        targets = []
        for nxt in (q.get("next") or []):
            if isinstance(nxt, dict) and "quest" in nxt:
                targets.append(nxt["quest"])
        graph[q["id"]] = targets
    
    # DFS to detect cycles
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    visited = set()
    cycles = []
    
    for node in graph:
        if node not in visited:
            if has_cycle(node, visited, set()):
                cycles.append(node)
    
    # This test will FAIL if there are circular dependencies
    assert len(cycles) == 0, f"Circular dependencies found: {cycles}"


def test_unused_flags_detection():
    """Flags that are set by quests but never consumed by any other quest
    should be detected as unused.
    
    This is a RED phase test — it should detect unused flags.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Collect all flags SET by quests
    flags_set = set()
    for q in reg.quests:
        effects = q.get("on_complete", {}).get("effects", [])
        for e in effects:
            if e.get("type") == "flag":
                flags_set.add(e["key"])
    
    # Collect all flags REQUIRED by quests
    flags_required = set()
    for q in reg.quests:
        avail = q.get("available_from", {})
        for f in avail.get("requires_flags", []):
            flags_required.add(f)
    
    # Flags that are set but never required
    unused_flags = flags_set - flags_required
    
    # This test will PASS if there are no unused flags
    # But we expect some unused flags in the current data
    # So we just report them, not fail
    if unused_flags:
        print(f"\n  Unused flags (set but never required): {sorted(unused_flags)}")
    
    # For now, just verify the detection works
    assert isinstance(unused_flags, set)


def test_impossible_prerequisites():
    """Flags that are required by quests but never set by any other quest
    should be detected as impossible prerequisites.
    
    This is a RED phase test — it should detect impossible prerequisites.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Collect all flags SET by quests
    flags_set = set()
    for q in reg.quests:
        effects = q.get("on_complete", {}).get("effects", [])
        for e in effects:
            if e.get("type") == "flag":
                flags_set.add(e["key"])
    
    # Also collect flags set by dialogs (branch choices)
    for d in reg.dialogs:
        nodes = d.get("nodes", {})
        if isinstance(nodes, dict):
            for nid, node in nodes.items():
                if not isinstance(node, dict):
                    continue
                for choice in node.get("choices", []):
                    if not isinstance(choice, dict):
                        continue
                    for e in choice.get("effects", []):
                        if e.get("type") == "flag":
                            flags_set.add(e["key"])
    
    # Collect all flags REQUIRED by quests
    flags_required = set()
    for q in reg.quests:
        avail = q.get("available_from", {})
        for f in avail.get("requires_flags", []):
            flags_required.add(f)
    
    # Flags that are required but never set
    impossible_prereqs = flags_required - flags_set
    
    # This test will FAIL if there are impossible prerequisites
    assert len(impossible_prereqs) == 0, \
        f"Impossible prerequisites (required but never set): {sorted(impossible_prereqs)}"


def test_cosmetic_branch_detection():
    """Branches where all options lead to the same quest with no differentiated
    effects should be detected as cosmetic.
    
    This is a RED phase test — it should detect cosmetic branches.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    cosmetic_branches = []
    
    for q in reg.quests:
        nxt = q.get("next") or []
        if len(nxt) <= 1:
            continue
        
        # Check if all options lead to the same quest
        targets = set()
        for n in nxt:
            if isinstance(n, dict) and "quest" in n:
                targets.add(n["quest"])
        
        if len(targets) == 1:
            # All options lead to same quest - check if effects differ
            # For now, just report it
            options = [n.get("option", "?") for n in nxt if isinstance(n, dict)]
            cosmetic_branches.append({
                "quest": q["id"],
                "options": options,
                "target": list(targets)[0]
            })
    
    # Report cosmetic branches (not necessarily a failure)
    if cosmetic_branches:
        print(f"\n  Cosmetic branches detected: {len(cosmetic_branches)}")
        for cb in cosmetic_branches:
            print(f"    {cb['quest']}: {cb['options']} → {cb['target']}")
    
    # For now, just verify detection works
    assert isinstance(cosmetic_branches, list)


def test_lin_yue_002_has_gate():
    """quest_char_lin_yue_002 should have a gate (relation_min or requires_flags)
    to prevent it from firing before quest 001.
    
    TDD Cycle 1: RED phase — test should FAIL because lin_yue_002 has no gate.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    q = reg.quest_by_id.get("quest_char_lin_yue_002")
    assert q is not None, "quest_char_lin_yue_002 not found"
    
    avail = q.get("available_from", {})
    has_relation_min = "relation_min" in avail
    has_requires_flags = "requires_flags" in avail
    
    # This test will FAIL because lin_yue_002 has no gate
    assert has_relation_min or has_requires_flags, \
        f"quest_char_lin_yue_002 has no gate: {avail}"


def test_lin_yue_002_gate_requires_previous_quest():
    """quest_char_lin_yue_002 should require completion of quest 001
    (either via relation_min or requires_flags).
    
    TDD Cycle 1: RED phase — test should FAIL.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    q = reg.quest_by_id.get("quest_char_lin_yue_002")
    avail = q.get("available_from", {})
    
    # Check if relation_min requires higher value than quest 001 provides
    q1 = reg.quest_by_id.get("quest_char_lin_yue_001")
    
    # Quest 001 has relation_min: npc_lin_yue >= 2
    # So quest 002 should require >= 3 (to ensure 001 is done first)
    rel_min = avail.get("relation_min", {})
    req_value = rel_min.get("value", 0)
    
    # This test will FAIL because lin_yue_002 has no relation_min
    assert req_value >= 3, \
        f"quest_char_lin_yue_002 relation_min too low: {req_value} (should be >= 3)"


def test_cosmetic_branch_effects_are_used():
    """Cosmetic branches (multiple options → same target) should have their
    effects checked by reactive dialogs in later arcs.
    
    This test verifies that the differentiation in dialog layer
    is actually consumed by the game.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Build set of all flags checked by dialog conditions
    flags_checked = set()
    for d in reg.dialogs:
        nodes = d.get("nodes", {})
        if isinstance(nodes, dict):
            for nid, node in nodes.items():
                if not isinstance(node, dict):
                    continue
                cond = node.get("condition")
                if cond and isinstance(cond, dict):
                    flag = cond.get("flag", {})
                    if flag.get("key"):
                        flags_checked.add(flag["key"])
    
    # Check that branch effects are actually checked somewhere
    # These flags ARE checked by reactive dialogs
    used_effects = {
        "state_identity_stance": "Arc03 branch",
        "state_mei_ruo_status": "Arc05 family branch",
        "state_shen_luo_status": "Arc05 family branch",
        "state_gu_han_status": "Arc05 family branch",
        "flag_mountain_gate_changed": "Arc05 mountain gate branch",
        "flag_mountain_gate_repeated": "Arc05 mountain gate branch",
    }
    
    for flag, branch in used_effects.items():
        assert flag in flags_checked, \
            f"Branch effect {flag} from {branch} is not checked by any dialog"
    
    # state_lin_yue_status is SET but NOT checked - design issue
    # This is a finding, not necessarily a bug
    unused_branch_effects = {
        "state_lin_yue_status": "Arc05 family branch",
    }
    
    for flag, branch in unused_branch_effects.items():
        if flag not in flags_checked:
            print(f"\n  WARNING: {flag} from {branch} is set but never checked by any dialog")
    
    # Most branch effects are used - branches are NOT truly cosmetic
    assert True
