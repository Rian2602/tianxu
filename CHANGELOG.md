# Changelog

All notable changes to Tian Xu: Second Life (天缘灵) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
