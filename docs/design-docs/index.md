# Design docs — index

Design and decision records for agent-harness.

| Document | Status | Notes |
|---|---|---|
| `DECISIONS.md` (repo root) | living | The decision log of record, D1–D71. Append-only: a superseded decision keeps its text and gains an inline supersession note naming the decision that replaced it (e.g. the D3/D19 FR/DE freeze, superseded by D27). |
| `core-beliefs.md` (this directory) | accepted | The small set of operating beliefs the detailed rules implement. |
| `docs/internal/PROJECT_CONTEXT.md` | living | Project panorama and long-term facts for this repo. |
| `ARCHITECTURE.md` (repo root) | living | Top-level component map and hard dependency rules. |

Status vocabulary: `accepted` (in force), `proposed` (under
discussion), `deprecated` (kept for history, no longer in force).
A decision recorded as DEFERRED is debt, and is mirrored in
`docs/exec-plans/tech-debt-tracker.md` with its re-trigger
condition.
