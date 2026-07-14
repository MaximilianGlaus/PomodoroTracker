# ADR-0005 — Round at analysis time, not at storage time

**Status:** Accepted
**Date:** 2026-07-13

## Context

Three sessions with 10 minutes of overtime each. Rounded per row: 0.4 → 0, three times.
Daily total: **0**. Rounded once at day level: 1.2 → **1**. Rounding early destroys
information irrecoverably.

The same applies to the Pomodoro length itself: any pre-converted value stored in the
database would be invalidated the moment the standard duration changes.

## Options

- Store converted Pomodoro units
- Store raw minutes, convert on read

## Decision

Store raw minutes. Conversion and rounding happen in the analysis layer, with the
standard duration as a parameter.

## Consequences

Calculation in pompodoros happens during analysis, the computing burden seems neglegable.
