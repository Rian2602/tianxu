"""Test reactive dialogs for Arcs IV-VI — verify that NPC dialogs
react to player choices made during these arcs.

FIX 2: Add reactive dialogs for Arcs IV-VI.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_arc05_family_branch_has_reactive_dialog():
    """The Arc05 family branch (protect/destroy/truth/despair) should have
    at least one NPC that reacts to the outcome during Arc V itself,
    not just in Arc VII.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    # Check if any dialog in arc05 or arc_world_reactive checks family status
    family_flags = {
        "state_lin_yue_status",
        "state_mei_ruo_status",
        "state_shen_luo_status",
        "state_gu_han_status",
    }
    found = set()
    for d in reg.dialogs:
        # Only check Arc V and reactive dialogs
        did = d.get("id", "")
        if not (did.startswith("dlg_a05") or "reactive" in did):
            continue
        nodes = d.get("nodes", {})
        if not isinstance(nodes, dict):
            continue
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            cond = node.get("condition")
            if cond and isinstance(cond, dict):
                flag = cond.get("flag", {})
                if isinstance(flag, dict) and flag.get("key") in family_flags:
                    found.add((did, flag["key"]))

    assert len(found) >= 1, (
        f"Arc05 family branch has no reactive dialog during Arc V. "
        f"Found: {found}"
    )
