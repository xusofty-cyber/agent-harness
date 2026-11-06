# Proposal — Dependency modelling for feature-list items

Status: **accepted and implemented** (2026-11-06). Owner ruling:
start semantics = **graded**: hard-block (iii) by default, with the
(ii) audit trail as a logged exception path — `--override-deps
"<reason>"` starts the item and records a `dependency_override`
event. (Owner's criterion, clarified the same day: flexibility — he
delegated the mechanism choice; the graded form is the
maintainer's pick under that criterion. The first
implementation's pure-(iii) reading was superseded.) Recorded as
DECISIONS.md D72; implemented in gate/pass-gate.py + schema +
tests/pass_gate_deps_test.py.
Origin: cross-audit with the course validator (2026-11-06)
confirmed `gate/feature_list.schema.json` has no dependency field;
items that secretly depend on each other are today coordinated
only by prose in titles/notes.

## Design (schema part — uncontroversial)

- Optional `depends_on`: array of item ids on each item.
- Validation (pass-gate `validate` + repo_checks): every id must
  exist; the graph must be acyclic. Existing items migrate
  untouched (absent = no dependencies).
- `status` output annotates items whose dependencies are not all
  `passing` ("blocked-by: <ids>", display only).

## Decision required — what `start` does with unmet dependencies

| Option | Behaviour | Trade-off |
|---|---|---|
| (i) Record-only | Nothing enforces; deps are documentation | Zero friction; the field can silently rot like prose does |
| (ii) Warn-first (**recommended**) | `start` prints unmet deps and requires an explicit `--override-deps`, logged as a gate event with the reason | Friction only at the moment of risk; the event log keeps overrides auditable; can be promoted to (iii) after a release of evidence |
| (iii) Hard-block | `start` refuses until deps are `passing` | Strongest guarantee; can deadlock legitimate reordering and historical dogfood items |

Recommendation: adopt (ii) now, revisit (iii) with data. WIP=1
already limits blast radius; the marginal value of (iii) over
(ii) is unproven — the same evidence-first posture as D69.

## Adoption path if accepted

1. Record the ruling as a new DECISIONS.md entry.
2. Schema + validate + status annotation; unit tests for cycle
   detection and the override event.
3. Backfill `depends_on` for the repo's own 6 items where a real
   dependency exists (expected: few or none — that is a finding,
   not a failure).
