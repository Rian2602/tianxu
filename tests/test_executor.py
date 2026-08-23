"""Test for playtest executor — TDD: test first, implement later."""
import pytest
import subprocess
import time
import urllib.request
import json
import signal
import os


@pytest.fixture(scope="module")
def server():
    """Start game server, yield, then kill."""
    proc = subprocess.Popen(
        ["python3", "web/app.py", "8099"],
        cwd="/home/dienk/tian-xu-second-life",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    yield proc
    proc.terminate()
    proc.wait(timeout=5)


class API:
    def __init__(self, base):
        self.base = base

    def get(self, path):
        req = urllib.request.Request(f"{self.base}{path}")
        return json.loads(urllib.request.urlopen(req, timeout=15).read())

    def post(self, path, data):
        # Wrap in {"action": {...}} for /api/action endpoint
        if path == "/action":
            data = {"action": data}
        d = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{self.base}{path}", d, headers={"Content-Type": "application/json"}
        )
        return json.loads(urllib.request.urlopen(req, timeout=15).read())


@pytest.fixture
def api():
    """API helper."""
    return API("http://127.0.0.1:8099/api")


def test_arc1_no_stuck_quests(server, api):
    """Executor completes all Arc I quests without getting stuck.

    This is the core acceptance test: if any quest doesn't advance,
    the executor is broken.
    """
    # New game
    api.post("/new", {"save_name": "test_arc1"})
    _drain_intro(api)

    stuck = _execute_chain(api)

    assert stuck == [], f"Quests stuck: {stuck}"
    state = api.get("/state")
    assert state["view"]["current_quest"]["id"] == "quest_a02_c01_001"


def test_arc1_final_state(server, api):
    """After Arc I, verify final state is correct."""
    api.post("/new", {"save_name": "test_arc1_state"})
    _drain_intro(api)

    stuck = _execute_chain(api)
    assert stuck == [], f"Quests stuck: {stuck}"

    state = api.get("/state")
    view = state["view"]
    player = view["player"]

    assert player["hp"] == 50
    assert player["qi"] == 30
    assert player["gold"] == 30
    assert player["academy"] == "pavilion_wuxin"
    assert view["current_quest"]["id"] == "quest_a02_c01_001"


def test_dialog_intro_plays_on_new_game(server, api):
    """New game starts with dialog intro, not explore mode."""
    api.post("/new", {"save_name": "test_intro"})

    state = api.get("/state")
    view = state["view"]

    assert view["mode"] == "dialog"
    assert view["dialog"] is not None
    assert "narration" in (view["dialog"].get("speaker") or "")


# ── Helpers ──────────────────────────────────────────────────────────────

NPC_DEFAULTS = {
    "npc_aptitude_examiner": "loc_tianxu_gate",
    "npc_proctor": "loc_training_hall",
    "npc_lin_yue": "loc_training_hall",
    "npc_shen_luo": "loc_training_hall",
    "npc_gu_han": "loc_training_hall",
}

CONNS = {
    "loc_protagonist_room": ["loc_training_hall"],
    "loc_training_hall": ["loc_tianxu_gate", "loc_pavilion_wuxin", "loc_pavilion_jianxin",
                          "loc_pavilion_yanzhi", "loc_pavilion_liuguang", "loc_protagonist_room",
                          "loc_outer_region", "loc_mo_chen_meeting", "loc_archive_public",
                          "loc_grandmaster_chamber", "loc_mentor_ground"],
    "loc_tianxu_gate": ["loc_tianxu_approach_road", "loc_training_hall"],
    "loc_outer_region": ["loc_training_hall", "loc_hutan_akademi", "loc_hidden_cave",
                         "loc_affected_village", "loc_mountain_gate"],
    "loc_hutan_akademi": ["loc_outer_region"],
}


def _bfs(start, goal):
    from collections import deque
    if start == goal:
        return []
    q = deque([(start, [start])])
    vis = {start}
    while q:
        n, p = q.popleft()
        for c in CONNS.get(n, []):
            if c == goal:
                return p[1:] + [c]
            if c not in vis:
                vis.add(c)
                q.append((c, p + [c]))
    return None


