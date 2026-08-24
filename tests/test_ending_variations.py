"""Test ending variations — verify that ending text varies based on
character states (stances and statuses).

Phase 7: Ending Variations
- Ending nodes should have conditional text based on character states
- Each ending should acknowledge the player's relationships
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _get_ending_nodes(reg):
    """Get the 5 ending nodes from dlg_a07_d03."""
    for d in reg.dialogs:
        if d.get("id") == "dlg_a07_d03":
            nodes = d.get("nodes", {})
            return {
                "preserve": nodes.get("n_ep_preserve", {}),
                "destroy": nodes.get("n_ep_destroy", {}),
                "transform": nodes.get("n_ep_transform", {}),
                "sacrifice": nodes.get("n_ep_sacrifice", {}),
                "second_life": nodes.get("n_ep_second_life", {}),
            }
    return {}


def test_ending_nodes_have_conditions():
    """At least some ending nodes should have conditional text based on
    character states (stances or statuses).

    TDD Cycle 1: RED phase — should FAIL because current ending nodes
    have no conditions.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))
    endings = _get_ending_nodes(reg)

    # Check if any ending node has conditional variants
    # (nodes with conditions that lead to the same ending)
    ending_keys = set(endings.keys())
    conditional_endings = set()

    for d in reg.dialogs:
        if d.get("id") == "dlg_a07_d03":
            nodes = d.get("nodes", {})
            for nid, node in nodes.items():
                if not isinstance(node, dict):
                    continue
                cond = node.get("condition")
                if not cond:
                    continue
                # Check if this node leads to an ending
                for choice in node.get("choices", []):
                    next_node = choice.get("next", "")
                    if next_node and next_node.startswith("n_ep_"):
                        ending_name = next_node.replace("n_ep_", "")
                        conditional_endings.add(ending_name)

    # At least 2 endings should have conditional variants
    assert len(conditional_endings) >= 2, (
        f"Only {len(conditional_endings)} endings have conditional variants "
        f"(need >= 2). Found: {sorted(conditional_endings)}"
    )


def test_ending_preserve_varies_by_gu_han_stance():
    """The Preserve ending should have different text based on Gu Han's
    stance (trust, sacrifice, preserve).

    TDD Cycle 1: RED phase — should FAIL because Preserve ending has
    no conditional variants.
    """
    from src.loader import DataRegistry

    reg = DataRegistry(str(ROOT / "data"))

    # Find all nodes that lead to n_ep_preserve
    preserve_sources = []
    for d in reg.dialogs:
        if d.get("id") == "dlg_a07_d03":
            nodes = d.get("nodes", {})
            for nid, node in nodes.items():
                if not isinstance(node, dict):
                    continue
                for choice in node.get("choices", []):
                    if choice.get("next") == "n_ep_preserve":
                        cond = node.get("condition", {})
                        preserve_sources.append((nid, cond))

    # Should have at least 2 sources (default + conditional)
    assert len(preserve_sources) >= 2, (
        f"Preserve ending has only {len(preserve_sources)} source(s), "
        f"need >= 2 for variation. Found: {preserve_sources}"
    )
