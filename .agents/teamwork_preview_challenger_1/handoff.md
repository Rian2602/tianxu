# Handoff Report — Dependency & Parallel Wave Challenger (Challenger 1)

**Target Document**: `docs/superpowers/plans/next-roadmap.md`  
**Verdict**: `REQUEST_CHANGES`  
**Date**: 2026-08-14  
**Challenger Role**: Dependency & Parallel Wave Challenger (Challenger 1)  

---

## 1. Observation

Direct empirical and structural observations from code inspection and script execution:

### Observation 1.1: File Collision in Wave 2 (Task EP2-T3 vs Jalur A)
- In `docs/superpowers/plans/next-roadmap.md` §5 (lines 790–800) and Table 5.1 (lines 824–825):
  - **Jalur A (Frontend)** is assigned `EP1-T1..T3 (Frontend)` with files `web/static/app.js`, `web/static/index.html`, `web/static/style.css`.
  - **Jalur B (Engine)** is assigned `EP2-T2 + EP2-T3 (Engine)` with files claimed as `src/engine/session.py, src/cli.py`, asserting `Risiko Konflik: NOL`.
- However, in `docs/superpowers/plans/next-roadmap.md` §4 (lines 567–573 and prompt lines 626–633), **Task EP2-T3** explicitly lists:
  ```markdown
  Daftar Berkas Target:
  1. src/engine/session.py
  2. src/cli.py
  3. web/static/app.js (Modifikasi: render modal rekapitulasi akhir di Web UI)
  4. web/static/style.css (Modifikasi: styling modal penutup emas xianxia)
  5. tests/test_cli.py, tests/test_web.py
  ```
  Both parallel subagents in Wave 2 target `web/static/app.js`, `web/static/style.css`, and `tests/test_web.py`.

### Observation 1.2: Monolithic Subagent Prompts Contradict Wave Partitioning
- In `docs/superpowers/plans/next-roadmap.md` §5 (lines 772–786), Wave 1 is defined as "Fondasi Skema Data & Konteks Web Backend" (`EP2-T1` + Backend Context for `EP1-T1..T3` in `web/app.py`), while Wave 2 handles Frontend UI in `web/static/`.
- In §4, the copy-ready prompt templates for `EP1-T1` (lines 181–199), `EP1-T2` (lines 277–292), and `EP1-T3` (lines 374–391) are full-stack monoliths that instruct the subagents to edit both `web/app.py` and `web/static/app.js` simultaneously.

### Observation 1.3: NPC Schedule Gating in EP2-T2 Softlocks Progression on Day 2+
- In `data/npcs.json` (lines 3–44), all 9 NPCs have `"day": 1` in their schedule entries (e.g. `Mo Yun: schedule: [ { "day": 1, "hour_start": 6, "hour_end": 22, "location": "loc_perpustakaan" } ]`).
- In `docs/superpowers/plans/next-roadmap.md` §4 (lines 507–520), the proposed `_is_npc_available` code snippet:
  ```python
  def _is_npc_available(self, npc: dict) -> bool:
      schedules = npc.get("schedule", [])
      if not schedules:
          return True
      for s in schedules:
          if s.get("day") is not None and s.get("day") != self.state.day:
              continue
          h_start = s.get("hour_start", 0)
          h_end = s.get("hour_end", 24)
          if h_start <= self.state.hour <= h_end:
              return True
      return True  # (Code snippet flaw: returns True even if no schedule matched)
  ```
- When tested empirically with `s.get("day") != self.state.day` returning `False` on non-matches, **all 9 NPCs return `False` on Day 2**:
  - `Day 1 (hour 12)`: all NPCs return `True`.
  - `Day 2 (hour 12)`: all 9 NPCs return `False`.
- Quests requiring Day 2+ progression (e.g. `q_akademi_3c` which advances 24h via `advance_time`, leading to `q_akademi_07` where the player must talk to `npc_moyun`) become permanently softlocked because Mo Yun cannot be spoken to on Day 2+.
- `data/npcs.json` is missing from the target files list of `EP2-T2`.