def _drain(api, max_iter=100):
    for _ in range(max_iter):
        state = api.get("/state")
        mode = state["view"]["mode"]
        if mode not in ("dialog", "battle"):
            return
        if mode == "dialog":
            api.post("/action", {"type": "dialog_choice", "choice_index": -1})
        elif mode == "battle":
            api.post("/action", {"type": "battle_action", "action": "attack"})


def _navigate_to(api, target):
    state = api.get("/state")
    cur = state["view"]["location"]["id"]
    if cur == target:
        return
    path = _bfs(cur, target)
    if path is None:
        return
    for loc in path:
        api.post("/action", {"type": "move", "to": loc})
        _drain(api)


def _navigate_to_npc(api, npc_id):
    state = api.get("/state")
    cur = state["view"]["location"]["id"]
    # Check if NPC is at current location
    ctx_npcs = {n["id"] for n in state["context"]["npcs"]}
    if npc_id in ctx_npcs:
        return
    # Navigate to default location
    default = NPC_DEFAULTS.get(npc_id, "loc_training_hall")
    _navigate_to(api, default)


def _drain_intro(api):
    for _ in range(20):
        state = api.get("/state")
        if state["view"]["mode"] == "dialog":
            api.post("/action", {"type": "dialog_choice", "choice_index": -1})
        else:
            break


def _execute_chain(api):
    """Run full Arc I chain; return list of quests that failed to advance."""
    CHAIN = [
        ("quest_a01_c01_001", "talk", "npc_aptitude_examiner"),
        ("quest_a01_c01_002", "talk", "npc_aptitude_examiner"),
        ("quest_a01_c02_003", "talk", "npc_proctor"),
        ("quest_a01_c02_003b", "talk", "npc_lin_yue"),
        ("quest_a01_c02_003c", "talk", "npc_shen_luo"),
        ("quest_a01_c02_003d", "talk", "npc_gu_han"),
        ("quest_a01_c02_003e", "talk", "npc_proctor"),
        ("quest_a01_c04_005a", "move", "loc_outer_region"),
        ("quest_a01_c04_005b", "talk", "npc_lin_yue"),
        ("quest_a01_c04_005c", "hunt", "loc_hutan_akademi"),
        ("quest_a01_c04_005d", "move", "loc_outer_region"),
        ("quest_a01_c04_006", "rest", "loc_protagonist_room"),
    ]

    stuck = []

    for expected_quest, action_type, target in CHAIN:
        state = api.get("/state")
        view = state["view"]
        qid = view.get("current_quest", {}).get("id", "NONE")

        # Handle choose mode (pavilion selection after 003e)
        if view["mode"] == "choose":
            api.post("/action", {"type": "choose", "option": "pavilion_wuxin"})
            _drain(api)
            state = api.get("/state")
            qid = state["view"].get("current_quest", {}).get("id", "NONE")

        if qid != expected_quest:
            continue

        if action_type == "talk":
            _navigate_to_npc(api, target)
            api.post("/action", {"type": "talk", "npc": target})
            _drain(api)
        elif action_type == "move":
            _navigate_to(api, target)
        elif action_type == "hunt":
            _navigate_to(api, target)
            # Retry: mini_boss_chance (~10%) spawns a foe that doesn't count
            # toward defeat objectives, and respawn cooldown can block a
            # second hunt — advance time and retry until quest moves on.
            for _attempt in range(8):
                api.post("/action", {"type": "hunt"})
                _drain(api)
                state = api.get("/state")
                if state["view"].get("current_quest", {}).get("id") != expected_quest:
                    break
                api.post("/action", {"type": "advance_time", "hours": 24})
        elif action_type == "rest":
            _navigate_to(api, target)
            api.post("/action", {"type": "rest"})
            _drain(api)

        state = api.get("/state")
        new_qid = state["view"].get("current_quest", {}).get("id", "NONE")
        if new_qid == expected_quest:
            stuck.append(expected_quest)

    return stuck
