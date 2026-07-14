# ADR-0007 — The core emits facts, the shell chooses presentation

**Status:** Accepted
**Date:** 2026-07-14

## Context

When designing the port's outbound events (see PORT.md), each event could carry either a
finished, human-readable string — e.g. `"Pomodoro stored (25 min)"` — or structured data
— e.g. `type=work, duration_min=25`. A single generic "message" channel from core to
shell was also considered as a convenience.

The core must remain ignorant of any interface (ADR-0006). A string like "Pomodoro
stored" is already a *presentation* choice: wording, language, and the assumption that
the interface even shows text (a GUI might flash green or draw an icon instead).

## Options

- **Core emits ready-made message strings** (incl. a generic `message` channel). Cheapest
  to wire for the first CLI.
- **Core emits structured, named events with data**; the shell maps each to text / colour
  / sound.

## Decision

The core emits **structured, named events carrying data**, never finished UI text. All
wording and formatting live in the shell — including turning `tick` seconds into `mm:ss`.
The generic `message` channel is rejected.

## Consequences

- **The shell owns a small presentation mapping** (one rule per event: "on `phase_stored`,
  print `Pomodoro stored (N min)`"). That is exactly where UI wording belongs, and it is
  what makes a different adapter able to present the same fact differently.
- **No string parsing.** The shell is handed `duration_min = 25`, never asked to dig `25`
  back out of a sentence it received.
- **Adding a user-facing string touches only the shell**, not the core.
- **Cost: a genuinely new event type touches two places** — the core must emit it and each
  shell must learn to present it. Accepted: that is the price of keeping presentation out
  of the core, and it is paid only when the *contract* grows, not when wording changes.
- A generic "message" channel would have been quicker for the first CLI; we forgo that
  convenience on purpose to stop the core from ever dictating UI text.
