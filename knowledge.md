# knowledge.md — Tian Xu: Second Life (天缘灵)

Xianxia cultivation RPG. Python 3.10+ **stdlib-only** engine (no third-party deps, no pip install). Web frontend renders from the same UI-agnostic engine dict. All UI text/comments in **Indonesian**; code identifiers are English.

## Key code

- `src/engine/` — Core engine; `GameSession` (session.py) is the orchestrator.
  - `session.py` — action dispatch, view(), save/load, dialog routing, hunt/search/shop/craft/meditate/mine; UX helpers `_locations_with_activity()`, travel suggestions
  - `quest.py` — DAG main quests + side quests, branch/convergence, timeout; `OBJECTIVE_HANDLERS` dispatch
  - `dialog.py` — conditional dialog trees, once-entries, eval_condition; `CONDITION_CHECKERS` dispatch
  - `battle.py` — turn-based combat, element advantage, status effects (`STATUS_KINDS`: dot/stun/debuff/hot/buff), companions, spar_team sequential `turn_queue`, element mastery XP (`MASTERY_XP_PER_USE`); `TECHNIQUE_KINDS`, `STATUS_KINDS` frozensets
  - `cultivation.py` — exp/level/breakthrough, dantian system, grounding
  - `effects.py` — effect handlers (flag, item, relation, reputation, technique, start_quest, npc_state, grant_companion, exp, unlock_realm_bonus, status_effect, dialog); `EFFECT_TYPES` set literal
  - `state.py` — GameState/PlayerState, `SCHEMA_VERSION = 9`; explicit migrations v0→v5 in `from_dict`, later fields backfill via `.get()` defaults; fatigue/rest, companions list, status_effects, element_mastery, passives
  - `memory.py` — memory unlock + reliability system
  - `morality.py` — morality adjustments (optional, dialog-gate only)
  - `events.py` — log append
  - `items.py` — `ITEM_TYPES` (consumable, weapon, key_item), `EQUIPMENT_SLOTS` (weapon)
- `src/loader.py` — `DataRegistry` loads JSON/CSV game data; exposes `.realms`, `.npcs`, `.quests`, `.dialogs`, `.items`, `.locations`, `.hunts`, `.mines`, `.recipes`, `.techniques`, `.enemies`, `.memories`, `.companions`, `.factions`, `.key_items`, `.npc_schedules`, `.passives`, `.fusions`, `.config`
- `src/validate.py` — Strict data contract validator; runs on every `DataRegistry()` load, collects all violations then throws; derives allowed types from dispatch tables
- `web/app.py` — stdlib `ThreadingHTTPServer` JSON API + static files; `context()` exposes character_status, factions, meta (title/subtitle/tagline/panel/avatar/audio)
- `web/static/app.js` — Vanilla JS frontend; applyMeta() for data-driven title/assets; avatar fallback (initials); faction panel; character status badges
- `web/static/index.html` + `style.css` — Layout + theme (ink-wash textures, Lucide icons)
- `tests/` — pytest suite (377 tests), fixtures in `tests/fixtures/minimal_data/`
- `data/` — **7 arc story data** (JSON/CSV): quests, dialogs, NPCs, locations, items (with description column), enemies, techniques, companions, recipes, factions, key_items, npc_schedules, passives, fusion_recipes
- `docs/` — Story Production Bible v1.0 (~20 docs incl. DESIGN_GAP_REPORT, ENDING_INTEGRATION + superpowers specs): narrative architecture, quest graphs, character arcs, memory system, dialogue system, ending matrix, consequence matrix, etc.

## Commands

```bash
python3 web/app.py            # Web server on http://127.0.0.1:8000 (port = argv[1])
pytest                        # Full suite (377 tests); single test: pytest tests/test_smoke.py -k <name>
pytest tests/test_smoke.py    # Smoke tests only
pytest tests/test_arc1_data.py  # Arc 1 playthrough tests
python3 -c "from src.loader import DataRegistry; DataRegistry('data')"  # Validate data/, no server needed
node --check web/static/app.js  # JS syntax check
```

No lint/typecheck configured — verification = pytest + `node --check`. `pyproject.toml` exists for build config; no `requirements.txt` — stdlib only, no pip install needed (`uv.lock` is a leftover tooling lock containing only the root package). `web/app.py` manually adds the project root to `sys.path`.

