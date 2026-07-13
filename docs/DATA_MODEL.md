# Data model

**Principle: store facts, compute metrics.** The database records *what happened*. The
analysis layer decides *how to read it*. Any interpretation baked into stored data
(Pomodoro length, rounding) becomes irreversible.

**Append-only.** Rows are only ever added, never modified. Rewriting a row means there
is a moment where the file is half-updated; a crash at that moment produces corrupt data
of unknown extent. Appending is atomic and trivial to implement.

## Current working shape — *subject to ADR-0004*

| Column | Example | Note |
|---|---|---|
| `timestamp` | `2026-07-13T12:30:00` | ISO 8601. Marks the **end** of the phase. |
| `type` | `work` / `overtime` | Meaning is stored, never inferred from the value. |
| `duration_min` | `25` | Raw minutes. No rounding, no Pomodoro conversion. |

Conversion to Pomodoros (`30 min → 1.2 → 1`) happens **in the analysis layer**, at query
time, with the standard duration as a parameter.

## Known consequence: no start time

Storing *end + duration* means the start time is not recoverable when a pause occurred
(net ≠ gross). A daily timeline plot will place a paused Pomodoro slightly wrong.
Accept deliberately, or add a `start` column — decide in ADR-0004.
