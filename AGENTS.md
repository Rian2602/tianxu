# AGENTS.md — Tian Xu: Second Life (天缘灵)

Xianxia cultivation RPG. Python 3.10+ stdlib-only engine, web frontend. All UI text and comments are in **Indonesian** (Bahasa Indonesia). Code identifiers are English.

## Commands

```bash
python3 web/app.py             # Web server on http://127.0.0.1:8000 (port = argv[1])
pytest                         # Full suite, seconds, no plugins; single test: pytest tests/test_smoke.py -k <name>
pytest tests/test_smoke.py     # Smoke tests only
python3 -c "from src.loader import DataRegistry; DataRegistry('data')"  # Validate data/, no server needed
node --check web/static/app.js # JS syntax check
```

No lint/typecheck configured — verification = pytest + `node --check`. `pyproject.toml` exists for build config; no `requirements.txt` — stdlib only, no pip install needed (`uv.lock` is a leftover tooling lock containing only the root package). `web/app.py` manually adds the project root to `sys.path`.

## Structure

- `src/engine/` — Core engine (battle, cultivation, dialog, quest, session, state, effects, morality, memory, events, items). `GameSession` is the orchestrator.
- `src/loader.py` — `DataRegistry` loads JSON/CSV from a data directory
- `src/validate.py` — Strict data contract validator, fails fast with all violations
- `web/app.py` — stdlib `ThreadingHTTPServer`, JSON API + static files
- `web/static/` — Vanilla JS/CSS/HTML (no framework, no build step) + assets (textures, fonts, icons, audio, NPC portraits)
- `tests/` — pytest suite, fixtures in `tests/fixtures/minimal_data/`
- `tools/` — Dev utilities: `audit_location_gates.py`, `gen_playtest_plan.py`, `run_playtest_plan.py`
- `docs/` — Story Production Bible v1.0 (~20 docs incl. DESIGN_GAP_REPORT, ENDING_INTEGRATION + superpowers specs, Indonesian)
- `data/` — 7 arc story data (JSON/CSV): quests, dialogs, NPCs, locations, items, enemies, techniques, companions, recipes, factions, key_items, npc_schedules, etc.
- `saves/` — Save file directory

## Key patterns

- **Dispatch tables everywhere** — `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`. Adding a new type = add a dict key. No if/elif chains. `EFFECT_TYPES`, `TECHNIQUE_KINDS`, and `STATUS_KINDS` are set literals (single source of truth for validator); `EFFECT_TYPES` includes `dialog`.
- **Engine is UI-agnostic** — `session.view()` returns a plain dict. Web renders from this data.
- **Data-driven** — Game content is JSON/CSV in `data/`. Adding quests/dialogs/NPCs = adding files. Zero code changes.
- **Validator runs on every `DataRegistry()` load** — `validate.py` runs per-area validators (config, quests, dialogs, npcs, locations, memories, companions, recipes, CSVs, key_items, passives, fusions, duplicates) checking schema, cross-references, unknown types, illegal `start_quest`, branching quests, timeouts. All violations collected before throwing.
- **Save system is versioned** — `SCHEMA_VERSION = 9`. Explicit `v < N` migrations in `from_dict` cover v0→v5 (hunt zones, factions, memories, companions list, realm_id mapping, dantian, status_effects); later fields backfill via `.get()` defaults. Saves newer than engine raise `ValueError`. Path traversal protected.
- **Travel is gated** — `_allowed_connections()` filters location `connections` by `connection_gates` (`{target_loc: flag}` in locations.json) + state flags. Gate story flow there, not in code.
- **Session actions dispatch via dict** — handler map at top of `GameSession.handle_action()` (session.py): talk/move/hunt/mine/craft/fuse_technique/etc. New action = new key + `_method`.
- **No walrus operator** (`:=`) in engine code — project convention is conservative Python style.

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

## Story data (7 arcs)

- Arc I: New Life → Pavilion selection → Forest trial → Night incident
- Arc II: First Artifact → Team spar → Branch (Obey/Investigate/Confront)
- Arc III: Gate Opened → Branch (Seek Truth/Accept Narrative)
- Arc IV: False History → no branch quest
- Arc V: World Remembers → Branch (Mountain Gate + Family Crisis → 4 permanent statuses)
- Arc VI: Last Cycle → Final Choice (Preserve/Destroy/Transform/Sacrifice)
- Arc VII: Second Life → Ending (including Hidden Resolution)

## Game systems

