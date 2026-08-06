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

- **Theirs:** application code — `core.py`, `gui_max.py`, `categories.py`, and future
  modules.
- **Yours on request:** documentation (ADRs, `PORT.md`, `README.md`) — they explicitly
  delegate doc-writing — plus build/config tooling and git plumbing.
- `gui_claude.py` is a reference scaffold written *for* them to compare against. The
  owner's own shell is `gui_max.py`; **do not overwrite it.**
- The agreed doc-writing process is: decision reached in chat → you draft in one pass →
  they review the diff. No live word-by-word co-writing — it wastes their time.

**Teach before you build.** Tooling is fair game to just do — *but only if they can read
the result afterwards*. Creating an artifact that introduces unfamiliar concepts and
explaining it after the fact does not work for them; they said so explicitly about the CI
workflow (`.github/workflows/tests.yml`, committed but deliberately not yet understood).
Name the concept, give keywords to look up, let them build it.

They sometimes leave `# @Claude ...` questions inline in the code — answer those when
encountered.

## Commands

- **Run the app (GUI):** `python3 gui_max.py` — the Tkinter desktop shell (owner's own
  implementation). Tkinter ships with Python; the app itself has no runtime dependencies.
  `gui_claude.py` is a reference scaffold for the same window.
  - **Storage-path safety.** Since the env-var + `sys.frozen` refactor, a source run
    (`python3 gui_max.py`) writes to `/tmp/pomodoro-dev/`, **not** the owner's real
    Library folder — the bundled `.app` keeps hitting `~/Library/Application
    Support/PomodoroTracker/`. Every launch prints the resolved path (`[path] ...`); read
    it before pressing Start. To point a source run at any other directory, set
    `POMODORO_DATA_DIR=/some/path python3 gui_max.py` — inline only, never in `~/.zshrc`.
- **Run the core's CLI harness:** `python3 core.py` — `main()` is a throwaway
  command-driven loop, guarded by `if __name__ == "__main__"` so `import core` does *not*
  run it. Handy for exercising the state machine without the GUI.
- **Tests:** `.venv/bin/python -m pytest -v`, or a single one with
  `.venv/bin/python -m pytest test_core.py::test_paused_time_does_not_accure -v`.
- **Environment:** a `.venv` exists; dev tooling (pytest, pyinstaller) is pinned in
  `requirements-dev.txt`. The owner has repeatedly fallen back to the Anaconda interpreter
  (`/Users/max/anaconda3/bin/python`) — if pytest "isn't installed", that is why. Use
  `.venv/bin/python` explicitly to avoid the trap.
- **Build the macOS app:** `pyinstaller --windowed --name PomodoroTracker --icon
  icon/PomodoroTracker.icns gui_max.py` (from inside the venv). Build from the venv, never
  Anaconda — Anaconda drags numpy/MKL in and the bundle balloons from ~26 MB to ~250 MB.

## Architecture

**Documentation is the source of truth, not the code.** The design was deliberately
front-loaded before any code. Read these before changing behaviour or design:

- `docs/decisions/` — ADRs 0001–0009. Immutable decisions *with their reasoning*. If a
  change contradicts an ADR, that ADR must be superseded by a new one, not silently
  broken. `docs/decisions/README.md` explains the format and the rule that a "no
  drawbacks" Consequences section means the thinking wasn't sharp enough. Latest:
  **0009** — labels use surrogate keys so a rename never touches the append-only session
  log.
- `docs/PORT.md` — the **contract** between core and shell (living doc, kept current).
- `docs/PRD.md` — the v0.2.0 product spec (categories + LLM weekly summary).
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
  shell sends **commands** in (`start`, `pause`, `resume`, `acknowledge`, `abort`,
  `set_category_id`) and reads `state` / `remaining_seconds` back out. Per ADR-0007 all
  presentation lives in the shell (`format_time` turns signed seconds into `mm:ss` /
  overtime); the beep is edge-detected in the shell by comparing `state` to the previous
  frame (the core has no event system yet).
- `categories.py` (`CategoryStore`, `Category` dataclass) is a **second domain module**
  beside `core`. It owns the label vocabulary — create/rename/merge/resolve — and
  persists as JSON, not CSV: JSON preserves types (int ids, `null` for `merged_into`) and
  matches the "small mutable structured data" shape. `sessions.csv` stays append-only;
  `category_storage.json` is mutable reference data (ADR-0009). Deletion is modelled as a
  **merge with a forwarding pointer** — no session row is ever rewritten. `resolve()`
  follows the chain; `CircularMergeError` guards both ends. Core stores an opaque
  `category_id` verbatim on each row — it never imports `categories`.