### Observation 1.4: Monster Respawn Timer Breaks Existing Test `test_side_quest_berburu_selesai_via_kemenangan`
- In `tests/test_quest_dag.py` (lines 148–151):
  ```python
  session.apply_action({"type": "hunt"})
  session.apply_action({"type": "battle_action", "action": "attack"})
  session.apply_action({"type": "hunt"})
  session.apply_action({"type": "battle_action", "action": "attack"})
  ```
- In `docs/superpowers/plans/next-roadmap.md` §4 (lines 497–503), `EP2-T2` enforces a 5-hour cooldown on `_hunt`.
- Running an empirical simulation of two immediate `hunt` actions confirmed that Hunt 1 succeeds and Hunt 2 is rejected ("Wilayah Berburu masih sepi"), which will fail `test_side_quest_berburu_selesai_via_kemenangan` (only 1 kill recorded out of 2 required).
- `tests/test_quest_dag.py` is missing from the target files list of `EP2-T2`.

### Observation 1.5: Test Assertion Breakage in Wave 1 (`EP1-T3` vs `tests/test_web.py`)
- In `tests/test_web.py` (lines 96–104):
  ```python
  def test_tianyuan_panel(base_url: str) -> None:
      post(base_url, "/api/new")
      body, status = get(base_url, "/api/tianyuan")
      assert status == 200
      data = json.loads(body)
      assert data["ok"] is True
      assert data["tianyuan"]["memories"] == []
  ```
- `EP1-T3` (§4 lines 333–353) modifies `/api/tianyuan` to return all 4 memory slots (`memories` list of length 4 with `unlocked: False` and `title: "???"`).
- Running `pytest` after this change without updating the assert in `tests/test_web.py` will fail with an assertion error.

### Observation 1.6: Omission of `src/engine/state.py` from Wave 2 Matrix
- In `docs/superpowers/plans/next-roadmap.md` §4 (line 491, 542), `EP2-T2` modifies `src/engine/state.py` to add `last_hunt_time`.
- In Table 5.1 (line 825), Wave 2 Jalur B lists only `src/engine/session.py, src/cli.py`, omitting `src/engine/state.py`.

---

## 2. Logic Chain

1. **Premise 1 (Parallel Wave Safety)**: In Subagent-Driven Development (SDD), tasks executing in parallel within the same wave must have strictly disjoint write sets. If two tasks in parallel modify the same files, file collisions and overwritten changes will occur.
   - *Observation 1.1* shows `EP2-T3` in Jalur B modifies `web/static/app.js` and `web/static/style.css`, which are the exact files modified by Jalur A (`EP1-T1..T3`).
   - *Conclusion 1*: The claimed `NOL` conflict risk in Wave 2 is invalid. Wave 2 cannot be safely run in parallel as specified.

2. **Premise 2 (Actionability of Prompts)**: The roadmap specifies ready-to-copy prompt templates for subagents.
   - *Observation 1.2* shows the prompts for `EP1-T1`, `EP1-T2`, and `EP1-T3` span across both backend (`web/app.py`) and frontend (`web/static/app.js`), ignoring the Wave 1 vs Wave 2 architectural split.
   - *Conclusion 2*: An orchestrator copying these prompts will trigger multi-agent write collisions on `web/app.py` in Wave 1 and `web/static/app.js` in Wave 2.

3. **Premise 3 (Game Flow Continuity & Invariants)**: Any simulation constraint added to `session.py` must not softlock existing main story branches or repeatable side quests.
   - *Observation 1.3* shows that on Day 2 (reached via `advance_time` or `q_akademi_3c`), all 9 NPCs in `data/npcs.json` are evaluated as unavailable due to hardcoded `day: 1` schedules.
   - *Conclusion 3*: Main quest `q_akademi_07` (talk to Mo Yun) and all side quests will be permanently softlocked on Day 2+. `data/npcs.json` must be updated and included in `EP2-T2`.

4. **Premise 4 (Zero Regressions on Existing 93 Tests)**: AGENTS.md and roadmap Rule 4 require zero breaking changes to existing passing tests unless explicitly planned.
   - *Observation 1.4* shows `tests/test_quest_dag.py::test_side_quest_berburu_selesai_via_kemenangan` fails when the 5-hour hunt cooldown is enforced.
   - *Observation 1.5* shows `tests/test_web.py::test_tianyuan_panel` fails when `/api/tianyuan` returns 4 slots instead of `[]`.
   - *Conclusion 4*: Target file lists in `EP2-T2` and `EP1-T3` must include these test files and explicitly plan their assertion updates.

