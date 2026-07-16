# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working style (read first)

The owner is learning software development; this is their first substantial Python
project. They want to be treated as an intern by a senior engineer: **do not write their
application code for them and do not hand over finished solutions.** Give context, ask
sharp questions, point out holes, name the principle behind a problem — then let them
solve it. Prefer hints over answers when debugging. Push back when they try to skip a step
(documenting, deciding, justifying). German or English are both fine.

Exception: **documentation** (ADRs, `PORT.md`, etc.) may be drafted for them on request —
they explicitly delegate doc-writing. Application code in `core.py` and future modules is
theirs to write.

## Commands

- **Run:** `python3 core.py` — pure standard library, no dependencies, no build step.
  `main()` is currently a throwaway test harness (a timed loop with a simulated pause), so
  running it prints a countdown and takes ~15 s because of real `time.sleep`.
- **Tests:** none yet. The core is designed to be testable *without* real time — `tick()`
  reads `self.now`, which the driver sets — so tests should inject fake `now` values and
  assert on `state`/`remaining_seconds` with no `sleep`.
- Durations in `core.py` are currently shortened for testing (`pomodoro_length_sec = 14`,
  `break_length_sec = 5`), not the real 25/5 minutes.

## Architecture

**Documentation is the source of truth, not the code.** The design was deliberately
front-loaded before any code. Read these before changing behaviour or design:

- `docs/decisions/` — ADRs 0001–0007. Immutable decisions *with their reasoning*. If a
  change contradicts an ADR, that ADR must be superseded by a new one, not silently
  broken. `docs/decisions/README.md` explains the format and the rule that a "no
  drawbacks" Consequences section means the thinking wasn't sharp enough.
- `docs/PORT.md` — the **contract** between core and shell (living doc, kept current).
- `docs/STATES.md`, `docs/DATA_MODEL.md`, `docs/GLOSSARY.md`, `docs/REQUIREMENTS.md`.

**Ports-and-adapters is the whole point (ADR-0006).** The domain must not depend on any
interface:

- `core.py` (`PomodoroTracker`) is the **domain**: the state machine, timer math, and
  Pomodoro rules. It must **never** `print`, read `input`, `sleep`, or own a loop. The one
  place still reading the real clock is `__init__` seeding `self.now`; all other time
  enters via `self.now`, set from outside.
- The **shell/driver** (currently `main()`, later a real CLI, then possibly GUI/Web) owns
  the loop, I/O, and `sleep`. It sends **commands** in (`start`, `pause`, `resume`,
  `acknowledge`, `abort`) and reads state back out. Per ADR-0007 the core emits **facts**
  (structured data), never presentation strings; the shell formats everything (including
  turning `remaining_seconds` into `mm:ss`).

**Load-bearing invariants** (breaking these silently corrupts the product's premise):

- **Store facts, compute metrics (ADR-0005/0004).** Persist raw minutes and wall-clock
  `start`/`end`; conversion to Pomodoro units and rounding happen only at analysis time,
  with the standard duration as a parameter. Never bake Pomodoro counts or rounding into
  stored data. Storage is **append-only** — rows are added, never rewritten.
- **Net ≠ gross.** A pause shifts *when* the timer finishes, not *what* is recorded.
  `resume` implements this by pushing `end_monotonic` forward by the paused duration.
- **Two time concepts.** `time.monotonic()` measures the countdown (a stopwatch — only
  differences are meaningful). Stored `start`/`end` need calendar time and will require
  `datetime` — not yet wired in.
- A Pomodoro is committed at the moment the standard duration is reached (the
  `work → work_overtime` transition), so a crash after that point doesn't lose it.

## Current status

Core state machine works and is committed. **Not yet built:** persistence (a `storage.py`
appending event rows per `DATA_MODEL.md`, plus `datetime` timestamps) and a real CLI shell
to replace the test-harness `main()`. `abort` from an overtime state should store the
earned Pomodoro but currently does not.