**Load-bearing invariants** (breaking these silently corrupts the product's premise):

- **Store facts, compute metrics (ADR-0005/0004).** Rows hold raw seconds and wall-clock
  `start`/`end` (ISO `datetime`); conversion to Pomodoro units and rounding happen only at
  analysis time, with the standard duration as a parameter. Never bake Pomodoro counts or
  rounding into stored data. Storage is **append-only** — rows appended via
  `csv.DictWriter` (`type,start,end,duration_sec`), never rewritten. `_save_csv` writes the
  header itself when the file is absent, so the store is self-healing; keep that check
  *before* the `open(..., "a")`, since append mode creates the file.
- **Platform knowledge lives in the shell, never the core.** The core *receives* its
  `storage_path` as a constructor argument — and it's a **directory**, not a file:
  `PomodoroTracker` appends `"sessions.csv"` inside `__init__`, `CategoryStore` appends
  `"category_storage.json"`. `gui_max._compute_storage_path` is the only code that knows
  about macOS and about environments. It uses a **three-layer decision**: (1) env var
  `POMODORO_DATA_DIR` if set → use it; (2) else if `getattr(sys, "frozen", False)` → the
  Library folder (packaged `.app`); (3) else `/tmp/pomodoro-dev/` (source run). Bundled
  binary can never accidentally run in dev mode; source can never accidentally hit prod.
  Never hardcode a platform path into `core.py` or `categories.py`.
- **The current-category slot never clears via any state transition** — only
  `set_category_id` writes it. The slot's value at row-save moment is what lands in that
  row, which is why the same id flows through both the `work` row (saved on
  `work → work_overtime` transition) and the `work_overtime` row (saved on
  `acknowledge` / `abort`). Do not add "clear on abort" or "clear on acknowledge"
  cleverness — it would silently drop the label from the second row of every session.
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
gets a disposable directory and never touches the owner's real history. An `advance(tracker,
n)` helper factors out the `for _ in range(n): now_monotonic += 1; tick()` loop noise — use
it for any test that walks the clock.

`test_categories.py` follows the same pattern with `tmp_path` and covers the JSON
round-trip (save → fresh store → load, merge pointer preserved, id counter restored).
`test_gui.py` exists but is thin — GUI code is hard to unit-test; prefer running the app
manually through a click checklist for widget layer changes.

**Testing philosophy in this repo:** DAMP over DRY. Extract the Arrange (fixtures, helpers
like `advance`) so it has a *name* that documents what it sets up. Keep the Act and Assert
explicit inline — a failing test should read as one story without jumping to helpers. Rule
of thumb: the third time you paste the same setup block, extract it.

## Current status

**Active branch:** `feat/category-labels` (v0.2.0-dev). `v0.1.1` is the last tagged
release — `v0.1.0` shipped as a `.app`, `v0.1.1` fixed an `abort`-during-overtime bug
where the row was silently never saved. Repo is **public** at
`github.com/MaximilianGlaus/PomodoroTracker`, CI runs on every push (`.github/workflows/tests.yml`).

**On the branch (foundation for v0.2.0):**

- `categories.py` — `CategoryStore` with JSON persistence, merge/resolve, cycle guard.
- `core.py` — `set_category_id`, `category_id` column, slot flows through phase saves.
- `gui_max.py` — three-layer storage-path decision (env var / `sys.frozen` / dev path).
- Test suite: 25 green (core + categories + a thin GUI test).
- ADR-0009 records the surrogate-key decision. PR open on GitHub.

**Not yet built:** the GUI category picker (Combobox + "New…" button) — the label
feature is not user-facing until this lands. Then the LLM weekly-summary integration
(Phase-1 milestone per the roadmap).

**Deferred / known rough edges:**

- `save_categories` is not atomic — mid-write crash can truncate the file. Fix is a
  temp-file-plus-`os.replace` pattern; do it next time the method is touched. Note in
  `BACKLOG.md`.
- `docs/DATA_MODEL.md` and `docs/STATES.md` predate the `category_id` column and haven't
  been updated. Draft that when the picker lands.
- Splitting `paused` into a separate "clock running" flag instead of a state — still
  planned, `_effective_state()` is the seam that keeps it cheap.
- `analysis.py` was deferred (see D-0002 in the Administration roadmap): the tracker
  itself is the Phase-1 vehicle now, and the analysis surface will be a category-aware
  burn-up chart built after the LLM summary work.
- `STATES.md` says break can be paused but the Mermaid diagram lacks that transition.
