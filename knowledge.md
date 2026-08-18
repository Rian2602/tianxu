# knowledge.md — Tian Xu: Second Life (天缘灵)

Xianxia cultivation RPG. Python 3.10+ **stdlib-only** engine (no third-party deps, no pip install). CLI + web frontend render from the same UI-agnostic engine dict. All UI text/comments in **Indonesian**; code identifiers are English.

## Key code

- `src/engine/` — Core engine; `GameSession` (session.py) is the orchestrator.
  - `session.py` — action dispatch, view(), save/load, dialog routing, hunt/search/shop/craft
  - `quest.py` — DAG main quests + side quests, branch/convergence, timeout
  - `dialog.py` — conditional dialog trees, once-entries, eval_condition
  - `battle.py` — turn-based combat, element advantage, status effects, companion
  - `cultivation.py` — exp/level/breakthrough, grounding
  - `effects.py` — effect handlers (flag, item, relation, reputation, technique, etc.)
  - `state.py` — GameState/PlayerState, save schema v2, migration
  - `memory.py` — memory unlock + reliability system
  - `morality.py` — morality adjustments (optional, dialog-gate only)
  - `events.py` — log append
  - `items.py` — key_item data
- `src/loader.py` — `DataRegistry` loads JSON/CSV game data; exposes `.realms`, `.npcs`, `.quests`, `.dialogs`, `.items`, `.locations`, `.hunts`, `.recipes`, `.techniques`, `.enemies`, `.memories`, `.companions`, `.factions`, `.config`
- `src/validate.py` — Strict data contract validator (7 rules, fails fast with all violations); derives allowed types from dispatch tables
- `src/cli.py` — Terminal frontend (data-driven header from `config.web`)
- `web/app.py` — stdlib `ThreadingHTTPServer` JSON API + static files; `context()` exposes character_status, factions, meta (title/subtitle/tagline/panel/avatar/audio)
- `web/static/app.js` — Vanilla JS frontend; applyMeta() for data-driven title/assets; avatar fallback (initials); faction panel; character status badges
- `web/static/index.html` + `style.css` — Layout + theme (ink-wash textures, Lucide icons)
- `tests/` — pytest suite (287 tests), fixtures in `tests/fixtures/minimal_data/`
- `data/` — **7 arc story data** (JSON/CSV): quests, dialogs, NPCs, locations, items, etc.
- `docs/` — Story Production Bible v1.0 (15 docs): narrative architecture, quest graphs, character arcs, memory system, dialogue system, etc.

## Commands

```bash
python3 src/cli.py            # CLI game
python3 src/cli.py -l save1   # CLI with a save file
python3 web/app.py            # Web server on http://127.0.0.1:8000
pytest                        # Run full test suite (287 tests, ~3.7s)
pytest tests/test_smoke.py    # Smoke tests only
pytest tests/test_arc1_data.py  # Arc 1 playthrough tests
node --check web/static/app.js  # JS syntax check
```

No package/build tooling: no `pyproject.toml`, `requirements.txt`, or build config.

## Conventions & constraints

- **Dispatch tables everywhere** — `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`. New type = new dict key, no if/elif chains. `EFFECT_TYPES`, `TECHNIQUE_KINDS`, and `STATUS_KINDS` are frozensets (single source of truth for validator).
- **Data-driven** — quests/dialogs/NPCs/locations/items/enemies/hunts/recipes/techniques/memories/companions/factions are JSON/CSV in `data/`. Adding content = adding files, zero code changes.
- **Engine is UI-agnostic** — `session.view()` returns a plain dict that both CLI and web render.
- **config.web** — data-driven title/subtitle/tagline/panel/audio/avatar (all with xianxia defaults)
- **Save system versioned** — `SCHEMA_VERSION` with forward migration; path traversal protected.
- **branch_quest** — explicit quest ID stored in state when branch pending (hardened against backward-search fragility)
- Single-player: one active web session per process, mutex-protected. Web static served with `Cache-Control: no-cache`.
- **No walrus operator** (`:=`) in engine code — project convention is conservative Python style

## Story data (7 arcs)

- Arc I: New Life → Pavilion selection
- Arc II: First Artifact → Branch (Obey/Investigate/Confront)
- Arc III: Gate Opened → Branch (Seek Truth/Accept Narrative)
- Arc IV: False History → no branch quest
- Arc V: World Remembers → Branch (Mountain Gate + Family Crisis → 4 permanent statuses)
- Arc VI: Last Cycle → Final Choice (Preserve/Destroy/Transform/Sacrifice)
- Arc VII: Second Life → Ending (including Hidden Resolution)

## Gotchas

- Tests copy `tests/fixtures/minimal_data/` to `tmp_path` or use `build_data()` — never touch real `data/`/`saves/`.
- No `.gitignore` — `.venv/`, `.coverage`, `saves/`, `__pycache__/` may show in `git status`.
- Stdlib only: verify a library is already used before adding any dependency.
- Companion system is dormant (no companions.json in data) — optional feature, don't remove.
- `_victory()` syncs HP/Qi BEFORE granting exp (bug fix for level-up heal being clobbered)

## Claude version note (2026-08-18)

A `claude/` directory with older versions of key files existed for comparison. Repo was found to be **more advanced** — 11 additional hardening fixes, dead code cleanup, and a fuller test suite (287 tests). No adaptations needed from Claude files; directory deleted (Task 1). See `.superpowers/sdd/2026-08-18-adapt-claude-best-parts/` for full diff details.
