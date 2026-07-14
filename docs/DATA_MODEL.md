# Data model

**Principle: store facts, compute metrics.** The database records *what happened*. The
analysis layer decides *how to read it*. Any interpretation baked into stored data
(Pomodoro length, rounding) becomes irreversible.

**Append-only.** Rows are only ever added, never modified. Rewriting a row means there
is a moment where the file is half-updated; a crash at that moment produces corrupt data
of unknown extent. Appending is atomic and trivial to implement.

## Schema — *decided in ADR-0004*

One row per completed phase. A `work` row is appended when the standard duration is
reached; an `overtime` row is appended when overtime ends. Rows are never linked or
rewritten.

| Column | Example | Note |
|---|---|---|
| `type` | `work` / `overtime` | Meaning is stored, never inferred from the value. |
| `start` | `2026-07-13T12:05:00` | ISO 8601. Beginning of the phase (wall clock). |
| `end` | `2026-07-13T12:30:00` | ISO 8601. End of the phase (wall clock). |
| `duration_min` | `25` | **Net** minutes worked. Raw — no rounding, no Pomodoro conversion. |

Conversion to Pomodoros (`30 min → 1.2 → 1`) happens **in the analysis layer**, at query
time, with the standard duration as a parameter.

## Net vs. gross is recoverable

`duration_min` is net work; `end − start` is the gross wall-clock span. When a pause
occurred the two diverge, and their difference is the pause time — kept deliberately as
an efficiency signal and to place blocks correctly on the daily stack plot. Storing both
is redundant only when nothing was paused; the redundancy is accepted on purpose
(ADR-0004).
