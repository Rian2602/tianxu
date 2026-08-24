"""Test character & faction web — verify that character stance and status
values are consumed by dialog conditions.

Phase 5: Character & Faction Web
- Character stances (gu_han, shen_luo, orthodox) should be consumed
- Character status='loyal' values should be evaluated for consumption
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
            flag = cond.get("flag")
            if isinstance(flag, dict) and flag.get("key"):
                checked.add((flag["key"], flag.get("value")))
            flag_not = cond.get("flag_not")
            if isinstance(flag_not, list):
                for fn in flag_not:
                    if isinstance(fn, dict) and fn.get("key"):
                        checked.add((fn["key"], fn.get("value")))
    return checked


def _find_dialog_effects(reg):
    """Build dict of key -> set of values SET by dialog choice effects."""
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


def test_gu_han_stance_all_values_consumed():
    """All 3 values of state_gu_han_stance (trust, sacrifice, preserve)
    set by dlg_gu_han_char_002 should be checked by at least one dialog
    condition — making the Gu Han character quest choice meaningful.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))
    set_vals = _find_dialog_effects(reg)
    checked = _find_dialog_conditions(reg)

    values = set_vals.get("state_gu_han_stance", set())
    missing = [v for v in values if ("state_gu_han_stance", v) not in checked]
    assert len(missing) == 0, (
        f"state_gu_han_stance values set but never checked: {missing}"
    )


def test_shen_luo_stance_all_values_consumed():
    """All 3 values of state_shen_luo_stance (reform, liberation, stay)
    set by dlg_shen_luo_char_002 should be checked by at least one dialog
    condition — making the Shen Luo character quest choice meaningful.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))
    set_vals = _find_dialog_effects(reg)
    checked = _find_dialog_conditions(reg)

    values = set_vals.get("state_shen_luo_stance", set())
    missing = [v for v in values if ("state_shen_luo_stance", v) not in checked]
    assert len(missing) == 0, (
        f"state_shen_luo_stance values set but never checked: {missing}"
    )


def test_orthodox_stance_all_values_consumed():
    """All 3 values of state_orthodox_stance (loyal, questioning, rebel)
    set by dlg_orthodox_faction_002 should be checked by at least one dialog
    condition — making the Orthodox faction quest choice meaningful.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))
    set_vals = _find_dialog_effects(reg)
    checked = _find_dialog_conditions(reg)

    values = set_vals.get("state_orthodox_stance", set())
    missing = [v for v in values if ("state_orthodox_stance", v) not in checked]
    assert len(missing) == 0, (
        f"state_orthodox_stance values set but never checked: {missing}"
    )


def test_arc07_d01_has_reactive_nodes_for_stances():
    """dlg_a07_d01 (Arc07 opening) should have conditional nodes that
    react to character stances, not just character statuses.

    This verifies that character quest 002 choices (stance) affect
    the ending narrative.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))
    d = reg.dialog_by_id.get("dlg_a07_d01")
    assert d is not None, "dlg_a07_d01 not found"

    # Collect all stance keys checked in node conditions
    stance_keys = {
        "state_gu_han_stance",
        "state_shen_luo_stance",
        "state_orthodox_stance",
    }
    found_stances = set()
    nodes = d.get("nodes", {})
    if isinstance(nodes, dict):
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            cond = node.get("condition")
            if cond and isinstance(cond, dict):
                flag = cond.get("flag", {})
                if isinstance(flag, dict) and flag.get("key") in stance_keys:
                    found_stances.add(flag["key"])

    missing = stance_keys - found_stances
    assert len(missing) == 0, (
        f"dlg_a07_d01 missing stance checks: {missing}"
    )
