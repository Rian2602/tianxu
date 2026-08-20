# Spar Debuff & Team Allies Design

## Context

Xu Zhiyuan (npc_proctor) has HP=150, Atk=20, Def=14. Player at this progression point has ~HP=60, Atk=13, Def=5. Solo spar quest is nearly impossible. Team spar quest uses companion beasts instead of NPC allies.

## Design Principles

- Keep the feature quest-scoped: regular spar menu behavior must not change.
- Store new quest knobs on `objective`, because spar behavior is objective-specific.
- Mutate only battle-local copies of combat stats; never mutate NPC registry data.
- Validate new data fields at startup so content errors fail early.

## Feature 1: Quest-Scoped Spar Debuff

**Goal:** Debuff Xu Zhiyuan to 60% power ONLY for the solo spar quest (quest_a02_c01_001). Regular spar menu uses full stats.

**Debuffed stats:** HP=90, Atk=12, Def=8.

### Data changes

**`data/quests/arc02.json`** — add `spar_debuff` to `quest_a02_c01_001.objective`:
```json
"objective": {
  "kind": "spar",
  "npc": "npc_proctor",
  "spar_debuff": {"hp_mult": 0.6, "atk_mult": 0.6, "def_mult": 0.6}
}
```

### Engine changes

**`src/engine/session.py` `_after_dialog()`** — when battle starts from a quest objective with `spar_debuff`, apply multipliers to the local `foe` dict before `battle.start()`.

Apply these fields:
- `hp` and `hp_max`: `max(1, round(hp * hp_mult))`
- `attack`: `max(1, round(attack * atk_mult))`
- `defense`: `max(0, round(defense * def_mult))`

No `BattleEngine.start()` debuff parameter is needed. `session.py` already builds `foe = dict(npc["combat"], ...)`, and `BattleEngine.start()` copies foes again, so registry data and regular `_spar()` remain unaffected.

### Scope

- Only quest_a02_c01_001 uses this initially
- Regular spar menu (`_spar()`) is unaffected
- Future quests can use `spar_debuff` if needed

## Feature 2: NPC Allies for Team Spar

**Goal:** Replace companion beasts with Lin Yue, Shen Luo, Gu Han as allies for quest_a02_c01_002. One ally attacks per turn, rotating.

### Data changes

**`data/npcs.json`** — add `combat` field to Lin Yue, Shen Luo, Gu Han:
```json
Lin Yue: {"hp": 25, "attack": 8, "defense": 4, "speed": 7, "element": "angin"}
Shen Luo: {"hp": 30, "attack": 9, "defense": 5, "speed": 5, "element": "api"}
Gu Han: {"hp": 25, "attack": 10, "defense": 6, "speed": 4, "element": "tanah"}
```

**`data/quests/arc02.json`** — add `allies` field to quest_a02_c01_002:
```json
"objective": {
  "kind": "spar",
  "npc": "npc_proctor",
  "context": "spar_team",
  "allies": ["npc_lin_yue", "npc_shen_luo", "npc_gu_han"]
}
```

### Engine changes

**`src/engine/session.py` `_after_dialog()`** — when quest objective has `context: "spar_team"` and `allies`, build ally list from NPC combat data instead of companions.

Each ally battle dict should include:
- `id`, `name`
- `hp`, `hp_max`
- `attack`, `defense`, `speed`
- optional `element`

Start the battle with `context="spar_team"`, the NPC allies list, and companion behavior disabled for this battle. If `context` is `spar_team` but no valid allies are configured, log a system error and do not silently fall back to companion beasts.

**`src/engine/battle.py`** — modify `_ally_turns()` for rotating one ally per turn:
- Add `ally_turn_index` to battle state
- Each player turn, one living ally attacks, then index advances
- Use a bounded loop over `range(len(allies))` so KO allies are skipped without infinite loops or missed wraparound
- Skip `_companion_turn()` and omit `companion` from battle view when the battle disables companion participation

### UI changes

**`src/engine/battle.py` `view()`** — expose `active_ally_index`, derived from `ally_turn_index` and the next living ally. Do not expose raw `ally_turn_index` as UI truth because it can point at a KO ally.

**`web/static/app.js`** — highlight the active ally card during battle based on `active_ally_index`.

**`web/static/style.css`** — add a restrained active ally style.

## Validation

**`src/validate.py`** should validate:
- `objective.spar_debuff`, when present on `kind: "spar"`, is an object.
- Allowed debuff keys are `hp_mult`, `atk_mult`, `def_mult`.
- Debuff values are numbers greater than 0.
- `objective.allies`, when present, is a non-empty list of known NPC ids.
- Each listed ally NPC has a `combat` object.

## Files changed

| File | Change |
|------|--------|
| `data/quests/arc02.json` | Add `objective.spar_debuff` to quest_a02_c01_001, `objective.allies` to quest_a02_c01_002 |
| `data/npcs.json` | Add `combat` field to Lin Yue, Shen Luo, Gu Han |
| `src/engine/session.py` | Apply debuff; build NPC allies for spar_team |
| `src/engine/battle.py` | Disable companions for NPC team spar; rotate one ally per turn; expose active ally index |
| `src/validate.py` | Validate spar_debuff and ally references |
| `web/static/app.js` | Highlight active ally in battle UI |
| `web/static/style.css` | Active ally highlight style |
| `tests/` | Update spar quest tests |

## Testing

- Solo spar quest completes with debuffed Xu Zhiyuan
- Regular spar menu uses full Xu Zhiyuan stats after the quest debuff path exists
- Team spar shows Lin Yue/Shen Luo/Gu Han as allies
- Team spar does not show or use Serigala/active companions
- One ally attacks per turn, rotating
- KO allies are skipped and rotation continues
- Validator rejects malformed `spar_debuff`, unknown ally ids, and ally NPCs without combat data
- All existing tests pass
