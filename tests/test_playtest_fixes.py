"""TDD kontrak pasif↔dialog & recipe items reachable — post-playtest fixes."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

# ── pasif↔dialog (BUG-001 fix) ──────────────────────────────────────
# Dialog wx2/jx2/yz2/lg2 menjanjikan pasif tertentu per pavilion.
# Test memverifikasi: config.academies[].passive = passives.json source = janji.
EXPECTED_PASSIVE_MAP = {
    "pavilion_wuxin":    "passive_flowing_qi",     # wx2: "Flowing Qi"
    "pavilion_jianxin":  "passive_sword_intent",    # jx2: "Sword Intent"
    "pavilion_yanzhi":   "passive_phoenix_blood",   # yz2: "Phoenix Blood"
    "pavilion_liuguang": "passive_earth_guardian",   # lg2: "Earth Guardian"
}


def _load_passives():
    return {p["id"]: p["source"] for p in json.load(open(DATA / "passives.json"))["passives"]}


def _load_config_academies():
    cfg = json.load(open(DATA / "config.json"))
    return {a["id"]: a.get("passive") for a in cfg.get("academies", [])}


def test_passive_source_matches_config():
    passives = _load_passives()
    academies = _load_config_academies()
    for acad_id, passive_id in EXPECTED_PASSIVE_MAP.items():
        source = passives.get(passive_id)
        assert source == acad_id, (
            f"{passive_id}.source={source}, expected {acad_id}"
        )
        assert academies.get(acad_id) == passive_id, (
            f"{acad_id}.passive={academies.get(acad_id)}, expected {passive_id}"
        )


# ── recipe items reachable (BUG-004 fix) ────────────────────────────
def _shop_items():
    npcs = json.load(open(DATA / "npcs.json"))["npcs"]
    items = set()
    for n in npcs:
        shop = n.get("shop") or {}
        for entry in shop.get("buy", []):
            items.add(entry["item"])
    return items


def _quest_granted_items():
    items = set()
    for qf in (DATA / "quests").glob("*.json"):
        quests = json.load(open(qf)).get("quests", [])
        for q in quests:
            oc = q.get("on_complete") or {}
            for eff in (oc.get("effects") or []):
                if eff.get("type") == "item":
                    items.add(eff.get("id") or eff.get("item"))
    return items


def _dialog_granted_items():
    items = set()
    for df in (DATA / "dialogs").glob("*.json"):
        dialogs = json.load(open(df)).get("dialogs", [])
        for d in dialogs:
            for node in (d.get("nodes") or {}).values():
                for eff in node.get("effects") or []:
                    if eff.get("type") == "item":
                        items.add(eff.get("id") or eff.get("item"))
    return items


def test_recipe_items_obtainable():
    recipes = json.load(open(DATA / "recipes.json"))["recipes"]
    shop = _shop_items()
    quest_items = _quest_granted_items()
    dialog_items = _dialog_granted_items()
    reachable = shop | quest_items | dialog_items
    for r in recipes:
        ri = r.get("recipe_item")
        if ri:
            assert ri in reachable, (
                f"recipe_item '{ri}' ({r['id']}) tidak reachable "
                f"via shop/quest/dialog"
            )


# ── meditation hint text (BUG-003 fix) ───────────────────────────────
def test_meditation_hint_accurate():
    """Hint tidak boleh bilang 'pertarungan' — exp hanya dari consumable."""
    session_src = (Path(__file__).resolve().parents[1] / "src"
                   / "engine" / "session.py").read_text()
    assert "pertarungan atau pil kultivasi" not in session_src


# ── auto-equip starter weapon (#3 fix) ───────────────────────────────
def test_starter_weapon_equipped():
    """Game baru harus langsung equip pedang_kayu."""
    from src.loader import DataRegistry
    from src.engine.session import GameSession
    reg = DataRegistry(str(DATA))
    s = GameSession.new(reg)
    # clear intro dialog
    while s.state.pending_dialog:
        s.apply_action({"type": "dialog_choice", "choice_index": -1})
    assert s.state.player.equipment["weapon"] == "pedang_kayu"
    assert s.state.inventory.get("pedang_kayu", 0) >= 1
