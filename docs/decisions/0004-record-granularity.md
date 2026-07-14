# ADR-0004 — Record granularity: event vs. session

**Status:** Accepted
**Date:** 2026-07-13

## Context

Overtime has no independent existence — it only ever follows a completed Pomodoro. A
separate overtime row is meaningless without the row it belongs to. Once labels arrive
(US-6), a label would have to be attached to both rows and kept in sync.

The question is not which schema is prettier, but **which questions the database will be
asked**:
- "How many Pomodoros on 13 July?"
- "How much overtime per Pomodoro on average?"
- "Plot the day as a stacked timeline."

Each schema makes some of these a filter-plus-count and others a plain count.

## Options

**A — one row per event**

| timestamp | type | duration_min |
|---|---|---|
| 2026-07-13T12:30:00 | work | 25 |
| 2026-07-13T13:00:00 | overtime | 30 |

**B — one row per session**

| start | work_min | overtime_min |
|---|---|---|
| 2026-07-13T12:05:00 | 25 | 30 |

**C — one row per phase, with start and end (chosen)**

| type | start | end | duration_min |
|---|---|---|---|
| work | 2026-07-13T12:05:00 | 2026-07-13T12:30:00 | 25 |
| overtime | 2026-07-13T12:30:00 | 2026-07-13T13:00:00 | 30 |

## Decision

**One row per phase (event schema), with an explicit `type`, a `start`, an `end`, and
`duration_min`.** A `work` row is written the moment the standard duration is reached
(the WORK → WORK_OVERTIME switch, see STATES.md); if overtime follows, an `overtime` row
is appended when it ends. Both writes are pure appends — nothing is ever rewritten.

The two rows are deliberately **not linked**. The relationship between a Pomodoro and its
own overtime is information this project does not need: the target insight only asks *how
many* Pomodoros and *how much* overtime in total, never *which overtime belonged to which
Pomodoro*.

Each row stores both `end` and `duration_min`. When no pause occurred these are
redundant (`end = start + duration_min`); when a pause occurred they diverge — `end −
start` is the gross wall-clock span, `duration_min` is the net work. The redundancy is
accepted on purpose: keeping both lets us recover pause time (`gross − net`) as an
efficiency signal and place blocks correctly on the daily stack plot. The `type` column
is what lets analysis separate the two target figures; a later `label` (US-6) will attach
to individual rows.



## Consequences

- **Both target figures separate cleanly.** Pomodoros = count of `work` rows; overtime =
  sum of `duration_min` over `overtime` rows, converted to Pomodoro units at analysis
  time (ADR-0005). Neither figure is forced into the other.
- **The work/overtime boundary is stored, not derived.** Because the split lives in two
  rows, a later change of the standard duration (25 → 50 min) does not corrupt past data:
  old `work` rows stay one earned Pomodoro each, old `overtime` rows keep their recorded
  minutes. Only the *conversion to Pomodoro units* re-parameterises — exactly what
  ADR-0005 defers.
- **`end` and `duration_min` are intentionally redundant** when no pause occurred. The
  cost is one extra column; the gain is recoverable pause time and honest placement on
  the timeline under net ≠ gross.
- **Overtime is not linked to its parent Pomodoro.** Per-Pomodoro overtime analysis, or a
  single label spanning both rows, would need a `session_id` or a migration. Accepted
  because those are deferred (US-6); the daily balance needs no linkage.
- **Two writes per Pomodoro-with-overtime**, both pure appends. A crash *between* them
  loses only the un-acknowledged overtime — never the earned Pomodoro, which was already
  committed at the 25-minute mark.
