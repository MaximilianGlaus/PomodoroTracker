# State machine

```mermaid
stateDiagram-v2
    [*] --> INACTIVE
    INACTIVE --> WORK: start
    WORK --> PAUSED: pause
    PAUSED --> WORK: resume
    WORK --> INACTIVE: abort (discarded)
    WORK --> WORK_OVERTIME: 25 min elapsed<br/>(sound + prompt)
    WORK_OVERTIME --> BREAK: acknowledge
    WORK_OVERTIME --> INACTIVE: abort (measurement ended + stored)
    BREAK --> BREAK_OVERTIME: 5 min elapsed<br/>(sound + prompt)
    BREAK --> WORK: acknowledge
    BREAK_OVERTIME --> WORK: acknowledge
    BREAK --> INACTIVE: abort
    BREAK_OVERTIME --> INACTIVE: abort
```

## Rules

- A Pomodoro counts **only on completion** of the standard duration.
- Abort from WORK or BREAK → the in-progress phase is discarded.
- Abort from WORK_OVERTIME → the measurement is **ended and stored** (the Pomodoro has
  already been earned).
- **BREAK and BREAK_OVERTIME are display states only.** Break time is shown live so the
  user can see an overrun happening, but it is never persisted. Consequently no timeout
  or cutoff rule is needed — a break left running overnight simply produces no data.
- INACTIVE is the start and rest state; nothing is tracked here.

## Open points

- [ ] Can the timer be PAUSED during BREAK? (Decide deliberately, do not just omit.)
- [ ] Behaviour on crash / app closed with a timer running.