- **Dantian/breakthrough** — `dantian_exp` fills toward `dantian_capacity` (from realm CSV). Breakthrough on full. Replaces old exp-per-level formula.
- **Companion system** — `data/companions.json` with per-pavilion companions. Up to 3 owned, 1 active in battle. Stats from `companion_stats()` in battle.py.
- **Fatigue/rest** — `fatigue_days` increments per in-game day without rest. Penalties to max HP/Qi. Rest at `loc_protagonist_room`.
- **Meditation** — weekly limit (`meditate_weekly_limit: 3`). Pil Sukses (+30% success), Pil Aman (cancel debuff on failure).
- **Status effects** — `status_effects` list on GameState. Kinds (`STATUS_KINDS` in battle.py): `dot`, `stun`, `debuff`, `hot`, `buff`. Can apply `hp_mult`/`qi_mult` to max stats.
- **Spar debuffs/teams** — Quests can have `spar_debuff` (hp_mult, atk_mult, def_mult) and `allies` list for team battles (`context: spar_team`). spar_team uses sequential turns (`turn_queue`: player ↔ allies alternate vs foes; tested in `tests/test_spar_team_turns.py`).
- **Multi-zone hunts** — `world.hunts[]` in config.json. Each zone has `pool` (enemies), `search_items` (item/chance/min/max), optional `mini_boss`.
- **Mines** — `world.mines[]` in config.json. Each zone has `pool` with item/chance/min/max.
- **Crafting** — `data/recipes.json`. Actions: `mine`, `craft` added to session.
- **Element mastery** — `element_mastery` dict on GameState (per 五行 element). Techniques used in battle grant mastery XP (`MASTERY_XP_PER_USE` in battle.py); levels 0–3 feed combat bonuses.
- **Passives** — `data/passives.json`. Academy choice grants a passive when quest `source` matches (quest.py); `get_player_passives()` applies stat modifiers in battle.
- **Technique fusion** — `data/fusion_recipes.json`. Session action `fuse_technique`: consumes source techniques at required level → grants result technique.
- **Elements** — logam, kayu, tanah, air, api. Advantage cycle: logam→kayu→tanah→air→api→logam.
- **NPC avatars** — NPC portraits in `web/static/assets/img/`. Fallback to initials.

## Testing

Tests copy `tests/fixtures/minimal_data/` to `tmp_path` — never touches real `data/` or `saves/`. Monkeypatch `SAVES_DIR` when needed. No test framework beyond pytest. Root `conftest.py` excludes `.agents/`, `.opencode/`, `claude/` from collection.

## Playtest issues — resolved

All 7 playtest findings are implemented in code — search `Playtest #` comments before re-diagnosing: dantian-full meditasi gate, Xu Ming hint text, cinematic intro dialog (`dlg_intro_narrative`), pavilion companion/signature-skill dialogs, Formation Tua intro + urgency dialog, `connection_gates` travel gating, spar_team sequential `turn_queue` (+ `tests/test_spar_team_turns.py`).

## Gotchas

- `.gitignore` exists — `.venv/`, `.coverage`, `saves/`, `__pycache__/` are excluded but may show in `git status`.
- Single-player only — one active web session per process, protected by mutex.
- Web static files served with `Cache-Control: no-cache`.
- `data/` is NOT empty — 7 arcs of story data live there. Don't assume data files are missing.
- Companion system is active — `data/companions.json` has per-pavilion companions (Serigala, Bangau, Fenghuang, Ular Air). `max_companions: 3`.
- `_victory()` syncs HP/Qi BEFORE granting exp (bug fix for level-up heal being clobbered).
- Effects engine casts numeric values to `int()` — string values in JSON are coerced, not crashed.
- `max_hp()`/`max_qi()` fallback returns sane defaults (50/30), not current HP.
- `realm_level` clamped to `>=1` in max_hp/max_qi formulas — corrupt saves can't produce negative HP.
- `max_hp()`/`max_qi()` now apply status effect multipliers and fatigue penalties from config.
- `exp_next()` reads `dantian_capacity` from realm CSV, not config-level growth formula.
- Old realm IDs (`realm_awal`, `realm_tengah`, `realm_atas`) are migrated to new names (`realm_chuji`, `realm_xuanshi`, `realm_dishi`) in save loader.
- **Cross-file dependencies** — `quest_faction_reform_003` requires `flag_disturbance_investigated` from `quest_a02_c02_004` in `arc02.json`. If editing `arc_faction_reformists.json` in isolation, this dependency is invisible. Both flags must be set.
- `knowledge.md` at repo root has deeper architecture context and has been refreshed to match the code (schema v9, current STATUS_KINDS). Hard numbers in docs (test counts, etc.) can lag behind the code — trust the code first.
