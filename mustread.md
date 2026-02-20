# MUST READ FIRST - Session Startup Protocol

Last Updated: 2026-02-20 12:06 UTC

## Mandatory Rule
Before starting any task in this project, every agent/session must read all project control documents.

## Required Read Order
1. `mustread.md` (this file)
2. `Agents.md`
3. `tasks.md`
4. `stack.md`
5. `journal.md`

## Mandatory Startup Checklist
- [ ] Read all files in required order.
- [ ] Identify current delivery phase from `tasks.md`.
- [ ] Review last journal entry in `journal.md`.
- [ ] Add a new journal entry marking session start.
- [ ] Confirm technical and testing rules from `Agents.md` and `stack.md`.
- [ ] Commit to unbiased and brutally honest technical guidance; challenge weak assumptions with explicit reasoning and alternatives.
- [ ] Confirm API-readiness requirements for external system integration.
- [ ] Confirm provisioning automation rule: offer selection must drive contract/subscriber handling automatically, with backend auto-detection for upgrade vs new-line and disambiguation handling.
- [ ] Confirm contract-first routing model is respected (new and existing client flows from contract tab) and subscriber-service compatibility is preserved.
- [ ] Confirm catalog service-component model is respected (Mobile/Internet/Landline with strict component rules and integer-hour quotas).
- [ ] Confirm current UI mode: single operator workflow and contract-first provisioning path.
- [ ] Confirm one-shot launchers (`launch_all.bat`, `launch_all.sh`) are still aligned with project structure.
- [ ] Confirm companion Linux stop script (`stop_all.sh`) is aligned with launcher PID/log conventions.
- [ ] Confirm launcher stale-process cleanup and post-launch smoke checks are still valid.
- [ ] Confirm phase foundation artifacts under `docs/` are aligned with current implementation.
- [ ] Confirm shared backend foundations under `backend/app/common/` remain consistent across services.
- [ ] Confirm active domain modules (`backend/app/models/`, `backend/app/services/`) align with `tasks.md` phase state.
- [ ] Confirm frontend domain screens in `frontend/src/App.tsx` align with current phase objectives.
- [ ] Only then begin implementation work.

## Mandatory Completion Checklist
- [ ] Review all project Markdown files in this order: `mustread.md`, `Agents.md`, `tasks.md`, `stack.md`, `journal.md`.
- [ ] Update all project Markdown files for the current interaction/iteration.
- [ ] Update `journal.md` with actual actions and results.
- [ ] Update `tasks.md` if task status changed.
- [ ] Ensure testing evidence is recorded.
- [ ] Ensure any architectural decision is documented.
- [ ] Verify that decisions in this iteration were reviewed critically (not accepted by default) and tradeoffs were stated.
- [ ] Validate deletion behavior against data-integrity policy (no destructive client deletion when financial/contract history exists).
- [ ] Ensure launchers (`launch_all.bat`, `launch_all.sh`) and stopper (`stop_all.sh`) remain valid after any structural or dependency change.

## Enforcement Note
This protocol is part of the project governance and must not be skipped.
Every interaction/iteration must leave synchronized updates across all project Markdown files.




