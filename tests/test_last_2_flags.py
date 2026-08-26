"""Test that the last 2 unused state flags are consumed by dialog nodes.

state_murid_status='registered' — set by quest_a01_c01_002 (Registrasi, Arc I)
state_reputation_academic=1 — set by quest_a02_c01_001 (Ujian Tengah, Arc II)

These are tutorial/early-game flags that should be acknowledged by NPCs
to close the last 2 gaps in quest-dialog connectivity.
"""
from __future__ import annotations

import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dialogs():
    """Load all dialog files and return flat list of (dialog_id, node_id, condition)."""
    results = []
    for f_path in glob.glob(str(ROOT / "data" / "dialogs" / "*.json")):
        with open(f_path) as fh:
            data = json.load(fh)
        dialogs = data.get("dialogs", [])
        if isinstance(dialogs, dict):
            dialogs = list(dialogs.values())
        for dlg in dialogs:
            if not isinstance(dlg, dict):
                continue
            did = dlg.get("id", "")
            for nid, node in dlg.get("nodes", {}).items():
                cond = node.get("condition", {})
                flag = cond.get("flag", {})
                key = flag.get("key", "")
                val = flag.get("value", "")
                results.append((did, nid, key, val))
    return results


def test_murid_status_consumed():
    """state_murid_status='registered' should be consumed by at least one dialog node."""
    nodes = _load_dialogs()
    consumers = [
        (did, nid) for did, nid, key, val in nodes
        if key == "state_murid_status" and val == "registered"
    ]
    assert len(consumers) >= 1, (
        f"state_murid_status='registered' not consumed by any dialog. "
        f"Expected >= 1 consumer, got 0"
    )


def test_reputation_academic_consumed():
    """state_reputation_academic=1 should be consumed by at least one dialog node."""
    nodes = _load_dialogs()
    consumers = [
        (did, nid) for did, nid, key, val in nodes
        if key == "state_reputation_academic"
    ]
    assert len(consumers) >= 1, (
        f"state_reputation_academic not consumed by any dialog. "
        f"Expected >= 1 consumer, got 0"
    )


def test_all_state_flags_consumed():
    """Every state_ flag set by quests should be consumed by at least one dialog node."""
    # Find all state_ flags set by quests
    set_flags = set()
    for f_path in glob.glob(str(ROOT / "data" / "quests" / "*.json")):
        with open(f_path) as fh:
            data = json.load(fh)
        quests = data if isinstance(data, list) else data.get("quests", [])
        if isinstance(quests, dict):
            quests = list(quests.values())
        for q in quests:
            if not isinstance(q, dict):
                continue
            for e in q.get("on_complete", {}).get("effects", []):
                if e.get("type") == "flag" and e.get("key", "").startswith("state_"):
                    set_flags.add(e["key"])

    # Find all state_ flags consumed by dialogs
    consumed_flags = set()
    for did, nid, key, val in _load_dialogs():
        if key.startswith("state_"):
            consumed_flags.add(key)

    # Check: every set flag should be consumed
    unconsumed = set_flags - consumed_flags
    assert not unconsumed, (
        f"state_ flags set by quests but not consumed by dialogs: {unconsumed}"
    )