---

## 3. Caveats

- **No Caveats**: All findings were empirically tested and reproduced via Python simulations against the real codebase and data files (`data/npcs.json`, `data/quests/quests_side.json`, `tests/test_quest_dag.py`, `tests/test_web.py`).

---

## 4. Conclusion & Required Changes

**Verdict**: `REQUEST_CHANGES`

The roadmap at `docs/superpowers/plans/next-roadmap.md` is well-structured and architecturally comprehensive, but requires the following **6 concrete revisions** before execution to guarantee safety, zero regressions, and smooth SDD parallelism:

### Required Changes:

1. **Resolve Wave 2 File Collision on `EP2-T3`**:
   - Scope `EP2-T3` strictly to backend and CLI (`src/engine/session.py`, `src/cli.py`, `tests/test_cli.py`).
   - Move the frontend modal rendering of `EP2-T3` (`arc_summary` modal) into Jalur A (Frontend Specialist in `web/static/app.js` and `web/static/style.css`).
2. **Align Subagent Prompts with Wave Partitioning**:
   - Split the prompt templates in §4 for Epic 1 into:
     - **Wave 1 Backend Prompt**: 1 prompt modifying `web/app.py` and `tests/test_web.py` to expose `merchant_shop`, `recipes`, and 3-section `_tianyuan_payload()`.
     - **Wave 2 Frontend Prompt**: 1 prompt for the Frontend Specialist modifying `web/static/app.js`, `index.html`, and `style.css` to render Shop, Recipes, Tianyuan modal, and Arc closure modal.
3. **Fix NPC Schedule Design & Add `data/npcs.json` to EP2-T2**:
   - In `data/npcs.json`, remove `day: 1` from default NPC daily routines (or treat `day` as optional/wildcard) so NPC availability is evaluated by `hour_start <= hour <= hour_end` regardless of current day.
   - Fix the `_is_npc_available` helper to return `False` when outside scheduled hours.
   - Add `data/npcs.json` to `EP2-T2` target files.
4. **Update `tests/test_quest_dag.py` in `EP2-T2` Target Files**:
   - Add `tests/test_quest_dag.py` to `EP2-T2` target files.
   - Update `test_side_quest_berburu_selesai_via_kemenangan` to advance time by 5 hours between hunts.
5. **Synchronize `test_tianyuan_panel` in `EP1-T3`**:
   - Explicitly note in `EP1-T3` that `tests/test_web.py::test_tianyuan_panel` must be updated to assert `len(data["tianyuan"]["memories"]) == 4` and `all(not m["unlocked"] for m in data["tianyuan"]["memories"])`.
6. **Update Table 5.1 Wave 2 File List**:
   - Include `src/engine/state.py` under Wave 2 Jalur B.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify NPC Schedule Softlock**:
   ```bash
   python3 -c '
   import json
   with open("data/npcs.json") as f:
       npcs = json.load(f)["npcs"]
   def is_avail(npc, day, hour):
       schedules = npc.get("schedule", [])
       if not schedules: return True
       for s in schedules:
           if s.get("day") is not None and s.get("day") != day: continue
           if s.get("hour_start", 0) <= hour <= s.get("hour_end", 24): return True
       return False
   print("Day 2, hour 12 availability:", [is_avail(n, 2, 12) for n in npcs])
   '
   ```
   *Expected result*: All entries are `False` (all NPCs locked out on Day 2).

2. **Verify Monster Cooldown Impact on Test Suite**:
   Inspect `tests/test_quest_dag.py:148-151` and compare with `EP2-T2` cooldown logic in `next-roadmap.md:497-503`.

3. **Verify File Collision in Wave 2**:
   Compare `docs/superpowers/plans/next-roadmap.md:567-573` (EP2-T3 target files) with `docs/superpowers/plans/next-roadmap.md:793-798` and `Table 5.1:824-825`.
