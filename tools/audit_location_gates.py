"""Audit reachability lokasi vs urutan main-quest chain (Tian Xu: Second Life).

Mendeteksi lokasi yang bisa dicapai pemain jauh lebih awal dari seharusnya
(kebocoran konten/plot) — kelas bug rantai Arsip Publik → Bawah Terdalam.

Dua pintu:
    from tools.audit_location_gates import audit
    audit()                       # -> list pesan masalah (kosong = aman)
    python3 tools/audit_location_gates.py [path_data]

Perbedaan dari heuristik serupa: sumber flag bukan cuma on_complete quest,
tapi juga efek pilihan dialog yang diatribusikan ke step quest-main yang
meroutenya. Dialog tanpa atribusi main-chain dan seluruh quest samping
sengaja diabaikan — arah error false-negative yang aman.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.loader import DataRegistry


def _chain_order(reg: DataRegistry) -> dict[str, int]:
    """Urutan step quest utama: BFS min-step mengikuti field `next`."""
    start = (reg.config.get("starting") or {}).get("current_quest")
    if not start or start not in reg.quest_by_id:
        return {}
    order = {start: 0}
    queue = deque([start])
    while queue:
        qid = queue.popleft()
        for nxt in reg.quest_by_id[qid].get("next") or []:
            nid = nxt.get("quest") if isinstance(nxt, dict) else None
            if nid in reg.quest_by_id and (nid not in order or order[qid] + 1 < order[nid]):
                order[nid] = order[qid] + 1
                queue.append(nid)
    return order


def _dialog_flag_steps(reg: DataRegistry, order: dict[str, int]) -> dict[str, int]:
    """dialog_id (punya flag) -> step paling awal tersedia via route main-chain."""
    steps: dict[str, int] = {}

    def consider(dlg_id, step):
        if dlg_id in reg.dialog_by_id:
            steps[dlg_id] = min(steps.get(dlg_id, 10**9), step)

    for npc in reg.npcs:
        routes = npc.get("dialog_routes") or {}
        for qid, dlg_id in (routes.get("main") or {}).items():
            if qid in order:
                consider(dlg_id, order[qid])
    for quest in reg.quests:
        if quest.get("id") not in order:
            continue
        for phase in ("on_start", "on_complete"):
            effects = ((quest.get(phase) or {}).get("effects")) or []
            for eff in effects:
                if eff.get("type") == "dialog":
                    consider(eff.get("id"), order[quest["id"]])
    return steps


def audit_rows(data_root: str = "data", gap_threshold: int = 2) -> list[dict]:
    """Baris temuan terstruktur: loc_id/name/actual/need/gap."""
    reg = DataRegistry(data_dir=data_root)
    order = _chain_order(reg)
    if not order:
        return ["[WARN] chain main-quest tak bisa dibangun dari config"]
    max_step = max(order.values())

    # flag dialog: key yang bisa di-set pilihan maupun efek level-node
    dlg_flags: dict[str, set] = {}
    for did, dlg in reg.dialog_by_id.items():
        keys = {
            eff.get("key")
            for node in (dlg.get("nodes") or {}).values()
            for eff in node.get("effects") or []
            if eff.get("type") == "flag"
        } | {
            eff.get("key")
            for node in (dlg.get("nodes") or {}).values()
            for choice in node.get("choices") or []
            for eff in choice.get("effects") or []
            if eff.get("type") == "flag"
        }
        if keys:
            dlg_flags[did] = keys

    # flag kumulatif per step
    acc: set = set()
    cumulative: list[set] = []
    dlg_step_map = _dialog_flag_steps(reg, order)
    for step in range(max_step + 1):
        for qid, o in order.items():
            if o == step:
                acc |= {
                    e.get("key")
                    for e in ((reg.quest_by_id[qid].get("on_complete") or {}).get("effects")) or []
                    if e.get("type") == "flag"
                }
        for did, stp in dlg_step_map.items():
            if stp == step:
                acc |= dlg_flags.get(did, set())
        cumulative.append(set(acc))

    edges = [
        (loc["id"], conn, (loc.get("connection_gates") or {}).get(conn))
        for loc in reg.locations
        for conn in loc.get("connections", [])
    ]
    start_loc = (reg.config.get("starting") or {}).get("location")

    first_reachable: dict[str, int] = {}
    for step in range(max_step + 1):
        seen = {start_loc}
        frontier = [start_loc]
        while frontier:
            nxt = []
            for node in frontier:
                for a, b, gate in edges:
                    if a == node and b not in seen and (gate is None or gate in cumulative[step]):
                        seen.add(b)
                        nxt.append(b)
            frontier = nxt
        for loc_id in seen:
            first_reachable.setdefault(loc_id, step)

    intended: dict[str, int] = {}

    def consider(loc_id, step):
        if loc_id and (loc_id not in intended or step < intended[loc_id]):
            intended[loc_id] = step

    for qid, step in order.items():
        obj = reg.quest_by_id[qid].get("objective") or {}
        consider(obj.get("location"), step)
        npc = reg.npc_by_id.get(obj.get("npc"))
        if npc:
            consider(npc.get("location"), step)

    rows = []
    for loc_id, actual in sorted(first_reachable.items(), key=lambda kv: kv[1]):
        need = intended.get(loc_id)
        if need is not None and need - actual >= gap_threshold:
            rows.append({
                "loc_id": loc_id,
                "name": reg.location_by_id.get(loc_id, {}).get("name", loc_id),
                "actual": actual,
                "need": need,
                "gap": need - actual,
            })
    return rows


def audit(data_root: str = "data", gap_threshold: int = 2) -> list[str]:
    return [
        f"[BOCOR] '{r['name']}' ({r['loc_id']}) reachable sejak step #{r['actual']}, "
        f"dibutuhkan cerita di step #{r['need']} (selisih {r['gap']})."
        for r in audit_rows(data_root, gap_threshold)
    ]


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "data"
    findings = audit(root)
    if findings:
        print(f"{len(findings)} lokasi berpotensi bocor:")
        for msg in findings:
            print("-", msg)
        sys.exit(1)
    print("OK — tidak ada lokasi yang reachable prematur.")