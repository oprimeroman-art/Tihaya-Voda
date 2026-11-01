---
title: Gameplay code map
summary: Verified repository areas that agents should inspect before changing the game experience.
code_paths: ["studio/**", "game-project/**", "game/**", "game-editor/**", "codex-scripts/**"]
---
# Code map

Based on the current root README, studio/ is the editable engine and event system; game-project/ is the exploded project and media; game/ and game-editor/ are browser output, while codex-scripts/ holds build and integration helpers.

Find the canonical source of the feature before editing packaged HTML. Check how working changes are propagated into game/ and game-editor/. The current synchronization command and exact runtime source of navigation have NOT been verified here; read project scripts and related existing docs before editing gameplay.
