# Port — the contract between core and shell

*Living document. Unlike an ADR, this is kept current: when the contract grows, edit it
here. The **reasoning** behind its shape lives in the ADRs (see references below).*

The **core** (domain: state machine, timer, the rule for what counts as a Pomodoro,
writing rows) exposes exactly this contract and nothing else. The **shell** (adapter:
CLI now, GUI/Web later) depends on the core; the core knows nothing about the shell. The
dependency points one way — inward. See ADR-0006.

The contract has two halves: **commands** flow in (shell → core), **events** flow out
(core → shell).

## Commands in (shell → core)

The shell sends the raw user intent. It never decides what the command *means* — the core
interprets it against the current state.

| Command | Meaning | Note |
|---|---|---|
| `start` | Begin a WORK phase from INACTIVE. | |
| `pause` | Halt the running timer (net accounting: pausing shifts *when* it finishes, not *what* is recorded). | |
| `resume` | Continue a paused timer. | |
| `acknowledge` | Confirm the end of the current phase. | State-dependent: after work → start a break; after break → start work. The **core** decides which. |
| `abort` | End the current phase early. | State-dependent: from WORK the phase is **discarded**; from WORK_OVERTIME the overtime is **ended and stored** (the Pomodoro was already earned). The **core** decides which. |

The shell must contain no logic like *"if in overtime, store first, then abort"* — that
lives in the core. The shell stays dumb.

## Events out (core → shell)

The core announces **facts**, as structured data. The shell decides how to present them
(text, colour, sound, a shrinking ring). See ADR-0007.

| Event | Data | The shell uses it to… |
|---|---|---|
| `state_changed` | `new_state` (INACTIVE, WORK, PAUSED, WORK_OVERTIME, BREAK, BREAK_OVERTIME) | Pick which screen to render. Its *change* to an OVERTIME state is also what triggers the beep + changed interface — there is **no separate "phase elapsed" event**. |
| `tick` | `seconds` | Show the running number. **Seconds, not a formatted string** — the shell formats to `mm:ss` or a ring. Direction is implied by the state (WORK counts down, OVERTIME counts up). |
| `phase_stored` | `type` (`work` / `overtime`), `duration_min` | Confirm the save and/or bump the day's counter. Explicit — so the shell never has to *infer* a save from which transition happened. |

## Principles (why the contract has this shape)

- **Push, not poll.** The core announces changes the instant they happen; the shell does
  not sit in a loop asking. This keeps a future GUI possible. (ADR-0006)
- **Facts, not presentation.** The core never sends finished UI strings; it sends data,
  the shell writes the words. No generic "message" channel. (ADR-0007)
- **Single source of truth.** The core owns state, time and the standard duration
  (25 → 50 is a core change). The shell keeps no copy of the truth — it mirrors what it is
  told, so the two cannot drift.

## Not yet in the contract (expected to grow)

- A `label` on a Pomodoro (US-6) — will add a command and/or extend `phase_stored`.
- An event for a rejected/invalid command, once we decide whether the shell can even
  issue one.
