# Glossary

*Ubiquitous language: one term, one meaning — identical in conversation, code and UI.*

| Term | Meaning |
|---|---|
| **WORK** | Work phase, standard duration 25 min |
| **BREAK** | Recovery phase, standard duration 5 min |
| **OVERTIME** | Continued measurement after the standard duration elapses, until acknowledged |
| **PAUSED** | Timer temporarily halted (interruption, doorbell). *Not* to be confused with BREAK. |
| **Pomodoro** | A WORK phase that reached its full standard duration |
| **Abort** | Early termination. The in-progress Pomodoro is discarded. |

## Time accounting: net, not gross

PAUSED time is not counted as work. Pausing shifts *when* the timer finishes, but does
not change *what* is recorded.

> Example: a Pomodoro started at 12:00, paused 12:05–12:10, finishes at 12:30 — and is
> recorded as 25 minutes, not 30.

**Consequence to be aware of:** the start time cannot be reconstructed as
`end − duration` once a pause has occurred. See DATA_MODEL.md.

## Unit of evaluation: Pomodoros

Overtime is expressed in Pomodoro units (30 min = 1.2), using standard mathematical
rounding. Rounding happens **at analysis time, never at storage time** — see ADR-0005.

## Sub-minute rule

*(TODO — decide: is overtime below a threshold recorded at all? If not, state the
threshold here. Missing rows must be explainable a year from now.)*
