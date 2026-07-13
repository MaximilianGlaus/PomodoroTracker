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
| [docs/decisions/](docs/decisions/) | Architecture Decision Records |
| [docs/BACKLOG.md](docs/BACKLOG.md) | What's next |

## Status

Design phase. No code yet — by design.
