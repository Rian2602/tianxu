# Changelog

All notable changes to Tian Xu: Second Life (天缘灵) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-08-24

### Added
- **Companion Healing**: Heal active companion via Qi cost (configurable in config.json)
- **Location Suggestions**: Travel/hunt/search errors now suggest available locations
- **Item Descriptions**: All 37 items now have descriptive text
- **Connection Gates**: Story-gated travel between locations (prevents premature access)
- **Quest on_start Effects**: Effects execute when quest begins (not just on complete)
- **Web Cinematic Intro**: Full-screen dialog intro on new game
- **NPC Schedules**: 4 NPCs with daily location schedules
- **Technique System**: 30 techniques with elements, tags, status effects, mastery XP
- **Elemental Mastery**: XP-based mastery system with combat bonuses (0-3 levels)
- **Pavilion Passives**: 4 unique passives (Sword Intent, Flowing Qi, Phoenix Blood, Earth Guardian)
- **Technique Evolution**: 4 branching pairs with branch_group mechanic
- **Technique Fusion**: 5 fusion recipes for endgame progression
- **2 New Realms**: Tian Shi + Shen Wu (5 realms total, 25 levels)
- **unlock_arc Column**: Cross-academy technique unlock via arc completion
- **Reactive World Events**: Spiritual Collapse, Mountain Gate, The Last Night
- **Memory Investigation**: Expanded to 8 memories with reliability curves
- **Faction Questlines**: Reformists (5 quests) + Orthodox questline
- **Playtest Plan Tools**: Generate + execute playtest plans via HTTP API
- **Audit Location Gates**: Tool to detect premature content reachability

### Fixed
- **Exp Multiplier**: effects.py now uses gain_exp() for roots multiplier (Critical)
- **Morality Clamp**: resolve_choose() now clamps morality to config bounds
- **Dialog Queue**: pending_dialog_next prevents dialog loss during queue
- **Dialog choose()**: Properly ends dialog on node without choices
- **Memory Reliability**: update_reliability() no longer silently fails
- **Battle Status Logging**: Unknown status kinds now logged for enemies
- **Flag Mismatches**: Fixed 6+ dead flag references in data
- **Data Fixes**: Arc2-7 spar allies, NPC schedules, fusion results, shop recipes
- **unlock_arc**: Added missing column to techniques.csv
- **BFS Connection Gates**: Playtest plan generator respects travel gates

### Changed
- **Save Schema**: v3 → v9 (with migrations v0→v5)
- **Validator**: 7-rule → 14-rule data contract validator
- **Test Suite**: 287 → 377 tests
- **CLI Removed**: Terminal frontend deleted (web-only)
- **Companion Status**: dormant → active (9 companions, max 3 owned)

### Removed
- CLI frontend and entry point
- Dead self-reassignment lines in validate.py
- Dead code in battle.py (_last_exp)
- Dead assignment in quest.py (objective_text)

## [1.0.0] - 2026-08-19

### Added
- **Core Engine**: Python 3.10+ stdlib-only game engine
  - Battle system: Turn-based combat with elemental advantages (五行)
  - Cultivation system: Realm progression with breakthrough mechanics
  - Dialog system: Conditional dialog trees with 19 condition types
  - Quest system: DAG-based main quests + side quests with branching
  - Memory system: Memory unlock with reliability curve
  - Effects system: Data-driven effects (flags, items, relations, reputation)
  - Save system: Versioned schema (v3) with migration support
  - Validator: 7-rule data contract validator (fail-fast)

- **Frontends**: 
  - CLI: Terminal-based game interface
  - Web: HTTP server with JSON API + vanilla JS/CSS/HTML UI

- **Story Content**: 7 arcs of narrative data
  - Arc I: New Life → Pavilion selection
  - Arc II: First Artifact → Branch (Obey/Investigate/Confront)
  - Arc III: Gate Opened → Branch (Seek Truth/Accept Narrative)
  - Arc IV: False History
  - Arc V: World Remembers → Branch (Mountain Gate + Family Crisis)
  - Arc VI: Last Cycle → Final Choice (Preserve/Destroy/Transform/Sacrifice)
  - Arc VII: Second Life → Ending (including Hidden Resolution)

- **Characters**: 18 NPCs with full dialog trees
  - Lin Yue: Bond + Conflict arc (2 quests)
  - Shen Luo: Investigation arc (2 quests)
  - Mei Ruo: Memory investigation prototype (3 quests)
  - Gu Han: Moral conflict arc (2 quests)
  - Grandmaster: Faction questline (2 quests)

- **Game Systems**:
  - Factions: 4 factions with reputation system
  - Companions: Companion system (dormant, data-driven)
  - Hunting: Multi-zone hunting with night pool
  - Crafting: Recipe-based crafting system
  - Shop: NPC merchant system

- **Testing**: 287 pytest tests
  - Smoke tests
  - Arc playthrough tests (Arc I-VII)
  - Engine system tests
  - Adaptivity tests
  - Web integration tests

- **Documentation**: 
  - Story Production Bible (15 docs)
  - Design Gap Report
  - Implementation Readiness Report

### Changed
- Migrated save schema from v1 to v3
- Enhanced dialog routing with priority cascade
- Improved battle system with speed-based turn order
- Added multi-zone hunting support

### Fixed
- Battle victory exp sync (HP/Qi clobbering)
- Memory unlock reliability tracking
- Quest timeout calculation
- Dialog condition evaluation bugs

## [0.1.0] - 2026-08-14

### Added
- Initial engine implementation
- Basic quest/dialog/battle systems
- CLI frontend
- 287 test suite
