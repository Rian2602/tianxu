"""TDD test for playtest plan BFS — connection_gates handling.

Bug: build_graph() ignores connection_gates → BFS finds paths through
gated connections → move fails at runtime.
Fix: Include gates in graph, skip gated connections without required flags.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures" / "minimal_data"


def _copy(tmp_path: Path) -> Path:
    dst = tmp_path / "gated_data"
    shutil.copytree(FIX, dst)
    return dst


def test_build_graph_includes_gates(tmp_path):
    """build_graph must return gate information alongside connections."""
    from tools.run_playtest_plan import build_graph

    dst = _copy(tmp_path)
    locs = json.loads((dst / "locations.json").read_text(encoding="utf-8"))
    # Add connection_gates to loc_gerbang
    for loc in locs["locations"]:
        if loc["id"] == "loc_gerbang":
            loc["connection_gates"] = {"loc_hutan": "flag_forest_open"}
    (dst / "locations.json").write_text(
        json.dumps(locs, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    result = build_graph(dst)
    # build_graph should return (graph, gates) tuple
    assert isinstance(result, tuple), f"build_graph should return tuple, got {type(result)}"
    graph, gates = result
    assert "loc_gerbang" in graph
    assert "loc_gerbang" in gates
    assert gates["loc_gerbang"].get("loc_hutan") == "flag_forest_open"


def test_bfs_skips_gated_connections(tmp_path):
    """BFS should not traverse gated connections without required flags."""
    from tools.run_playtest_plan import build_graph, bfs_path

    dst = _copy(tmp_path)
    locs = json.loads((dst / "locations.json").read_text(encoding="utf-8"))
    # Gate: loc_gerbang → loc_hutan requires flag_forest_open
    for loc in locs["locations"]:
        if loc["id"] == "loc_gerbang":
            loc["connection_gates"] = {"loc_hutan": "flag_forest_open"}
    (dst / "locations.json").write_text(
        json.dumps(locs, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    graph, gates = build_graph(dst)
    # Without flags, BFS should NOT find path to loc_hutan through gated connection
    path = bfs_path(graph, "loc_gerbang", "loc_hutan", gates, set())
    assert path is None, f"Gated path should be unreachable without flags: {path}"


def test_bfs_traverses_gated_connections_with_flags(tmp_path):
    """BFS should traverse gated connections when flags are present."""
    from tools.run_playtest_plan import build_graph, bfs_path

    dst = _copy(tmp_path)
    locs = json.loads((dst / "locations.json").read_text(encoding="utf-8"))
    # Gate: loc_gerbang → loc_hutan requires flag_forest_open
    for loc in locs["locations"]:
        if loc["id"] == "loc_gerbang":
            loc["connection_gates"] = {"loc_hutan": "flag_forest_open"}
    (dst / "locations.json").write_text(
        json.dumps(locs, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    graph, gates = build_graph(dst)
    # With flags, BFS should find path
    path = bfs_path(graph, "loc_gerbang", "loc_hutan", gates, {"flag_forest_open"})
    assert path is not None, "BFS should find path when flags are present"
    assert "loc_hutan" in path


def test_bfs_ignores_nonexistent_gate(tmp_path):
    """BFS should traverse connections that have no gate defined."""
    from tools.run_playtest_plan import build_graph, bfs_path

    dst = _copy(tmp_path)
    graph, gates = build_graph(dst)
    # loc_gerbang has no gates → should work normally
    path = bfs_path(graph, "loc_gerbang", "loc_hutan", gates, set())
    assert path is not None, "Ungated connection should be traversable"
