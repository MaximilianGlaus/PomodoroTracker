# Architecture Decision Records

One file per decision, numbered sequentially, immutable. A superseded ADR is not
deleted — it is marked *Superseded by ADR-XXXX* and left in place. The value is not the
decision itself but the **reasoning**: in six months someone asks "why is aborted work
discarded?" and reads ADR-0001 instead of guessing.

## Format

```
# ADR-XXXX — Title

**Status:** Proposed | Accepted | Superseded by ADR-YYYY
**Date:** YYYY-MM-DD

## Context
What problem forced a decision? What was true at the time?

## Options
What was considered? (At least two, honestly stated.)

## Decision
What was chosen?

## Consequences
What does this cost? What becomes harder? What is now impossible?
```

**The Consequences section is mandatory.** If it says "no drawbacks", the thinking
wasn't sharp enough.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-discard-aborted-pomodoros.md) | Aborted Pomodoros are discarded | Accepted |
| [0002](0002-do-not-track-inactive.md) | Time in INACTIVE is not tracked | Accepted |
| [0003](0003-phase-records-not-event-log.md) | Phase records instead of a full event log | Accepted |
| [0004](0004-record-granularity.md) | Record granularity: event vs. session | **Proposed** |
| [0005](0005-round-at-analysis-time.md) | Round at analysis time, not at storage time | Accepted |
| [0006](0006-first-interface-cli.md) | First interface: CLI, behind a UI-agnostic domain | Accepted |
