"""Test narrative integration — verify that side quest effects are used by main story.

TDD Cycle 1: RED phase — test should FAIL because state_lin_yue_status
is set but never checked by any dialog.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_state_lin_yue_status_is_checked_in_ending():
    """state_lin_yue_status is set by Arc05 family branch and should be
    checked by Arc07 ending dialog to make the branch decision meaningful.
    
    TDD Cycle 1: RED phase — test should FAIL because state_lin_yue_status
    is not checked by any dialog node condition.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Build set of all flags checked by dialog NODE conditions
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
    
    # state_lin_yue_status should be checked in a node condition
    # This test will FAIL because it's only checked in choice conditions
    assert "state_lin_yue_status" in flags_checked, \
        "state_lin_yue_status is set by Arc05 branch but never checked by any dialog node condition"


def test_all_character_status_flags_are_checked():
    """All 4 character status flags from Arc05 family branch should be
    checked by reactive dialogs to make the branch decision meaningful.
    
    TDD Cycle 1: RED phase — test should FAIL because state_lin_yue_status
    is not checked.
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
    
    # All 4 character status flags should be checked
    character_flags = {
        "state_lin_yue_status",
        "state_mei_ruo_status", 
        "state_shen_luo_status",
        "state_gu_han_status",
    }
    
    missing = character_flags - flags_checked
    
    # This test will FAIL because state_lin_yue_status is missing
    assert len(missing) == 0, \
        f"Character status flags not checked by any dialog: {missing}"


def test_arc07_dialog_uses_character_statuses():
    """Arc07 opening dialog (dlg_a07_d01) should have conditional nodes that
    check character status flags to provide different opening text.
    
    TDD Cycle 1: RED phase — test should FAIL because state_lin_yue_status
    is not checked in node conditions.
    """
    from src.loader import DataRegistry
    
    reg = DataRegistry(str(ROOT / "data"))
    
    # Check dlg_a07_d01 for character status checks
    d = reg.dialog_by_id.get("dlg_a07_d01")
    assert d is not None, "dlg_a07_d01 not found"
    
    # Collect all flags checked in NODE conditions
    flags_checked = set()
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
    
    # Check that state_lin_yue_status is checked in node conditions
    # This test will FAIL because it's not checked
    assert "state_lin_yue_status" in flags_checked, \
        f"dlg_a07_d01 does not check state_lin_yue_status in node conditions. Checked: {flags_checked}"
