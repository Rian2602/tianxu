# Ending Integration — Tian Xu: Second Life

## Overview

This document traces how player choices throughout the game lead to different endings. Each ending requires specific player decisions, faction standings, and knowledge states.

## Endings Summary

| Ending | Name | Requirements | Difficulty |
|--------|------|--------------|------------|
| `preserve` | The Unbroken Heaven | Default choice | Easy |
| `destroy` | The Mortal Dawn | Default choice | Easy |
| `transform` | The New Heaven | Default choice | Easy |
| `sacrifice` | The Nameless Guardian | Default choice | Easy |
| `second_life` | Second Life (Hidden) | 7 flags + 3 anti-conditions | Hard |

## Ending Conditions

### 1. The Unbroken Heaven (`preserve`)

**Narrative**: Tian Xu is preserved. Cultivation continues. The world appears normal on the surface, but the player knows the cost.

**Player Choice**: Select "Preserve" in Arc VII final dialogue.

**Prerequisites**:
- Complete Arc VII: "Malam Terakhir"
- Reach the final dialogue with Jiang Yan's imprint

**Effects**:
```json
{
  "state_ending_achieved": "preserve",
  "relation_npc_grandmaster": +3,
  "reputation_faction_tianxu_orthodox": +3
}
```

**Narrative Payoff**: Player chose stability over change. Grandmaster approves. Orthodox faction strengthens.

---

### 2. The Mortal Dawn (`destroy`)

**Narrative**: Cultivation gradually disappears. Some hate the player, some are grateful. Humanity no longer depends on something they don't understand.

**Player Choice**: Select "Destroy" in Arc VII final dialogue.

**Prerequisites**:
- Complete Arc VII: "Malam Terakhir"
- Reach the final dialogue with Jiang Yan's imprint

**Effects**:
```json
{
  "state_ending_achieved": "destroy",
  "relation_npc_gu_han": +3,
  "reputation_faction_tianxu_orthodox": -4
}
```

**Narrative Payoff**: Player chose liberation over preservation. Gu Han approves. Orthodox faction weakened.

---

### 3. The New Heaven (`transform`)

**Narrative**: New institutions begin to form. This is not a perfect victory — a new generation must learn cultivation from scratch. But for the first time, the world's relationship with its source is not exploitative.

**Player Choice**: Select "Transform" in Arc VII final dialogue.

**Prerequisites**:
- Complete Arc VII: "Malam Terakhir"
- Reach the final dialogue with Jiang Yan's imprint

**Effects**:
```json
{
  "state_ending_achieved": "transform",
  "relation_npc_mei_ruo": +3,
  "relation_npc_shen_luo": +2
}
```

**Narrative Payoff**: Player chose transformation over destruction. Mei Ruo and Shen Luo approve. Balanced approach.

---

### 4. The Nameless Guardian (`sacrifice`)

**Narrative**: The world continues without the player. Some remember the name, some forget. Among those who remain, some never stop thanking the person they never see again.

**Player Choice**: Select "Sacrifice" in Arc VII final dialogue.

**Prerequisites**:
- Complete Arc VII: "Malam Terakhir"
- Reach the final dialogue with Jiang Yan's imprint

**Effects**:
```json
{
  "state_ending_achieved": "sacrifice",
  "relation_npc_mentor": +3
}
```

**Narrative Payoff**: Player chose self-sacrifice. Mentor approves. Bittersweet ending.

---

### 5. Second Life (Hidden Resolution) (`second_life`)

**Narrative**: The first morning of a new world. Lin Yue sits beside the player, looking into the distance, then asks calmly: "If you could live your life again, would you choose the same?"

**Player Choice**: Select "Second Life" in Arc VII final dialogue (requires 7 knowledge flags + 3 anti-conditions).

**Prerequisites** (ALL must be met):

**Knowledge Flags** (must be TRUE):
1. `flag_the_gate_full_truth_known` — Know the full truth about The Gate
2. `flag_tianxu_feeds_segel_known` — Know that Tian Xu feeds the seal
3. `flag_version_iii_read` — Read Version III of the history
4. `flag_jiang_yan_origin_known` — Know Jiang Yan's origin
5. `flag_betrayal_identity_known` — Know about the betrayal
6. `flag_cycle_formation_known_partial` — Know partial truth about Cycle Formation
7. `belief_protagonist_may_be_cause` = FALSE — Do NOT believe the protagonist may be the cause

**Anti-Conditions** (must NOT be true):
1. `state_lin_yue_status` ≠ "disillusioned" — Lin Yue must not be disillusioned
2. `state_identity_stance` ≠ "deny" — Player must not have denied their identity
3. `state_final_principle` ≠ "sacrifice" — Player must not have chosen sacrifice as final principle

**Effects**:
```json
{
  "state_ending_achieved": "second_life",
  "relation_npc_lin_yue": +4
}
```

**Narrative Payoff**: Player achieved the hidden ending through deep investigation and relationship building. Lin Yue approves. True "Second Life" achieved.

---

## Player Choice Traceability

### Arc III: Identity Choice

| Choice | Flag Set | Effect on Endings |
|--------|----------|-------------------|
| "Aku bukan dia." (Deny) | `state_identity_stance = "deny"` | ❌ Blocks Second Life |
| "Mungkin ada benarnya." (Accept Cautious) | `state_identity_stance = "accept_cautious"` | ✅ Allows Second Life |
| "Aku akan mencari kebenaran." (Seek Truth) | `state_identity_stance = "seek_truth"` | ✅ Allows Second Life |

