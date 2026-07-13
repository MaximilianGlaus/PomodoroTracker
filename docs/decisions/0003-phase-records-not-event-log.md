# ADR-0003 — Phase records instead of a full event log

**Status:** Accepted
**Date:** 2026-07-13

## Context

The insight sought is the daily balance ("17 Pomodoros, +2 overtime"), not forensic
reconstruction of the day. A full event log of every state transition would answer many
questions that are not being asked. YAGNI.

## Options

- Event log: every state transition with a timestamp
- One record per completed phase

## Decision

One record per completed phase.

## Consequences

- *(TODO: which later analyses become impossible? What would a migration cost if the
  answer turns out to be "I do want them"?)*
