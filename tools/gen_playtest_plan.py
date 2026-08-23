"""Generator jalur playtest — DataRegistry-based, dual-mechanism branch detection.

Detects:
1. Quest multi-next branches (Arc 2/3/5)
2. Dialog nodes where ≥2 choices set same flag to different values (Arc 6/7)

Output: one JSON per path (baseline + branch variants).
"""
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loader import DataRegistry


def build_quest_order(reg):
    """BFS quest graph → order_of dict + children map."""
    start_qid = reg.config.get("starting", {}).get("current_quest")
    order_of = {}
    children = {}
    if not start_qid or start_qid not in reg.quest_by_id:
        return order_of, children, start_qid

    order_of[start_qid] = 0
    queue = deque([start_qid])
    while queue:
        qid = queue.popleft()
        q = reg.quest_by_id.get(qid)
        if not q:
            continue
        kids = []
        for nxt in q.get("next") or []:
            if not isinstance(nxt, dict):
                continue
            nid = nxt.get("quest")
            if not nid or nid not in reg.quest_by_id:
                continue
            kids.append((nid, nxt.get("option")))
            new_order = order_of[qid] + 1
            if nid not in order_of or new_order < order_of[nid]:
                order_of[nid] = new_order
                queue.append(nid)
        children[qid] = kids
    return order_of, children, start_qid


def find_quest_branches(children):
    """qid → [(child_qid, option_label)] for nodes with >1 next."""
    return {qid: kids for qid, kids in children.items() if len(kids) > 1}


def find_dialog_flag_branches(reg):
    """Scan all dialog nodes for choices setting same flag to ≥2 different values.

    Returns: list of {
        dialog_id, node_id, flag_key,
        values: [{value, label}],
    }
    """
    branches = []
    for d in reg.dialogs:
        did = d.get("id", "?")
        for nid, node in (d.get("nodes") or {}).items():
            if not isinstance(node, dict):
                continue
            flag_vals = {}  # flag_key → {value: label}
            for ch in node.get("choices", []) or []:
                for fx in ch.get("effects", []) or []:
                    if isinstance(fx, dict) and fx.get("type") == "flag" and fx.get("key"):
                        fk = fx["key"]
                        fv = fx.get("value")
                        if fk not in flag_vals:
                            flag_vals[fk] = {}
                        flag_vals[fk][fv] = ch.get("label", str(fv))
            for fk, vals in flag_vals.items():
                if len(vals) >= 2:
                    branches.append({
                        "dialog_id": did,
                        "node_id": nid,
                        "flag_key": fk,
                        "values": [{"value": v, "label": l} for v, l in vals.items()],
                    })
    return branches


def walk_baseline(children, start_qid):
    """Baseline: always pick first option at each branch."""
    path = []
    qid = start_qid
    visited = set()
    while qid and qid not in visited:
        visited.add(qid)
        path.append(qid)
        kids = children.get(qid, [])
        if not kids:
            break
        qid = kids[0][0]
    return path


def walk_with_override(children, start_qid, override_at, override_child):
    """Baseline except at one branch point."""
    path = []
    qid = start_qid
    visited = set()
    while qid and qid not in visited:
        visited.add(qid)
        path.append(qid)
        kids = children.get(qid, [])
        if not kids:
            break
        qid = override_child if qid == override_at else kids[0][0]
    return path


def quest_to_step(reg, qid):
    q = reg.quest_by_id[qid]
    obj = q.get("objective", {})
    return {
        "quest_id": qid,
        "title": q.get("title"),
        "action": obj.get("kind"),
        "npc": obj.get("npc"),
        "location": obj.get("location"),
        "item": obj.get("item"),
        "enemies": obj.get("enemies"),
        "hint": obj.get("hint"),
        "choose_options": (
            [o.get("value") for o in obj.get("options", [])]
            if obj.get("kind") == "choose" else None
        ),
        "expect_flags_after": sorted({
            eff["key"] for eff in (q.get("on_complete", {}).get("effects") or [])
            if eff.get("type") == "flag"
        }),
    }


def build_plan(name, quest_ids, reg, *, diverges_at=None, option=None, dialog_branch=None):
    steps = [quest_to_step(reg, qid) for qid in quest_ids]
    plan = {"name": name, "quest_ids": quest_ids, "steps": steps}
    if diverges_at:
        plan["diverges_at"] = diverges_at
        plan["option"] = option
    if dialog_branch:
        plan["dialog_branch"] = dialog_branch
    return plan


def generate(reg):
    """Generate all plans: baseline + quest branches + dialog-flag branches."""
    order_of, children, start_qid = build_quest_order(reg)
    if not start_qid:
        return []

    quest_branches = find_quest_branches(children)
    dialog_branches = find_dialog_flag_branches(reg)

    plans = []

    # Baseline
    baseline_ids = walk_baseline(children, start_qid)
    plans.append(build_plan("baseline", baseline_ids, reg))

    # Quest multi-next branches
    for branch_qid, kids in quest_branches.items():
        for child_qid, option_label in kids[1:]:
            name = f"quest_{branch_qid}_{option_label or child_qid}"
            ids = walk_with_override(children, start_qid, branch_qid, child_qid)
            plans.append(build_plan(name, ids, reg,
                                    diverges_at=branch_qid, option=option_label))

    # Dialog-flag branches: each value gets its own plan (baseline path + dialog step)
    for db in dialog_branches:
        for vi, val_info in enumerate(db["values"]):
            suffix = val_info["value"]
            name = f"dialog_{db['dialog_id']}_{db['flag_key']}_{suffix}"
            plans.append(build_plan(name, baseline_ids, reg,
                                    dialog_branch={
                                        "dialog_id": db["dialog_id"],
                                        "node_id": db["node_id"],
                                        "flag_key": db["flag_key"],
                                        "choose_value": val_info["value"],
                                        "choose_label": val_info["label"],
                                    }))

    return plans


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "test_plans"
    os.makedirs(out_dir, exist_ok=True)

    reg = DataRegistry(data_dir=data_dir)
    print(f"Data: {len(reg.quests)} quests, {len(reg.dialogs)} dialogs")

    plans = generate(reg)
    for plan in plans:
        path = os.path.join(out_dir, f"{plan['name']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"{len(plans)} plans → {out_dir}/")

    # Coverage report
    dialog_branches = find_dialog_flag_branches(reg)
    for db in dialog_branches:
        print(f"  dialog branch: {db['dialog_id']}.{db['node_id']} "
              f"flag={db['flag_key']} values={[v['value'] for v in db['values']]}")


if __name__ == "__main__":
    main()
