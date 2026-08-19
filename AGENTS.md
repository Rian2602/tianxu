# AGENTS.md — Tian Xu: Second Life (天缘灵)

Xianxia cultivation RPG. Python 3.10+ stdlib-only engine, CLI + web frontend. All UI text and comments are in **Indonesian** (Bahasa Indonesia). Code identifiers are English.

## Commands

```bash
python3 src/cli.py            # CLI game
python3 src/cli.py -l save1   # CLI with save file
python3 web/app.py             # Web server on http://127.0.0.1:8000
pytest                         # Run tests (287 tests, ~3.7s, no plugins)
pytest tests/test_smoke.py     # Smoke tests only
node --check web/static/app.js # JS syntax check
```

`pyproject.toml` exists for build config; no `requirements.txt` — stdlib only, no pip install needed. Both `src/cli.py` and `web/app.py` manually add the project root to `sys.path`.

## Structure

- `src/engine/` — Core engine (battle, cultivation, dialog, quest, session, state, effects, morality, memory, events, items). `GameSession` is the orchestrator.
- `src/cli.py` — Terminal frontend
- `src/loader.py` — `DataRegistry` loads JSON/CSV from a data directory
- `src/validate.py` — Strict data contract validator (7 rules, fails fast with all violations)
- `web/app.py` — stdlib `ThreadingHTTPServer`, JSON API + static files
- `web/static/` — Vanilla JS/CSS/HTML (no framework, no build step) + assets (textures, fonts, icons, audio)
- `tests/` — pytest suite, fixtures in `tests/fixtures/minimal_data/`
- `docs/` — Story Production Bible v1.0 (15 docs, Indonesian)
- `data/` — 7 arc story data (JSON/CSV): quests, dialogs, NPCs, locations, items, enemies, techniques, etc.
- `saves/` — Save file directory

## Key patterns

- **Dispatch tables everywhere** — `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`. Adding a new type = add a dict key. No if/elif chains. `EFFECT_TYPES`, `TECHNIQUE_KINDS`, and `STATUS_KINDS` are frozensets (single source of truth for validator).
- **Engine is UI-agnostic** — `session.view()` returns a plain dict. Both CLI and web render from the same dict.
- **Data-driven** — Game content is JSON/CSV in `data/`. Adding quests/dialogs/NPCs = adding files. Zero code changes.
- **Validator runs at startup** — `validate.py` checks schema, duplicates, cross-references, unknown types, illegal `start_quest`, branching quests, timeouts. All violations collected before throwing.
- **Save system is versioned** — `SCHEMA_VERSION = 3` with forward migration. Path traversal protected.
- **No walrus operator** (`:=`) in engine code — project convention is conservative Python style.

## Testing

Tests copy `tests/fixtures/minimal_data/` to `tmp_path` — never touches real `data/` or `saves/`. Monkeypatch `SAVES_DIR` when needed. No test framework beyond pytest.

## Gotchas

- `.gitignore` exists — `.venv/`, `.coverage`, `saves/`, `__pycache__/` are excluded but may show in `git status`.
- Single-player only — one active web session per process, protected by mutex.
- Web static files served with `Cache-Control: no-cache`.
- `data/` is NOT empty — 7 arcs of story data live there. Don't assume data files are missing.
- Companion system is dormant (no companions.json in data) — optional feature, don't remove.
- `_victory()` syncs HP/Qi BEFORE granting exp (bug fix for level-up heal being clobbered).
- Effects engine casts numeric values to `int()` — string values in JSON are coerced, not crashed.
- `max_hp()`/`max_qi()` fallback returns sane defaults (50/30), not current HP.
- `realm_level` clamped to `>=1` in max_hp/max_qi formulas — corrupt saves can't produce negative HP.
- `knowledge.md` at repo root has deeper architecture context if needed.
