<div align="center">

# 天缘灵 · Tian Xu: Second Life

**Xianxia Cultivation RPG — Python Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-287%20passing-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-CLI%20%2B%20Web-lightgrey)]()

*A data-driven text RPG engine where every choice shapes your destiny across seven arcs of cultivation, mystery, and consequence.*

[Play CLI](#quick-start) · [Play Web](#web-mode) · [Story Bible](docs/) · [Changelog](CHANGELOG.md)

</div>

---

## Overview

Tian Xu: Second Life is a **single-player xianxia cultivation RPG** built with a **pure Python stdlib engine** — zero external dependencies. The game features:

- **7 narrative arcs** with branching quests and convergence
- **18 NPCs** with conditional dialog trees and character agency
- **4 faction system** with reputation-driven content
- **Memory investigation** mechanics with reliability curves
- **Turn-based battle** with elemental advantages (五行)
- **Realm cultivation** progression across 3 realms, 15 levels
- **Data-driven architecture** — add content by editing JSON/CSV, zero code changes

## Screenshots

```
┌─────────────────────────────────────────────┐
│  天缘灵 · TIAN XU: SECOND LIFE             │
│─────────────────────────────────────────────│
│  🏯 loc_tianxu_gate                        │
│  📅 Day 1 · Hour 6 · Bulan 1              │
│─────────────────────────────────────────────│
│  👤 Kultivator                              │
│  💫 realm_awal Lv.1  ⚡ 0/100              │
│  ❤️ HP: 50/50  🔵 Qi: 30/30               │
│  💰 Gold: 0                                │
│─────────────────────────────────────────────│
│  📋 Quest: Beban Seorang Teman             │
│─────────────────────────────────────────────│
│  [bicara] [pindah] [meditasi] [berburu]    │
│  [cari] [spar] [pakai] [beli] [racik]      │
└─────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- No pip install needed — stdlib only

### CLI Mode

```bash
# Start new game
python3 src/cli.py

# Load save file
python3 src/cli.py -l save1
```

### Web Mode

```bash
# Start web server
python3 web/app.py

# Open browser to http://127.0.0.1:8000
```

### Run Tests

```bash
# Full test suite (287 tests, ~3.7s)
pytest

# Smoke tests only
pytest tests/test_smoke.py
```

## Architecture

```
tian-xu-second-life/
├── src/
│   ├── engine/           # Core game engine
│   │   ├── session.py    # Action orchestrator
│   │   ├── quest.py      # DAG quest system
│   │   ├── dialog.py     # Conditional dialog trees
│   │   ├── battle.py     # Turn-based combat
│   │   ├── cultivation.py # Realm progression
│   │   ├── state.py      # Game state + save/load
│   │   └── effects.py    # Data-driven effects
│   ├── cli.py            # Terminal frontend
│   ├── loader.py         # Data registry
│   └── validate.py       # Data contract validator
├── web/
│   ├── app.py            # HTTP server + JSON API
│   └── static/           # JS/CSS/HTML frontend
├── data/                 # Game data (7 arcs)
│   ├── quests/           # Quest definitions
│   ├── dialogs/          # Dialog trees
│   ├── npcs.json         # NPC definitions
│   ├── locations.json    # World locations
│   ├── items.csv         # Items
│   ├── enemies.csv       # Enemies
│   ├── techniques.csv    # Combat techniques
│   ├── realms.csv        # Cultivation realms
│   ├── memories.json     # Memory fragments
│   ├── factions.json     # Faction data
│   └── config.json       # Game configuration
├── tests/                # 287 pytest tests
├── docs/                 # Story Production Bible
└── pyproject.toml        # Build configuration
```

## Key Features

### Data-Driven Content

All game content lives in `data/`. To add a new quest, NPC, or dialog:

1. Edit JSON/CSV files in `data/`
2. Run validator: `python3 -c "from src.loader import DataRegistry; DataRegistry('data')"`
3. Play the game — zero code changes needed

### Engine Architecture

- **Dispatch Tables**: `CONDITION_CHECKERS`, `OBJECTIVE_HANDLERS`, `EFFECT_HANDLERS` — add new types by adding dict keys
- **UI-Agnostic**: `session.view()` returns a plain dict; both CLI and web render from the same data
- **Save System**: Versioned schema (v3) with forward migration and path traversal protection
- **Validator**: 7-rule data contract validator that fails fast with all violations

### Story Content

| Arc | Title | Branches | Endings |
|-----|-------|----------|---------|
| I | New Life | Pavilion selection | 1 |
| II | First Artifact | Obey / Investigate / Confront | 2 |
| III | Gate Opened | Seek Truth / Accept Narrative | 1 |
| IV | False History | — | 1 |
| V | World Remembers | Mountain Gate + Family Crisis | 3 |
| VI | Last Cycle | Preserve / Destroy / Transform / Sacrifice | 4 |
| VII | Second Life | Hidden Resolution | 1 |

**Total**: 50 quests · 49 dialogs · 18 NPCs · 11 endings

### Character System

- **Lin Yue**: Bond → Conflict → Agency arc
- **Shen Luo**: Investigation → Stance decision
- **Mei Ruo**: Memory investigation prototype
- **Gu Han**: Moral conflict → Independent choice

### Combat

- Turn-based with elemental advantages (五行: logam → kayu → tanah → air → api → logam)
- Status effects (DoT, Stun)
- Companion system (dormant, data-driven)
- Critical hits with configurable rates

## Documentation

| Document | Description |
|----------|-------------|
| [Story Production Bible](docs/) | 15-doc narrative architecture |
| [Changelog](CHANGELOG.md) | Version history |
| [Design Gap Report](docs/DESIGN_GAP_REPORT.md) | Known gaps and roadmap |
| [Implementation Readiness](docs/15-implementation-readiness-report.md) | Release readiness audit |

## Development

### Project Conventions

- **Python 3.10+** with type hints
- **No walrus operator** (`:=`) — conservative style
- **No external dependencies** — stdlib only
- **Indonesian** UI text, **English** code identifiers
- **Dispatch tables** over if/elif chains

### Testing

```bash
# Run all tests
pytest

# Run specific arc
pytest tests/test_arc1_data.py

# Run with coverage
pytest --cov=src
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- Xianxia genre inspiration
- Python stdlib community
- Data-driven RPG architecture patterns

---

<div align="center">

**天缘灵 · Tian Xu: Second Life**

*Every choice shapes your destiny.*

</div>
