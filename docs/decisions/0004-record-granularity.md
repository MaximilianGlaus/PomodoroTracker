# ADR-0004 — Record granularity: event vs. session

**Status:** Proposed
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

## Decision

*(in progress — Max)*

## Consequences

*(TODO — must address at least:)*
- Can the two figures of the target insight (Pomodoros **and** overtime) still be
  produced separately, or does the schema force them into one sum?
- What happens to existing data if the standard duration changes from 25 to 50 min?
- Is the start time available for the timeline plot, given net ≠ gross?
