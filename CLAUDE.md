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
they explicitly delegate doc-writing. Application code (`core.py`, `gui_max.py`, future
modules) is theirs to write. `gui_claude.py` is a reference scaffold written *for* them to
compare against — the owner's own shell is `gui_max.py`; do not overwrite it.

## Commands

- **Run the app (GUI):** `python3 gui_max.py` — the Tkinter desktop shell (owner's own
  implementation, in progress). Tkinter ships with Python; no dependencies, no build step.
  `gui_claude.py` is the reference scaffold for the same window.
- **Run the core's CLI harness:** `python3 core.py` — `main()` is a throwaway
  command-driven loop, guarded by `if __name__ == "__main__"` so `import core` does *not*
  run it. Handy for exercising the state machine without the GUI.
- **Tests:** none yet. The core is testable *without real time*: it reads the clock only in
  `update_time()` (sets `self.now_monotonic` / `self.now_datetime`); a test can set those
  directly and assert on `state` / `remaining_seconds` with no `sleep`.
- Durations in `core.py` are shortened for testing (`pomodoro_length_sec = 14`,
  `break_length_sec = 5`); real use is `25 * 60` / `5 * 60`.

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

- `core.py` (`PomodoroTracker`) is the **domain**: the state machine, timer math, Pomodoro
  rules, and CSV persistence. It must **never** `print`, read `input`, `sleep`, or own a
  loop. It reads the real clock only through the single `update_time()` seam
  (`time.monotonic()` + `datetime.now()`), which the shell calls each cycle; all timer math
  derives from the stored `self.now_monotonic` / `self.now_datetime`. Keep clock reads
  funnelled through that one method so the core stays fake-clock testable.
- The **shell/adapter** is a Tkinter GUI (`gui_max.py`, scaffold in `gui_claude.py`). It
  owns all I/O and the loop — but the loop is the *framework's*: `root.after(1000,
  self._heartbeat)` re-schedules a heartbeat that runs `update_time()` + `tick()` + re-render
  once a second (no threads, no `sleep`, no hand-written `while`). The core is **passive** —
  it computes only when the shell calls it, so the `after` interval is the throttle. The
  shell sends **commands** in (`start`, `pause`, `resume`, `acknowledge`, `abort`) and reads
  `state` / `remaining_seconds` back out. Per ADR-0007 all presentation lives in the shell
  (`format_time` turns signed seconds into `mm:ss` / overtime); the beep is edge-detected in
  the shell by comparing `state` to the previous frame (the core has no event system yet).

**Load-bearing invariants** (breaking these silently corrupts the product's premise):

- **Store facts, compute metrics (ADR-0005/0004).** Rows hold raw seconds and wall-clock
  `start`/`end` (ISO `datetime`); conversion to Pomodoro units and rounding happen only at
  analysis time, with the standard duration as a parameter. Never bake Pomodoro counts or
  rounding into stored data. Storage is **append-only** — rows appended to
  `session_storage.csv` (`type,start,end,duration_sec`), never rewritten.
- **Net ≠ gross.** A pause shifts *when* the timer finishes, not *what* is recorded.
  `resume` implements this by pushing `end_monotonic` forward by the paused duration.
- **Two time concepts.** `time.monotonic()` measures the countdown (a stopwatch — only
  differences are meaningful); `datetime.now()` stamps the calendar `start`/`end` in stored
  rows. Both are read together in `update_time()`.
- A Pomodoro is committed at the moment the standard duration is reached (the
  `work → work_overtime` transition), so a crash after that point doesn't lose it.

## Current status

Working end-to-end: core state machine, CSV persistence (`save_session` appends rows;
`abort` from overtime now stores the earned Pomodoro), and a Tkinter GUI with a live
`after`-driven countdown and an overtime beep. **In progress:** `gui_max.py` — the owner is
building the shell themselves; treat it as their code and mentor rather than rewrite.
**Owed:** an ADR recording the pivot to a Tkinter GUI as the v1 interface (ADR-0006 chose
"CLI first, behind a UI-agnostic domain" — the domain-agnostic part still holds, only the
chosen adapter changed). **Rough/open:** the `paused` live display, the sub-minute overtime
rule (still `TODO` in `GLOSSARY.md`), and the CSV header is not managed by code.