## Conventions & constraints

- **Dispatch tables everywhere** — `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`, `EFFECT_TYPES`, `TECHNIQUE_KINDS`, `STATUS_KINDS` are set literals (single source of truth for validator); `EFFECT_TYPES` includes `dialog`. New type = new dict key, no if/elif chains.
- **Data-driven** — quests/dialogs/NPCs/locations/items/enemies/hunts/mines/recipes/techniques/memories/companions/factions/key_items/npc_schedules/passives/fusions are JSON/CSV in `data/`. Adding content = adding files, zero code changes.
- **Engine is UI-agnostic** — `session.view()` returns a plain dict that web renders.
- **config.web** — data-driven title/subtitle/tagline/panel/audio/avatar (all with xianxia defaults)
- **Travel is gated** — `_allowed_connections()` filters location `connections` by `connection_gates` (`{target_loc: flag}` in locations.json) + state flags. Gate story flow there, not in code.
- **Session actions dispatch via dict** — handler map at top of `GameSession.handle_action()`: talk/move/hunt/mine/craft/fuse_technique/etc. New action = new key + `_method`.
- **Save system versioned** — `SCHEMA_VERSION = 9`. Explicit `v < N` migrations in `from_dict` cover v0→v5 (hunt zones, factions, memories, companions list, realm_id mapping, dantian, status_effects); later fields backfill via `.get()` defaults. Saves newer than engine raise `ValueError`. Path traversal protected.
- **branch_quest** — explicit quest ID stored in state when branch pending (hardened against backward-search fragility)
- **ITEM_TYPES** — `consumable`, `weapon`, `key_item` (from `items.py`). Validator enforces; unknown types rejected.
- Single-player: one active web session per process, mutex-protected. Web static served with `Cache-Control: no-cache`.
- **No walrus operator** (`:=`) in engine code — project convention is conservative Python style

## Dispatch table snapshots (source of truth)

```
EFFECT_TYPES = {morality, relation, reputation, flag, item, gold, technique,
                start_quest, npc_state, grant_companion, exp, unlock_realm_bonus,
                status_effect, dialog}

OBJECTIVE_HANDLERS = {talk, defeat, gather, reach, choose, spar, advance_time, rest}

TECHNIQUE_KINDS = {attack, defend, heal}

STATUS_KINDS = {dot, stun, debuff, hot, buff}

ITEM_TYPES = {consumable, weapon, key_item}
```

## GameState fields (key runtime state)

Player: name, hp, qi, realm, realm_level, gold, roots, academy, equipment, exp, dantian_exp, morality, techniques, technique_levels

Session: location, day, hour, current_quest, completed/failed_quests, active_side_quests, side_quest_cooldowns, inventory, flags, relations, memories, talked_npcs, log, last_safe_location, last_hunt_time, grounding_hours_today, exp_grind_today, daily_spar_counts, branch_pending/branch_quest, pending_dialog, pending_battle, companion/companions/active_companion, npc_states, factions, realms_unlocked, status_effects, meditate_week_count/start, pil_sukses/aman_active, fatigue_days, rested_today, element_mastery, passives

## Game systems

