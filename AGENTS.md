# AGENTS.md — Tian Xu: Second Life (天缘灵)

Xianxia cultivation RPG. Python 3.10+ stdlib-only engine, web frontend. All UI text and comments are in **Indonesian** (Bahasa Indonesia). Code identifiers are English.

## Commands

```bash
python3 web/app.py             # Web server on http://127.0.0.1:8000
pytest                         # Run tests (287 tests, ~3.7s, no plugins)
pytest tests/test_smoke.py     # Smoke tests only
node --check web/static/app.js # JS syntax check
```

`pyproject.toml` exists for build config; no `requirements.txt` — stdlib only, no pip install needed. `web/app.py` manually adds the project root to `sys.path`.

## Structure

- `src/engine/` — Core engine (battle, cultivation, dialog, quest, session, state, effects, morality, memory, events, items). `GameSession` is the orchestrator.
- `src/loader.py` — `DataRegistry` loads JSON/CSV from a data directory
- `src/validate.py` — Strict data contract validator (7 rules, fails fast with all violations)
- `web/app.py` — stdlib `ThreadingHTTPServer`, JSON API + static files
- `web/static/` — Vanilla JS/CSS/HTML (no framework, no build step) + assets (textures, fonts, icons, audio, NPC portraits)
- `tests/` — pytest suite, fixtures in `tests/fixtures/minimal_data/`
- `docs/` — Story Production Bible v1.0 (19 docs + superpowers specs, Indonesian)
- `data/` — 7 arc story data (JSON/CSV): quests, dialogs, NPCs, locations, items, enemies, techniques, companions, recipes, factions, key_items, npc_schedules, etc.
- `saves/` — Save file directory

## Key patterns

- **Dispatch tables everywhere** — `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`. Adding a new type = add a dict key. No if/elif chains. `EFFECT_TYPES`, `TECHNIQUE_KINDS`, and `STATUS_KINDS` are frozensets (single source of truth for validator).
- **Engine is UI-agnostic** — `session.view()` returns a plain dict. Web renders from this data.
- **Data-driven** — Game content is JSON/CSV in `data/`. Adding quests/dialogs/NPCs = adding files. Zero code changes.
- **Validator runs at startup** — `validate.py` checks schema, duplicates, cross-references, unknown types, illegal `start_quest`, branching quests, timeouts. All violations collected before throwing.
- **Save system is versioned** — `SCHEMA_VERSION = 7` with forward migration (v0→v7: hunt zones, factions, memories, companions, realm_id mapping, dantian, status_effects, fatigue). Path traversal protected.
- **No walrus operator** (`:=`) in engine code — project convention is conservative Python style.

## Game systems

- **Dantian/breakthrough** — `dantian_exp` fills toward `dantian_capacity` (from realm CSV). Breakthrough on full. Replaces old exp-per-level formula.
- **Companion system** — `data/companions.json` with per-pavilion companions. Up to 3 owned, 1 active in battle. Stats from `companion_stats()` in battle.py.
- **Fatigue/rest** — `fatigue_days` increments per in-game day without rest. Penalties to max HP/Qi. Rest at `loc_protagonist_room`.
- **Meditation** — weekly limit (`meditate_weekly_limit: 3`). Pil Sukses (+30% success), Pil Aman (cancel debuff on failure).
- **Status effects** — `status_effects` list on GameState. Types: `dot`, `stun`. Can apply `hp_mult`/`qi_mult` to max stats.
- **Spar debuffs/teams** — Quests can have `spar_debuff` (hp_mult, atk_mult, def_mult) and `allies` list for team battles (`context: spar_team`).
- **Multi-zone hunts** — `world.hunts[]` in config.json. Each zone has `pool` (enemies), `search_items` (item/chance/min/max), optional `mini_boss`.
- **Mines** — `world.mines[]` in config.json. Each zone has `pool` with item/chance/min/max.
- **Crafting** — `data/recipes.json`. Actions: `mine`, `craft` added to session.
- **NPC avatars** — NPC portraits in `web/static/assets/img/`. Fallback to initials.

## Testing

Tests copy `tests/fixtures/minimal_data/` to `tmp_path` — never touches real `data/` or `saves/`. Monkeypatch `SAVES_DIR` when needed. No test framework beyond pytest.

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
- `knowledge.md` at repo root has deeper architecture context if needed.
