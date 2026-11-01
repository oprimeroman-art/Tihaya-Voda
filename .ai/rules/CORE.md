# byGagarin shared development rules

- Working result first: a game loop, a functional feature, or a reproducible build. Documentation supports delivery, not the other way around.
- Prefer the simplest working implementation; no new architecture unless the current one demonstrably blocks development.
- Protect existing game progress, scene content, media, and production builds.
- Facts, assumptions, and future work must be separated. A task or draft is not a finished feature.
- Maintain cross-agent context in docs/ops/PROJECT_STATE.md and docs/ops/HANDOFF.md. Do not ask the user to copy technical context between agent windows.
- If changes require publication, verify scope and current release policy first. A documentation update alone must not trigger a game release.
- Keep changes focused; report failures explicitly.
