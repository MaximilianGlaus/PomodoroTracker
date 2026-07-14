# Requirements

## Constraints (non-functional)

- **C-1 Platform independence.** Low-friction use anywhere → the domain must not depend on
  any one interface. Resolved in ADR-0006: UI-agnostic domain behind a port, CLI as the
  first (disposable) adapter.

## V1 — Core

### US-1
As a user, I want to be called to a break after 25 minutes, so that I keep work and rest
cleanly separated.

**Acceptance criteria**
- After *start*, a visible timer counts down from 25:00 to 00:00.
- Elapse is signalled by sound **and** a changed interface.
- After elapse the timer counts up (OVERTIME) until the user acknowledges.
- The timer can be halted (PAUSED) and resumed by button press.
- BREAK behaves analogously: 5 min countdown, then OVERTIME until acknowledged.

### US-2
As a user, I want to actively acknowledge the end of a phase, so that extra work and
overrun breaks have a defined end point.

### US-3
As a user, I want to count completed Pomodoros, in order to measure my work output.

### US-4
As a user, I want completed phases to be persisted, so that later analysis is possible.

## Later

### US-5
Analysis and visualisation of recorded work (strategic level).

### US-6
Labels per Pomodoro, to make resource allocation transparent.
