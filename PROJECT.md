# Project: Tian Xu: Second Life — Fase 1 (Arc Akademi)

## Architecture
- **Language & Runtime**: Python 3.12, stdlib-only runtime.
- **Pattern**: Data-Driven Architecture (all game data in `data/`, single entry action dispatcher `src/engine/session.py::apply_action`).
- **Interfaces**:
  - CLI: `src/cli.py` (ANSI terminal interactive)
  - Web: `web/app.py` (stdlib `http.server`, REST JSON API, 3-column static UI)
- **Engine Subsystems** (`src/engine/`):
  - `session.py`: Master orchestrator, action router, safe-zone & battle gating, UI view serializer.
  - `state.py`: Dataclass models (`PlayerState`, `GameState`, `UIState`), dynamic computed properties.
  - `battle.py`: Fixed-order turn-based combat, Wuxing 5-element cycle, companion combat logic, KO penalties.
  - `quest.py`: DAG quest engine (1-active invariant, branching, convergence to `q_akademi_07`, repeatable side quests).
  - `dialog.py`: Graph-based dialogue tree, condition evaluators, effect triggers.
  - `cultivation.py`: 9 realms × 10 levels, exponential exp curve, spiritual roots multipliers, auto-breakthrough.
  - `morality.py`: Dao & morality scale ([-100, +100]).
  - `memory.py`: Tianyuan Ling narrative memory unlocking.
  - `effects.py`: State mutation dispatcher (morality, relations, reputation, items, gold, flags).
  - `events.py`: Categorized chronological event logging.
  - `loader.py`: `DataRegistry` startup parser and indexed lookup builder.
  - `tools/validate_data.py`: 16-rule data consistency startup validator.

