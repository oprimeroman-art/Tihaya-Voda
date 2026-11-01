# byGagarin — instructions for every coding agent

1. Start with docs/README.md, docs/INDEX.md, docs/ops/PROJECT_STATE.md and docs/ops/HANDOFF.md. Read other documentation selectively through the index.
2. Canonical instructions and skills live in .ai/. If your agent needs its own directory, run python3 scripts/ai_sync.py. Do not maintain divergent copies of skills.
3. Before editing source, run python3 scripts/ai_docs.py related PATH to discover related documentation. If none exists, consult the index and create a focused note only when needed.
4. Ship an actual playable improvement or functioning change before polishing or creating reports. Never substitute audits, plans or graphics for implementation.
5. Do not touch published game or production branches without an explicitly authorized release task. Prefer a working branch and preserve existing saves, assets and history.
6. After implementation, run one targeted smoke test, update directly affected docs, regenerate the index and write a factual docs/ops/HANDOFF.md. Do not claim tests or deployments that were not done.
7. Be terse when reporting: what changed, where to inspect it, what remains broken.
