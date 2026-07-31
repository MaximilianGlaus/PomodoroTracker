# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working style (read first)

**Use the `mentor-mode` skill for this repository.** It is the full statement of how to
work with the owner — the division of labour, the "predict before you check" and "teach it
back" habits, how to run and prioritise a review, and when to drop a parked concern. Load
it before doing anything substantial here. It lives in the owner's personal skills
directory (`~/.claude/skills/mentor-mode/`), so it is *not* checked into this repo; the
summary below is the fallback if it is unavailable.

The short version: the owner is learning software development and this is their first
substantial Python project. Treat them as an intern, you as the senior engineer. **Do not
write their application code and do not hand over finished solutions** — give the shape,
the principle, the failing case, then let them write it. Prefer hints over answers when
debugging. Push back when they skip documenting, deciding or justifying — but when they
park something, park it. German or English are both fine.

Project-specific division of labour:

- **Theirs:** application code — `core.py`, `gui_max.py`, `analysis.py` and future modules.
- **Yours on request:** documentation (ADRs, `PORT.md`, `README.md`) — they explicitly
  delegate doc-writing — plus build/config tooling and git plumbing.
- `gui_claude.py` is a reference scaffold written *for* them to compare against. The
  owner's own shell is `gui_max.py`; **do not overwrite it.**

**Teach before you build.** Tooling is fair game to just do — *but only if they can read
the result afterwards*. Creating an artifact that introduces unfamiliar concepts and
explaining it after the fact does not work for them; they said so explicitly about the CI
workflow (`.github/workflows/tests.yml`, committed but deliberately not yet understood).
Name the concept, give keywords to look up, let them build it.

They sometimes leave `# @Claude ...` questions inline in the code — answer those when
encountered.

## Commands

- **Run the app (GUI):** `python3 gui_max.py` — the Tkinter desktop shell (owner's own
  implementation). Tkinter ships with Python; the app itself has no dependencies.
  `gui_claude.py` is a reference scaffold for the same window.
- **Run the core's CLI harness:** `python3 core.py` — `main()` is a throwaway
  command-driven loop, guarded by `if __name__ == "__main__"` so `import core` does *not*
  run it. Handy for exercising the state machine without the GUI.
- **Tests:** `python3 -m pytest -v`, or a single one with
  `python3 -m pytest test_core.py::test_paused_time_does_not_accure -v`.
- **Environment:** a `.venv` exists; dev tooling (pytest, pyinstaller) is pinned in
  `requirements-dev.txt`. The owner has repeatedly fallen back to the Anaconda interpreter
  (`/Users/max/anaconda3/bin/python`) — if pytest "isn't installed", that is why.
- **Build the macOS app:** `pyinstaller --windowed --name PomodoroTracker --icon
  icon/PomodoroTracker.icns gui_max.py` (from inside the venv). Build from the venv, never
  Anaconda — Anaconda drags numpy/MKL in and the bundle balloons from ~26 MB to ~250 MB.

## Architecture

**Documentation is the source of truth, not the code.** The design was deliberately
front-loaded before any code. Read these before changing behaviour or design:

- `docs/decisions/` — ADRs 0001–0008. Immutable decisions *with their reasoning*. If a
  change contradicts an ADR, that ADR must be superseded by a new one, not silently
  broken. `docs/decisions/README.md` explains the format and the rule that a "no
  drawbacks" Consequences section means the thinking wasn't sharp enough.
- `docs/PORT.md` — the **contract** between core and shell (living doc, kept current).
- `docs/STATES.md`, `docs/DATA_MODEL.md`, `docs/GLOSSARY.md`, `docs/REQUIREMENTS.md`.

**Ports-and-adapters is the whole point (ADR-0006, adapter choice revised by ADR-0008).**
The domain must not depend on any interface:

- `core.py` (`PomodoroTracker`) is the **domain**: the state machine, timer math, Pomodoro
  rules, and CSV persistence. It must **never** `print`, read `input`, `sleep`, or own a
  loop. It reads the real clock only through the single `update_time()` seam
  (`time.monotonic()` + `datetime.now()`), which the shell calls each cycle; all timer math
  derives from the stored `self.now_monotonic` / `self.now_datetime`. Keep clock reads
  funnelled through that one method so the core stays fake-clock testable.