## Feature Inventory & Status Matrix
| # | Feature | Category | Spec Reference | Implementation Location | Current Status |
|---|---------|----------|----------------|-------------------------|----------------|
| 1 | 9 Ranah Kultivasi & 10 Level | Cultivation | GDD §7, ENGINE §5.4 | `src/engine/cultivation.py`, `data/realms.csv` | DONE (Verified) |
| 2 | Exp Curve & Roots Multiplier | Cultivation | DESIGN §4, ENGINE §9.1 | `src/engine/state.py`, `data/config.json` | DONE (Verified) |
| 3 | Meditasi Grounding (8h cap) | Cultivation | DESIGN §3, ENGINE §12.3 | `src/engine/session.py:261-283` | DONE (Verified) |
| 4 | Auto Breakthrough Level 10 | Cultivation | GDD §7, ENGINE §9.1 | `src/engine/cultivation.py:35-59` | DONE (Verified) |
| 5 | Turn-based Combat & Formulas | Combat | DESIGN §4, ENGINE §8.1 | `src/engine/battle.py:1-362` | DONE (Verified) |
| 6 | Siklus Elemen 五行 (1.5x/0.67x) | Combat | DESIGN §4, ENGINE §8.2 | `src/engine/battle.py:110-140` | DONE (Verified) |
| 7 | Kompanion Roh Awan (Summoning) | Combat | GDD §5.1, ENGINE §9.4 | `src/engine/battle.py:233-267` | DONE (Verified) |
| 8 | KO Penalty (10% exp) & Safe Respawn | Combat | GDD §8, ENGINE §8.3 | `src/engine/battle.py:170-195` | DONE (Verified) |
| 9 | Main Quest DAG (1-active invariant) | Quest | GDD §4, ENGINE §6.1 | `src/engine/quest.py:30-228` | DONE (Verified) |
| 10 | 4 Cabang Insiden & Konvergensi q07 | Quest/Story | STORY §2, ENGINE §6.2 | `data/quests/quests_akademi.json` | DONE (Verified) |
| 11 | 4 Memori Tianyuan Ling | Narrative | GDD §2.1, STORY §4 | `src/engine/memory.py`, `data/memories.json` | DONE (Verified) |
| 12 | Safe Zone Gating (Save/Rest/Craft) | Engine | DESIGN §3, ENGINE §12.3 | `src/engine/session.py:26-36` | DONE (Verified) |
| 13 | Save/Load Path Traversal Protection | Security | ENGINE §13, reviews | `src/engine/session.py:434-454` | DONE (Verified) |
| 14 | Web UI Toko Pedagang (Beli/Jual) | Web/Economy | GDD §11.1, ENGINE §12.3 | `web/static/app.js`, `web/app.py::_context` (merchant_shop) | DONE (Verified) |
| 15 | Web UI Dynamic Alchemy Recipes | Web/Craft | GDD §7, ENGINE §5.7 | `web/static/app.js` (render dari `context.recipes`) | DONE (Verified) |
| 16 | Tianyuan Ling 3-Section UI Panel | UI/Design | GDD §2.1, ENGINE §11.1 | `web/app.py::_tianyuan_payload`, `web/static/app.js` | DONE (Verified) |
| 17 | Side Quest Cooldown Schema & Logic | Quest/Data | ENGINE §5.1, §6.4 | `data/quests/quests_side.json`, `src/engine/quest.py`, `src/engine/state.py` (`side_quest_cooldowns`) | DONE (Verified) |
| 18 | Monster Respawn & NPC Schedule | World Sim | GDD §7, ENGINE §9.2 | `src/engine/session.py::_hunt`, `_is_npc_available` | DONE (Verified) |
| 19 | Arc 1 Completion Summary / Screen | Story/UI | GDD §11.2, DoD | `src/engine/session.py::view` (`arc_summary`), `src/cli.py`, `web/static/app.js` | DONE (Verified) |
| 20 | Edge Case Unit Test Coverage | Testing | QA Review §5.1 | `tests/` (244 test, coverage src ≈ 99,9%) | DONE (Verified) |
| 21 | Architecture Doc Sync | Docs | ENGINE §12, §16 | `docs/ENGINE_ARCHITECTURE.md` (EP3-T2, 2026-08-14) | DONE (Verified) |
| 22 | Relations Berdampak pada Dialog | Relationship | GDD §7, §4.4 | `dialog.py::_eval_condition` (`relation_min/max`), `battle.py::_victory` (`spar_win_relation`), node gated Han Xiu/Gu Canghai | DONE (Verified) |
| 23 | Gating Ingatan → Opsi Dialog | Narrative | GDD §3.1, STORY §3.1 (B3/#13) | `dialog.py::_eval_condition` (`memory`), opsi gated `dlg_moyun`/`dlg_gucanghai` | DONE (Verified) |
| 24 | Tipe Musuh Beragam & Pool Malam | World Sim | GDD §8 | `world.hunt.night_pool`/`night_window`, `session.py::_hunt`, 2 musuh baru (Pembelot Malam, Ular Bayangan) | DONE (Verified) |
| 25 | Teknik Dipelajari & Ditingkatkan (C1) | Combat/Progression | GDD §7, ENGINE §9.1 | efek `technique` (effects.py), `player.techniques`/`technique_levels` (state.py), `upgrade_technique` (session.py), power scaling (battle.py) | DONE (Verified) |

## Identified Gaps and Subagent-Driven Development (SDD) Roadmap

> **Status 2026-08-14**: seluruh gap di bawah telah **dieksekusi dan diverifikasi** (lihat matriks fitur di atas — semua DONE Verified). Roadmap historis.

### Milestone Structure for Roadmap
- **Epic 1: Web UI Feature Parity & Context API (Priority: P0)** — SELESAI
  - `EP1-T1`: Web UI Merchant Shop Modal & Buy/Sell Transaction System
  - `EP1-T2`: Dynamic Recipe Rendering in Web UI Crafting Panel
  - `EP1-T3`: 3-Section Tianyuan Ling UI Modal Alignment
- **Epic 2: Engine Simulation & Data Integrity (Priority: P1)** — SELESAI
  - `EP2-T1`: Side Quest Schema Alignment (`cooldown`) & QuestEngine Enforcement
  - `EP2-T2`: World Simulation: Monster Respawn Timer (5h) & NPC Schedule Check
  - `EP2-T3`: Arc 1 Completion Summary & Statistics Modal (Closure after `q_akademi_07`)
- **Epic 3: Test Hardening & Documentation Synchronization (Priority: P2)** — SELESAI
  - `EP3-T1`: Engine Edge-Case Test Hardening (>95% Branch Coverage)
  - `EP3-T2`: Architecture & GDD Document Drift Remediation

## Code Layout
```
tian-xu-second-life/
├── src/
│   ├── engine/
│   │   ├── session.py       # Master orchestrator & action dispatcher
│   │   ├── state.py         # Data models & state serialization
│   │   ├── battle.py        # Turn-based combat & wuxing
│   │   ├── quest.py         # DAG quest progression
│   │   ├── dialog.py        # Dialogue tree & conditions
│   │   ├── cultivation.py   # Realms, levels, breakthrough
│   │   ├── morality.py      # Dao scale
│   │   ├── memory.py        # Tianyuan Ling memories
│   │   ├── effects.py       # State mutations
│   │   └── events.py        # Chronological event logger
│   ├── loader.py            # DataRegistry loader
│   └── cli.py               # CLI game interface
├── web/
│   ├── app.py               # Web server & REST API
│   └── static/
│       ├── index.html       # 3-column UI layout
│       ├── style.css        # Xianxia theme styles
│       └── app.js           # Frontend client controller
├── data/                    # JSON / CSV game datasets
├── tools/
│   └── validate_data.py     # 16-rule data integrity validator
├── tests/                   # Deterministic test suites (pytest)
└── docs/
    ├── GDD.md               # Game Design Document
    ├── DESIGN_SUMMARY.md    # Approved design decisions
    ├── STORY_FASE1.md       # Narrative & quest design
    ├── ENGINE_ARCHITECTURE.md # Technical architecture & schemas
    └── superpowers/plans/
        └── next-roadmap.md  # Final SDD Roadmap Deliverable
```
