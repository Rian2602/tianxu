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

**Current State:**
- Characters (Lin Yue, Shen Luo, Mei Ruo, Gu Han) only have character quests in standalone side quest files
- No character development in the main Arc I-III questlines
- Character relationships only change via side quest effects

**Impact:**
- Main story feels disconnected from character arcs
- Players may not encounter character quests
- Character development is optional, not integrated

**Design Decision Needed:**
- Should character quests be required or optional?
- How should character development be integrated into main quest flow?
- Should character relationships affect main quest availability?

**Recommendation:**
- Character quests should be discoverable but not required for main progression
- Add character interaction opportunities in main quest dialogues
- Consider making character relationship thresholds gate certain content

---

#### GAP-A3: Branching Content Still Shallow

**Current State:**
- 4 branching quests exist, but all converge to the same next quest
- Branch consequences are primarily dialogue variants
- No unique objectives or locations per branch

**Impact:**
- Branching feels cosmetic rather than meaningful
- Players don't experience truly different content
- Replay value is limited

**Design Decision Needed:**
- Should branches lead to different quests?
- Should branches unlock different locations?
- How deep should branching go (1 quest vs 1 arc)?

**Recommendation:**
- For player testing, current depth is sufficient
- For full release, consider 1-2 branches with unique quest chains
- Focus on quality over quantity (1 meaningful branch > 5 cosmetic ones)

---

### B. IMPORTANT DESIGN GAPS (Should resolve before full release)

---

#### GAP-B1: Memory Investigation Only 1 Prototype

**Current State:**
- Only `memory_a03_m01` has investigation system
- Other 7 memories are still linear unlock
- No investigation for later arc memories

**Impact:**
- Memory system feels incomplete
- Players only experience investigation once
- Mystery mechanic is underutilized

**Design Decision Needed:**
- Which other memories should have investigation?
- How complex should investigation be (simple vs multi-step)?
- Should investigation be required or optional?

**Recommendation:**
- Expand to 2-3 more memories for player testing
- Keep investigation simple (question → evidence → reinterpretation)
- Make investigation optional but rewarding

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
| A2: Missing Characters | HIGH | HIGH | HIGH | Integrate into main quests |
| A3: Branching Shallow | MEDIUM | HIGH | MEDIUM | Keep for testing, expand later |
| B1: Memory Investigation | MEDIUM | MEDIUM | MEDIUM | Add 2 more prototypes |
| B2: Faction System | MEDIUM | MEDIUM | MEDIUM | Add 1 more faction |
| B3: Reactive World | MEDIUM | LOW | MEDIUM | Add to The Last Night |
| B4: Dead Flags | LOW | LOW | LOW | Keep for potential use |
| C1: Quest Linearity | LOW | HIGH | LOW | Acceptable for testing |
| C2: Dialogue Conditions | LOW | MEDIUM | LOW | Add 5-10 more |
| C3: Side-Offer Discovery | LOW | LOW | LOW | Keep as-is |

---

## Recommendations for Next Phase

### Immediate (Before Player Testing)
1. **GAP-A1**: Add 2 more realms for cultivation progression
2. **GAP-B1**: Expand memory investigation to 2 more memories

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
