# DESIGN GAP REPORT — Tian Xu: Second Life

**Report Date:** August 2026
**Status:** Post-Phase 7 (Reactive World Event Prototype)
**Player Testing:** READY (9/9 requirements met)

---

## Executive Summary

After completing Phases 0-7, the game has:
- 47 quests (36 main, 11 side)
- 46 dialogs
- 66 written states, 32 alive
- 4 character arcs (Lin Yue, Shen Luo, Mei Ruo, Gu Han)
- 1 memory investigation prototype
- 1 faction prototype (Tian Xu Orthodox)
- 1 reactive world event prototype
- 287 tests passing
- 0 critical issues

**Remaining gaps are DESIGN decisions, not bugs.** They require narrative/design input before implementation.

---

## Gap Categories

### A. CRITICAL DESIGN GAPS (Must resolve before full release)

---

#### GAP-A1: Realm Progression Incomplete

**Status: ✅ RESOLVED**

**Resolution:**
- Added 2 new realms: `realm_tengah` (order=2) and `realm_atas` (order=3)
- Each realm has 5 levels with escalating stats:
  - `realm_awal`: base_hp=50, base_qi=30
  - `realm_tengah`: base_hp=100, base_qi=60
  - `realm_atas`: base_hp=200, base_qi=120
- Breakthrough logic verified: realm_awal → realm_tengah → realm_atas → max
- All 287 tests pass

**Impact:**
- Players can now progress through 3 realms (15 levels total)
- Breakthrough mechanic fully testable
- Core RPG progression complete for player testing

---

#### GAP-A2: Missing Characters in Arcs I-III

**Status: ✅ RESOLVED**

**Resolution:**
- Added `dialog_routes.side` for Shen Luo, Mei Ruo, Gu Han, Grandmaster
  (engine can now route to character quest offer/report dialogs)
- Added `available_from.relation_min` to all character quests
  (quests only offered when relationship threshold met)
- Added relationship-gated dialogue variants in Arc IV and Arc V
  (Grandmaster dialogue changes when Shen Luo relationship ≥ 5)
  (Lin Yue dialogue changes when Gu Han relationship ≥ 5)
- Removed unused `side_offers` field from NPCs

**Impact:**
- Players discover character quests through NPC conversations
- Character quests require minimum relationship to unlock
- Main quest dialogues react to character relationships
- Character development is now integrated into main story flow

---

#### GAP-A3: Branching Content Still Shallow

**Status: ✅ RESOLVED**

**Resolution:**
- Added unique branch quests for Arc II Obey/Investigate/Confront paths:
  - Obey: quest_a02_c04_007a (talk to proctor)
  - Investigate: quest_a02_c04_007b (reach archive)
  - Confront: quest_a02_c04_007c (confront grandmaster)
- Added unique dialogues for each branch path
- All branches now have unique objectives before convergence
- Branch-specific dialog routes added to NPCs

**Impact:**
- Each branch now has unique content (dialogue + objective)
- Players experience different gameplay per branch
- Replay value increased
- Quality over quantity maintained (1 meaningful branch deepened)

---

### B. IMPORTANT DESIGN GAPS (Should resolve before full release)

---

#### GAP-B1: Memory Investigation Only 1 Prototype

**Status: ✅ RESOLVED**

**Resolution:**
- Added investigation system for 3 more memories: `memory_a01_m01` (Koridor Terbakar), `memory_a01_m02` (Tangan yang Mengingat), `memory_a01_m04` (Jangan Percaya Sejarah), `memory_a02_m01` (Apa yang Tidak Akan Kau Kembali)
- Each investigation has offer + report dialogs with Mei Ruo
- Reinterpretation flags affect Arc IV and V dialogs:
  - `state_memory_a01_m01_reinterpretation = coverup` → special Arc IV entry dialog
  - `state_memory_a01_m02_reinterpretation = past_life` → special Arc IV entry + Version III dialog
  - `state_memory_a02_m01_reinterpretation = connected` → special Arc V Lin Yue dialogue
- Investigation quests available via `has_memory` condition (optional, reward: relation + reinterpretation)
- All 287 tests pass

**Impact:**
- Players experience memory investigation 4 times (up from 1)
- Investigation choices affect later story content
- Mystery mechanic fully utilized across arcs
- Optional but rewarding (relation bonus with Mei Ruo)

---

#### GAP-B2: Faction System Only 1 Prototype

**Current State:**
- Only Tian Xu Orthodox has faction questline
- Other 3 factions (Reformists, Liberation, Hidden Guardians) have no quests
- Faction reputation only affects dialogue conditions

**Impact:**
- Faction system feels incomplete
- Players only interact with one faction
- Political dynamics are underexplored

**Design Decision Needed:**
- Which other factions should have questlines?
- How should faction reputation affect gameplay?
- Should factions have opposing goals?

**Recommendation:**
- Add 1 more faction questline (Liberation or Reformists)
- Keep faction effects simple (dialogue variants, access conditions)
- Focus on faction identity over faction quantity

---

#### GAP-B3: Reactive World Events Only 1 Prototype

**Current State:**
- Only Spiritual Collapse has reactive dialogue
- The Last Night has no reactive elements
- World events don't change based on player history

**Impact:**
- World feels static despite player actions
- Consequences of player choices are limited
- World reactivity is underutilized

