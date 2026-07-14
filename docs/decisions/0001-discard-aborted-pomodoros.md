# ADR-0001 — Aborted Pomodoros are discarded

**Status:** Accepted
**Date:** 2026-07-13

## Context

What counts as a "completed" Pomodoro? Does a session aborted after 6 minutes count?
The definition determines what every later analysis is built on.

## Options

- Discard entirely
- Count proportionally (e.g. 6/25 of a Pomodoro)
- Store separately as a fragment

## Decision

Discarded. A Pomodoro counts only once the standard duration is reached. In the future we might add a button that offers to end a pompodoro early.

## Consequences

- The user is incentivised to adhere to the minimum of 25 minutes.
- In order to avoid significant data loss a "end early button" might be introduced later

