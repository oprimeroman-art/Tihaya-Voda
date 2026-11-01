---
title: Development workflow
summary: Small, game-first, multi-agent production cycle with explicit release boundary.
code_paths: []
---
# Workflow

Task -> relevant docs -> working code -> targeted check -> docs -> handoff -> review -> authorized release.

- Coordinator: selects one concrete task and prevents simultaneous edits to the same section.
- Developer: changes a working branch and produces a real artifact.
- Gameplay/content: checks that the change is meaningful to the player.
- Reviewer: checks the changed scenario and reports reproducible defects.
- Release guard: deploys only when authorized, checks the published game and records rollback steps.

These are roles, not running bots. One agent may perform multiple roles. Git commits and these docs, rather than chat memory, are the handoff contract.
