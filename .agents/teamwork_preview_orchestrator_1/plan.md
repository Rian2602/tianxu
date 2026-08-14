# Plan: Tian Xu: Second Life Roadmap Generation

## Objective
Analyze the codebase and documentation of Tian Xu: Second Life, identify completed vs. missing Fase 1 requirements, and create a comprehensive, prioritized, actionable Subagent-Driven Development (SDD) roadmap at `docs/superpowers/plans/next-roadmap.md`.

## Steps
1. **Phase 1: Multi-angle Survey & Exploration**
   - Explorer 1 (`teamwork_preview_explorer`): Codebase inventory (src/engine/, src/loader.py, src/cli.py, web/, data/, tests/, tools/validate_data.py). Map existing functionality and current test status.
   - Explorer 2 (`teamwork_preview_spec_miner`): Documentation & Spec Mining (docs/GDD.md, docs/DESIGN_SUMMARY.md, docs/STORY_FASE1.md, docs/ENGINE_ARCHITECTURE.md). Enumerate all Fase 1 required features, systems, and content.
   - Explorer 3 (`teamwork_preview_explorer`): Gap & Dependency Analysis. Cross-reference implementation with specs to identify unimplemented/partially implemented features, broken contracts, and structural dependencies.

2. **Phase 2: Synthesis & PROJECT.md Update**
   - Synthesize findings from Explorers into a structured gap matrix and architecture index.
   - Record in `PROJECT.md` and update orchestrator state.

3. **Phase 3: Authoring SDD Roadmap Document**
   - Dispatch Worker (`teamwork_preview_worker`) to author `docs/superpowers/plans/next-roadmap.md` with:
     - Executive summary & current state breakdown
     - Prioritized epics and tasks (P0, P1, P2)
     - SDD Task Specifications (Task ID, Title, Priority, Motivation, Files to modify/create, Detailed Specs, Test/Validation plan, Acceptance Criteria)
     - Dependency graph and execution sequence
     - Subagent prompt templates and SDD workflow guidance

4. **Phase 4: Review, Challenge & Forensic Audit Gate**
   - Dispatch 2 Reviewers (`teamwork_preview_reviewer`) to verify accuracy against codebase and docs, and verify actionable SDD format.
   - Dispatch 2 Challengers (`teamwork_preview_challenger`) to stress-test roadmap feasibility, completeness against docs, and dependency consistency.
   - Dispatch 1 Forensic Auditor (`teamwork_preview_auditor`) for authenticity and integrity check.
   - Evaluate gate criteria in `GATE_STATUS.md`.

5. **Phase 5: Final Report to Parent**
   - Synthesize all findings and report completed roadmap back to Sentinel.