- **Companion system** — `data/companions.json` exists with per-pavilion companions. `max_companions: 3`. Companion stats computed from `companion_stats()` in battle.py.
- **Dantian / breakthrough** — `dantian_exp` fills toward `dantian_capacity` (from realm CSV). Breakthrough on full.
- **Fatigue/rest** — `fatigue_days` increments per in-game day without rest. Configurable penalties to max HP/Qi. Rest at `loc_protagonist_room`.
- **Meditation** — weekly limit (`meditate_weekly_limit: 3`). Pil Sukses (+30% success), Pil Aman (cancel debuff on failure).
- **Mines** — `world.mines[]` in config.json. Each zone has `pool` with item/chance/min/max.
- **Hunts** — multi-zone (`world.hunts[]`). Each zone has `pool` (enemies), `search_items` (item/chance/min/max), optional `mini_boss_chance`/`mini_boss`.
- **Enemy drops** — `enemies.csv` has `drop_item`, `drop_chance` columns.
- **Items** — `items.csv` has `exp_value` and `description` columns. 36 items including beast cores, cultivation pills, technique scrolls, reagents.
- **Key items with use_effects** — `data/key_items.json` items can have `consumed: true` + `use_effects[]` (e.g., technique scrolls grant techniques).
- **NPC state overrides** — `npc_state` effect can change NPC location at runtime. `npc_states` dict on GameState tracks overrides.
- **NPC schedules** — `data/npc_schedules.json` moves NPCs by time of day.
- **Spar debuffs/teams** — Quests can have `spar_debuff` (hp_mult, atk_mult, def_mult) and `allies` list for team battles (`context: spar_team`). spar_team uses sequential turns (`turn_queue`: player ↔ allies alternate vs foes; tested in `tests/test_spar_team_turns.py`).
- **NPC spar_require** — `spar_require: {"realm_min": "realm_xuanshi"}` gates spar access.
- **Elements** — logam, kayu, tanah, air, api. Advantage cycle: logam→kayu→tanah→air→api→logam.
- **Element mastery** — `element_mastery` dict on GameState (per 五行 element). Techniques used in battle grant mastery XP (`MASTERY_XP_PER_USE`); levels 0–3 feed combat bonuses.
- **Passives** — `data/passives.json`. Academy choice grants a passive when quest `source` matches (quest.py `_grant_passive`); `get_player_passives()` applies stat modifiers in battle.
- **Technique fusion** — `data/fusion_recipes.json` (registry `.fusions`). Session action `fuse_technique`: consumes source techniques at required level → grants result technique.
- **Item types** — consumable (use for HP/Qi/exp), weapon (equip for power), key_item (narrative, may have use_effects).
- **Item use_effects pattern** — Key items pakai `use_effects[]` generik. Consumable special-cased (pil_sukses, pil_aman) masih hardcoded di session.py `_use_item()`. Refactor ke use_effects saat ada consumable baru yang butuh custom effect.
- **UX suggestions** — When travel/hunt/search is blocked, session suggests reachable locations or activity zones via `_locations_with_activity()`.

## Story data (7 arcs)

- Arc I: New Life → Pavilion selection → Forest trial → Night incident
- Arc II: First Artifact → Team spar → Branch (Obey/Investigate/Confront)
- Arc III: Gate Opened → Branch (Seek Truth/Accept Narrative)
- Arc IV: False History → no branch quest
- Arc V: World Remembers → Branch (Mountain Gate + Family Crisis → 4 permanent statuses)
- Arc VI: Last Cycle → Final Choice (Preserve/Destroy/Transform/Sacrifice)
- Arc VII: Second Life → Ending (including Hidden Resolution)

## Gotchas

- Tests copy `tests/fixtures/minimal_data/` to `tmp_path` or use `build_data()` — never touch real `data/`/`saves/`. Monkeypatch `SAVES_DIR` when needed.
- `.gitignore` exists — `.venv/`, `.coverage`, `saves/`, `__pycache__/` are excluded but may show in `git status`.
- Stdlib only: verify a library is already used before adding any dependency.
- `data/` is NOT empty — 7 arcs of story data live there. Don't assume data files are missing.
- `_victory()` syncs HP/Qi BEFORE granting exp (bug fix for level-up heal being clobbered).
- `realm_level` clamped to `>=1` in max_hp/max_qi formulas — corrupt saves can't produce negative HP.
- Effects engine casts numeric values to `int()` — string values in JSON are coerced, not crashed.
- `max_hp()`/`max_qi()` fallback returns sane defaults (50/30), not current HP.
- Companion system is active — `data/companions.json` has per-pavilion companions. `max_companions: 3`.
- Old realm IDs (`realm_awal`, `realm_tengah`, `realm_atas`) are migrated to new names (`realm_chuji`, `realm_xuanshi`, `realm_dishi`) in save loader.

## Claude Audit Verified (2026-08-24)

10 files audited. 2 fixed, 1 documented, 7 skipped:
- **Fixed:** effects.py exp multiplier bypass, quest.py morality clamp bypass
- **Documented:** session.py `_use_item` hardcoded IDs (design debt)
- **Skipped:** false positives (battle.py status-kind, quest.py rewards, effects.py dialog field, events.py coercion, state.py log persist, __init__.py trivial)
