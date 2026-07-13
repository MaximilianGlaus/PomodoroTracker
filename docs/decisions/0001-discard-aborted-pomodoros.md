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

Discarded. A Pomodoro counts only once the standard duration is reached.

## Consequences

- The user is incentivised to adhere to the minimum of 25 minutes.
- *(TODO: data loss — 24 minutes of real work are recorded as nothing. This sits in
  tension with the honesty thesis. Name the tension and justify it.)*
- *(TODO: incentives cut both ways — a user who finishes a task at minute 22 will sit
  out the remaining three minutes to make the counter ring. The metric starts shaping
  the behaviour it measures. Harmless here; worth seeing.)*
