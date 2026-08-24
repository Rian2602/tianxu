"""Test meaningful branching — verify that all branch option values are consumed.

TDD Cycle 1: RED phase — tests should FAIL because state_identity_stance
values 'deny' and 'accept_cautious' are set by arc03 branch but never
checked by any dialog condition.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _find_dialog_conditions(reg):
    """Build set of all (key, value) pairs checked by dialog node conditions."""
    checked = set()
    for d in reg.dialogs:
        nodes = d.get("nodes", {})
        if not isinstance(nodes, dict):
            continue
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            cond = node.get("condition")
            if not cond or not isinstance(cond, dict):
                continue
            # flag: {key, value}
            flag = cond.get("flag")
            if isinstance(flag, dict) and flag.get("key"):
                checked.add((flag["key"], flag.get("value")))
            # flag_not: [{key, value}, ...]
            flag_not = cond.get("flag_not")
            if isinstance(flag_not, list):
                for fn in flag_not:
                    if isinstance(fn, dict) and fn.get("key"):
                        # flag_not means "not this value" — still consumes the value
                        checked.add((fn["key"], fn.get("value")))
    return checked


def _find_dialog_effects(reg):
    """Build dict of key → set of values SET by dialog choice effects."""
    set_values = {}
    for d in reg.dialogs:
        nodes = d.get("nodes", {})
        if not isinstance(nodes, dict):
            continue
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            for choice in node.get("choices", []):
                for e in choice.get("effects", []):
                    if isinstance(e, dict) and e.get("type") == "flag":
                        key = e.get("key", "")
                        val = e.get("value")
                        if key:
                            set_values.setdefault(key, set()).add(val)
    return set_values


def test_arc03_identity_stance_all_values_consumed():
    """All 3 values of state_identity_stance (deny, accept_cautious, seek_truth)
    set by arc03 branch should be checked by at least one dialog condition.
    
    TDD Cycle 1: RED phase — should FAIL because deny and accept_cautious
    are never checked.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    set_vals = _find_dialog_effects(reg)
    checked = _find_dialog_conditions(reg)

    stance_values = set_vals.get("state_identity_stance", set())
    missing = []
    for val in stance_values:
        has_consumer = any(k == "state_identity_stance" and v == val for k, v in checked)
        if not has_consumer:
            missing.append(val)
    assert len(missing) == 0, (
        f"state_identity_stance values set but never checked: {missing}"
    )


def test_arc05_mountain_gate_all_flags_consumed():
    """Both mountain gate flags (flag_mountain_gate_changed, flag_mountain_gate_repeated)
    set by arc05 branch should be checked by at least one dialog condition.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    checked = _find_dialog_conditions(reg)

    expected_flags = {"flag_mountain_gate_changed", "flag_mountain_gate_repeated"}
    checked_keys = {k for k, v in checked}

    for flag in expected_flags:
        assert flag in checked_keys, (
            f"{flag} is set by arc05 branch but never checked by any dialog condition"
        )


def test_arc05_family_status_all_values_consumed():
    """All 4 character status flags (lin_yue, mei_ruo, shen_luo, gu_han)
    set by arc05 family branch should have both 'loyal' and 'separated'
    values checked by dialog conditions.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    checked = _find_dialog_conditions(reg)

    status_keys = {
        "state_lin_yue_status",
        "state_mei_ruo_status",
        "state_shen_luo_status",
        "state_gu_han_status",
    }

    for key in status_keys:
        values_checked = {v for k, v in checked if k == key}
        assert len(values_checked) > 0, (
            f"{key} is set by arc05 family branch but never checked"
        )
