# Pomodoro Tracker

**Thesis:** A timer that simply stops at zero lies about my day. I want to measure what
actually happened — not what was planned.

A Pomodoro timer that persists completed intervals and makes them analysable. The core
mechanism is **active acknowledgement**: the end of a phase must be confirmed by the
user. Whoever is in flow and keeps working gets credited for the extra time; whoever
overruns a break sees it happen. The goal is an honest daily balance, not a
disciplinary tool.

**Target insight (what the analysis must produce):**

> *24 June: 17 completed Pomodoros, +2 Pomodoros of overtime.*

Every feature must justify itself against this thesis.

## Documentation

| Document | Purpose |
|---|---|
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Ubiquitous language — one term, one meaning |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | User stories, acceptance criteria, constraints |
| [docs/STATES.md](docs/STATES.md) | State machine |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Storage schema |
| [docs/PORT.md](docs/PORT.md) | Contract between core and shell (commands in, events out) |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records |
| [docs/BACKLOG.md](docs/BACKLOG.md) | What's next |

## Running it

Requires Python 3.11+ and nothing else — the app is pure standard library
(Tkinter ships with Python).

```bash
python3 gui_max.py     # the desktop app
python3 -m pytest -v   # the test suite (needs pytest)
```

Completed phases are appended to `~/Library/Application Support/PomodoroTracker/sessions.csv`
(`type,start,end,duration_sec`) — never rewritten, see [docs/DATA_MODEL.md](docs/DATA_MODEL.md).

## Status

**v0.1.0 — working and in daily use.** Tkinter desktop app with a live countdown,
overtime beep and append-only CSV persistence, bundled as a macOS `.app` with
PyInstaller. The domain (`core.py`) is UI-agnostic and covered by a pytest suite
that drives it with a fake clock — no `sleep`, no real time.

**Next:** analysis and visualisation of the recorded data (the target insight above);
splitting the paused state into a separate "clock running" flag (see
[docs/BACKLOG.md](docs/BACKLOG.md)).