**Design Decision Needed:**
- Which world events should be reactive?
- How should player history affect world events?
- Should world events have multiple outcomes?

**Recommendation:**
- Add reactive elements to The Last Night
- Keep reactive scope small (1-2 conditions per event)
- Focus on quality of reactivity over quantity

---

#### GAP-B4: Dead Flags (34 total)

**Current State:**
- 34 flags are written but never read
- Most are legitimate tracking flags
- Some could potentially be connected to future content

**Impact:**
- No functional impact (tracking flags are harmless)
- Potential future use is unexplored
- Codebase has some dead code

**Design Decision Needed:**
- Should tracking flags be connected to future content?
- Are there opportunities to make dead flags meaningful?
- Should dead flags be removed or kept for potential use?

**Recommendation:**
- Keep tracking flags for potential future use
- Connect 1-2 dead flags to Arc VI/VII content if possible
- Don't remove tracking flags (they're harmless and may be useful)

---

### C. MINOR DESIGN GAPS (Nice to have, low priority)

---

#### GAP-C1: Quest Linearity in Arcs I-III

**Current State:**
- Arcs I-III are mostly linear (one quest leads to next)
- Limited branching in early arcs
- Player choices have minimal impact on progression

**Impact:**
- Early game feels linear
- Player agency is limited in early arcs
- Replay value is low for early content

**Design Decision Needed:**
- Should early arcs have more branching?
- How much player agency should exist in early arcs?
- Is linearity acceptable for tutorial/introduction arcs?

**Recommendation:**
- Keep early arcs linear for player testing (tutorial purpose)
- Add branching in Arc IV+ where story becomes more complex
- Linearity in early arcs is acceptable and common in RPGs

---

#### GAP-C2: Dialogue Condition Count (4/90)

**Current State:**
- Only 4 out of 90 choices have conditions
- Most choices are unconditional
- Limited state-dependent dialogue

**Impact:**
- Dialogue feels static
- Player state doesn't affect most conversations
- Limited replay value from dialogue variations

**Design Decision Needed:**
- How many choices should have conditions?
- What states should affect dialogue?
- Should conditions be simple (flag check) or complex (multi-state)?

**Recommendation:**
- For player testing, current count is sufficient
- Add 5-10 more conditional choices in Arc IV+ content
- Focus on meaningful conditions (character relationship, faction reputation)

---

#### GAP-C3: NPC Side-Offer System Unused by Players

**Current State:**
- All 4 character NPCs and Grandmaster have side_offers
- Side-offers are routed via `side_offers` array in npcs.json
- Players must manually talk to NPCs to trigger quests

**Impact:**
- Players may miss character quests
- Quest discovery is passive
- Side-offers are not prominently displayed

**Design Decision Needed:**
- Should side-offers be automatically offered?
- How should players discover available quests?
- Should quest availability be more visible?

**Recommendation:**
- Keep side-offers as-is for player testing
- Consider adding quest availability indicators in future
- Quest discovery through exploration is acceptable

---

## Gap Priority Matrix

| Gap | Priority | Effort | Impact | Recommendation |
|-----|----------|--------|--------|----------------|
| ~~A1: Realm Progression~~ | ~~HIGH~~ | ~~HIGH~~ | ~~HIGH~~ | ✅ RESOLVED |
| ~~A2: Missing Characters~~ | ~~HIGH~~ | ~~HIGH~~ | ~~HIGH~~ | ✅ RESOLVED |
| ~~A3: Branching Shallow~~ | ~~MEDIUM~~ | ~~HIGH~~ | ~~MEDIUM~~ | ✅ RESOLVED |
| ~~B1: Memory Investigation~~ | ~~MEDIUM~~ | ~~MEDIUM~~ | ~~MEDIUM~~ | ✅ RESOLVED |
| B2: Faction System | MEDIUM | MEDIUM | MEDIUM | Add 1 more faction |
| B3: Reactive World | MEDIUM | LOW | MEDIUM | Add to The Last Night |
| B4: Dead Flags | LOW | LOW | LOW | Keep for potential use |
| C1: Quest Linearity | LOW | HIGH | LOW | Acceptable for testing |
| C2: Dialogue Conditions | LOW | MEDIUM | LOW | Add 5-10 more |
| C3: Side-Offer Discovery | LOW | LOW | LOW | Keep as-is |

---

## Recommendations for Next Phase

### Immediate (Before Player Testing)
1. **GAP-A1**: Add 2 more realms for cultivation progression ✅
2. **GAP-B1**: Expand memory investigation to 2 more memories ✅

### Short-term (During Player Testing)
3. **GAP-B2**: Add 1 more faction questline (Liberation)
4. **GAP-B3**: Add reactive elements to The Last Night

### Medium-term (After Player Testing)
5. **GAP-A2**: Integrate character development into main quests
6. **GAP-A3**: Add 1-2 meaningful branches with unique content

### Long-term (Full Release)
7. **GAP-C1-C3**: Address minor gaps based on player feedback

---

## Conclusion

The game is **READY for player testing** with current gaps. All critical systems are functional:
- Character arcs work
- Memory investigation works
- Faction system works
- World reactivity works
- Branch consequences work

Remaining gaps are **design decisions** that require narrative input, not technical fixes. They should be addressed based on player feedback and testing results.

---

**Report generated by:** Narrative QA Audit System
**Last updated:** August 2026
