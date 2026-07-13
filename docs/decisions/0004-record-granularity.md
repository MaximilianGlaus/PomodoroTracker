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

Schema A with beginning anda end timestamp has been chosen. It has the advantage that it works with only appending, and we can save the work that has been done with the initial Pomodoro first and add anything afterwards to it. In the end, for me, I do not need a distinction between the two. The reason why we treat them separately is that the initial block just has to be done 25 minutes, more or less, at once. I mean, of course, allowing for unexpected pauses. But generally, it can't be a series of 10-minute sessions. And we have the overtime because we want to account for it and not have it being lost. So what we gain is the ability to have a point in time where we have accomplished the bits of work. But what I also decided is to have, to save start, starting point, end point, and duration. Because this gives us also some information about efficiency. So if it's being paused all the time, something that's interesting, and this way also the graphic, the stack, if I do a stack plot, it's something that we can consider, like, something that between starting and end point is where we can have the gain in working time.



## Consequences

*(TODO — must address at least:)*
- It does not allow the differentiation between the main worksession and overtime. However this is not needed as far as I can tell.
- Because we measure in minutes. The interpretation in pomodoros is not hardcoded into the data
- The distinction between net and gross time usage becomes possible.
