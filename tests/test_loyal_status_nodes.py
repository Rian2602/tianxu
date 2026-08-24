"""Test loyal status nodes — verify that all character status values
(loyal, separated, disillusioned) are consumed by dialog conditions.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_lin_yue_loyal_consumed():
    """state_lin_yue_status='loyal' should be checked by at least one
    dialog node condition (not just via flag_not).
    """
    from src.loader import DataRegistry
    reg = DataRegistry(str(ROOT / "data"))

    found = False
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
                if (isinstance(flag, dict)
                        and flag.get("key") == "state_lin_yue_status"
                        and flag.get("value") == "loyal"):
                    found = True
                    break
        if found:
            break

    assert found, (
        "state_lin_yue_status='loyal' is not checked by any dialog node condition"
    )


def test_mei_ruo_loyal_consumed():
    """state_mei_ruo_status='loyal' should be checked by at least one
    dialog node condition.
    """
    from src.loader import DataRegistry
    reg = DataRegistry(str(ROOT / "data"))

    found = False
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
                if (isinstance(flag, dict)
                        and flag.get("key") == "state_mei_ruo_status"
                        and flag.get("value") == "loyal"):
                    found = True
                    break
        if found:
            break

    assert found, (
        "state_mei_ruo_status='loyal' is not checked by any dialog node condition"
    )


def test_gu_han_loyal_consumed():
    """state_gu_han_status='loyal' should be checked by at least one
    dialog node condition.
    """
    from src.loader import DataRegistry
    reg = DataRegistry(str(ROOT / "data"))

    found = False
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
                if (isinstance(flag, dict)
                        and flag.get("key") == "state_gu_han_status"
                        and flag.get("value") == "loyal"):
                    found = True
                    break
        if found:
            break

    assert found, (
        "state_gu_han_status='loyal' is not checked by any dialog node condition"
    )


def test_reactive_mentor_exists():
    """dlg_a06_reactive_mentor should exist for Arc VI reactivity."""
    from src.loader import DataRegistry
    reg = DataRegistry(str(ROOT / "data"))

    d = reg.dialog_by_id.get("dlg_a06_reactive_mentor")
    assert d is not None, "dlg_a06_reactive_mentor not found"
    assert d.get("npc") == "npc_mentor", (
        f"dlg_a06_reactive_mentor npc should be npc_mentor, got {d.get('npc')}"
    )