### Arc IV: False History

| Choice | Flag Set | Effect on Endings |
|--------|----------|-------------------|
| Read Version III | `flag_version_iii_read = true` | ✅ Required for Second Life |
| Learn Tian Xu feeds seal | `flag_tianxu_feeds_segel_known = true` | ✅ Required for Second Life |

### Arc V: World Remembers

| Choice | Flag Set | Effect on Endings |
|--------|----------|-------------------|
| Learn about Cycle Formation | `flag_cycle_formation_known_partial = true` | ✅ Required for Second Life |
| Learn about protagonist cause | `belief_protagonist_may_be_cause = true` | ❌ Blocks Second Life |

### Arc VI: Last Cycle

| Choice | Flag Set | Effect on Endings |
|--------|----------|-------------------|
| Learn Jiang Yan origin | `flag_jiang_yan_origin_known = true` | ✅ Required for Second Life |
| Learn about betrayal | `flag_betrayal_identity_known = true` | ✅ Required for Second Life |
| Learn about The Gate truth | `flag_the_gate_full_truth_known = true` | ✅ Required for Second Life |
| Choose "preserve" principle | `state_final_principle = "preserve"` | ✅ Allows Second Life |
| Choose "destroy" principle | `state_final_principle = "destroy"` | ✅ Allows Second Life |
| Choose "transform" principle | `state_final_principle = "transform"` | ✅ Allows Second Life |
| Choose "sacrifice" principle | `state_final_principle = "sacrifice"` | ❌ Blocks Second Life |

### Character Relationships

| Relationship | Effect on Endings |
|--------------|-------------------|
| Lin Yue disillusioned | ❌ Blocks Second Life |
| Lin Yue high relation | ✅ +4 relation in Second Life ending |
| Grandmaster high relation | ✅ +3 relation in Preserve ending |
| Gu Han high relation | ✅ +3 relation in Destroy ending |
| Mei Ruo high relation | ✅ +3 relation in Transform ending |
| Shen Luo high relation | ✅ +2 relation in Transform ending |
| Mentor high relation | ✅ +3 relation in Sacrifice ending |

### Faction Standings

| Faction | Effect on Endings |
|---------|-------------------|
| Orthodox loyal stance | ✅ +3 reputation in Preserve ending |
| Orthodox rebel stance | ✅ +3 reputation in Destroy ending |
| Reformation reform stance | ✅ Available for Transform ending |
| Reformation liberation stance | ✅ Available for Destroy ending |

---

## Ending Matrix

| Condition | Preserve | Destroy | Transform | Sacrifice | Second Life |
|-----------|----------|---------|-----------|-----------|-------------|
| `flag_the_gate_full_truth_known` | - | - | - | - | ✅ Required |
| `flag_tianxu_feeds_segel_known` | - | - | - | - | ✅ Required |
| `flag_version_iii_read` | - | - | - | - | ✅ Required |
| `flag_jiang_yan_origin_known` | - | - | - | - | ✅ Required |
| `flag_betrayal_identity_known` | - | - | - | - | ✅ Required |
| `flag_cycle_formation_known_partial` | - | - | - | - | ✅ Required |
| `belief_protagonist_may_be_cause` | - | - | - | - | ❌ Must be false |
| `state_lin_yue_status` ≠ disillusioned | - | - | - | - | ✅ Required |
| `state_identity_stance` ≠ deny | - | - | - | - | ✅ Required |
| `state_final_principle` ≠ sacrifice | - | - | - | - | ✅ Required |
| `relation_npc_grandmaster` | +3 | - | - | - | - |
| `relation_npc_gu_han` | - | +3 | - | - | - |
| `relation_npc_mei_ruo` | - | - | +3 | - | - |
| `relation_npc_shen_luo` | - | - | +2 | - | - |
| `relation_npc_mentor` | - | - | - | +3 | - |
| `relation_npc_lin_yue` | - | - | - | - | +4 |
| `reputation_orthodox` | +3 | -4 | - | - | - |

---

## Implementation Notes

### Current State

- **5 endings** implemented in Arc VII
- **11 ending conditions** in config
- **7 knowledge flags** required for Second Life
- **3 anti-conditions** block Second Life
- **6 character relationships** affect endings
- **2 faction standings** affect endings

### Data-Driven Design

All ending conditions are defined in `config.json` under `arcs[].endings[]`. The engine evaluates conditions using `DialogEngine._eval_condition()`. No hardcoded ending logic.

### Future Enhancements

1. **Ending variations**: Add dialogue variations based on faction standings
2. **Ending epilogues**: Add post-ending scenes based on player history
3. **New Game+**: Carry over some flags to next playthrough
4. **Achievement system**: Track which endings have been achieved

---

## Summary

| Metric | Value |
|--------|-------|
| Total endings | 5 |
| Simple endings | 4 (Preserve, Destroy, Transform, Sacrifice) |
| Hidden ending | 1 (Second Life) |
| Knowledge flags for Second Life | 7 |
| Anti-conditions for Second Life | 3 |
| Character relationships affecting endings | 6 |
| Faction standings affecting endings | 2 |

**Status: Ending Integration Complete. All player choices traced to endings. 287 tests pass.**