- The **shell/adapter** is a Tkinter GUI (`gui_max.py`, scaffold in `gui_claude.py`). It
  owns all I/O and the loop — but the loop is the *framework's*: `root.after(500,
  self._heartbeat)` re-schedules a heartbeat that runs `update_time()` + `tick()` + re-render
  twice a second (no threads, no `sleep`, no hand-written `while`). The interval is a
  deliberate shell-side choice, not a domain constant — the core is **passive** —
  it computes only when the shell calls it, so the `after` interval is the throttle. The
  shell sends **commands** in (`start`, `pause`, `resume`, `acknowledge`, `abort`) and reads
  `state` / `remaining_seconds` back out. Per ADR-0007 all presentation lives in the shell
  (`format_time` turns signed seconds into `mm:ss` / overtime); the beep is edge-detected in
  the shell by comparing `state` to the previous frame (the core has no event system yet).

**Load-bearing invariants** (breaking these silently corrupts the product's premise):

- **Store facts, compute metrics (ADR-0005/0004).** Rows hold raw seconds and wall-clock
  `start`/`end` (ISO `datetime`); conversion to Pomodoro units and rounding happen only at
  analysis time, with the standard duration as a parameter. Never bake Pomodoro counts or
  rounding into stored data. Storage is **append-only** — rows appended via
  `csv.DictWriter` (`type,start,end,duration_sec`), never rewritten. `_save_csv` writes the
  header itself when the file is absent, so the store is self-healing; keep that check
  *before* the `open(..., "a")`, since append mode creates the file.
- **Platform knowledge lives in the shell, never the core.** The core *receives* its
  `storage_path` as a constructor argument (dependency injection, same principle as the
  clock seam). `gui_max._compute_storage_path` is the only code that knows about macOS —
  it builds `~/Library/Application Support/PomodoroTracker/sessions.csv` and `mkdir`s the
  parent. The core's own default is a bare relative path, used only by the CLI harness and
  overridden in tests. Never hardcode a platform path into `core.py`.
- **Net ≠ gross.** A pause shifts *when* the timer finishes, not *what* is recorded.
  `resume` implements this by pushing `end_monotonic` forward by the paused duration.
- **Two time concepts.** `time.monotonic()` measures the countdown (a stopwatch — only
  differences are meaningful); `datetime.now()` stamps the calendar `start`/`end` in stored
  rows. Both are read together in `update_time()`.
- A Pomodoro is committed at the moment the standard duration is reached (the
  `work → work_overtime` transition), so a crash after that point doesn't lose it.
- **The clock must not advance while paused.** `tick()` returns early in `"paused"`;
  without that, `remaining = end - now` keeps growing and paused time is recorded as work.
- **`_effective_state()` answers "which phase am I really in?"** (returns `earlier_state`
  when paused). Anything *asking* about the phase — `acknowledge`, `abort`,
  `_calculate_duration_sec`, `_construct_dataline` — must go through it, or a phase ended
  while paused is stored with `type="paused"` and a stale duration. Anything *assigning*
  keeps plain `self.state = ...`. Half-applying this has caused real data corruption twice.

## Testing

`test_core.py` drives the core with a **fake clock**: set `now_monotonic` / `now_datetime`
directly and call `tick()`, never `update_time()` (that reads the real clock and makes
tests non-deterministic). No `sleep` anywhere — a full 25-minute Pomodoro plus overtime
runs in microseconds. The `tracker` fixture takes pytest's built-in `tmp_path` so each test
gets a disposable CSV and never touches the owner's real history.

Covered: initial state, `start`, elapse into overtime, the overtime→break acknowledge, the
overtime-drift regression, paused-time accounting, and a CSV round-trip. Not covered:
`abort`, the full break cycle, anything in the GUI.

## Current status

**v0.1.0 is tagged, packaged and in daily use.** Working end-to-end: core state machine,
CSV persistence, Tkinter GUI with an `after`-driven countdown and overtime beep, bundled
as a macOS `.app` via PyInstaller (~26 MB from the venv).

**Pending right now:** the repo has no remote yet — the owner has created a GitHub
repository and is connecting it (`git remote add origin …`, `git push -u origin main`,
`git push origin --tags`). A GitHub Actions workflow (`.github/workflows/tests.yml`) is
committed but has never run; the owner does not yet understand it and wants to learn
Actions/YAML before it goes live. Do not push on their behalf.

**Next up (agreed):** `analysis.py` — a third adapter that only *reads* the CSV, converting
raw seconds to Pomodoro units at read time (ADR-0005) to produce the target insight
("17 Pomodoros, +2 overtime"), plus a matplotlib chart with a target line at 15/day from
the owner's yearly plan. Then this project drops to maintenance and they move to the next
milestone of their learning roadmap (an LLM-API CLI tool).

**Deferred / known rough edges:** splitting `paused` into a separate "clock running" flag
instead of a state (planned 0.2.0 refactor — `_effective_state()` is the seam that makes it
cheap); the sub-minute overtime rule still `TODO` in `GLOSSARY.md`; `STATES.md` says break
can be paused but the Mermaid diagram lacks that transition.
