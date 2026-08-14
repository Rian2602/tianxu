## 2026-08-14T04:27:05Z

You are Worker 2 for Tian Xu: Second Life.
Your working directory is: /home/dienk/tian-xu-second-life/.agents/teamwork_preview_worker_author_2
Original request: /home/dienk/tian-xu-second-life/.agents/ORIGINAL_REQUEST.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You have exclusive write ownership of `/home/dienk/tian-xu-second-life/docs/superpowers/plans/next-roadmap.md`.

Task:
Refine and update `/home/dienk/tian-xu-second-life/docs/superpowers/plans/next-roadmap.md` to address all high-value findings from the adversarial challenger reports:

1. **NPC Schedule Daily Recurrence & Softlock Prevention (EP2-T2)**:
   - In `EP2-T2`, clarify that NPC schedule checking in `session.py` evaluates daily recurring operating hours (matching `start_hour <= state.hour <= end_hour` across days, or `entry.get("day") in (None, state.day)`), so NPCs are not permanently locked out on Day 2+.
   - Add `data/npcs.json` to the target files list.
   - Clarify fallback message behavior when NPC is not available.
2. **Parallel Execution Isolation & Zero File Collision (Wave 2 Jalur A vs Jalur B & Section 5)**:
   - Refactor Section 4 & Section 5 so that `EP2-T3` (Arc 1 Completion Closure) has a clear separation: Backend state/CLI closure in Wave 2 Jalur B (`session.py`, `cli.py`), and Frontend UI modal rendering in Wave 2 Jalur A (`app.js`, `style.css`) or as Wave 3 polish.
   - Update Table 5.1 (Matriks Isolasi Berkas) to explicitly include `src/engine/state.py` in Wave 2 Jalur B.
3. **Subagent Prompt Templates Alignment**:
   - Ensure the subagent prompt templates in Section 4 reflect the phased file ownership cleanly.
4. **Tianyuan Ling Mission Payload Structure (EP1-T3)**:
   - Refine `mission` payload structure to `{"main": ..., "side_quests": [...]}` so side quests are preserved even if `current_quest` is None.
   - Explicitly note in test plans to synchronize test assertions in `tests/test_web.py`.
5. **Monster Respawn Timer & Test Suite Sync (EP2-T2)**:
   - Add `tests/test_quest_dag.py` to EP2-T2 target files and note that tests performing back-to-back hunts should advance time by 5 hours or mock `last_hunt_time`.
6. **Frontend Modal Dismissal State (EP2-T3)**:
   - Specify `state.arc_summary_dismissed` flag in frontend state to prevent infinite popup loops on subsequent user actions.
7. **Defensive Save/Load Serialization**:
   - Explicitly require defensive `.get()` patterns in `GameState.from_dict()` for `side_quest_cooldowns` and `last_hunt_time` to preserve backward compatibility with older save files.

Write your handoff report at `/home/dienk/tian-xu-second-life/.agents/teamwork_preview_worker_author_2/handoff.md` and send a message back when complete.
