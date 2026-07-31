# ADR-0009 — Labels are referenced by surrogate key

**Status:** Accepted
**Date:** 2026-07-31

## Context

It was decided that a separate **Analysis Core** should be introduced to support the
future analysis functionality of the application.

As a first step towards this, Pomodoro sessions need to be associated with a user-defined
label/category. Several approaches were considered, including hardcoding a fixed set of
labels and introducing identifiers for dynamically created labels.

## Options

- **Hardcoded labels** — fixed set of predefined labels in the application.
- **Label name stored directly in the session row** — simple and self-describing, but a
  rename would require rewriting history, which the append-only store forbids.
- **Surrogate keys** — dynamically created labels are assigned a unique identifier, which
  is stored alongside the label information.

## Decision

Surrogate keys were decided upon.

Each label will receive a unique identifier that is used to reference it from Pomodoro
sessions. The label's human-readable name can therefore be changed without changing the
historical session data associated with it.

The introduction of identifiers requires a separate storage file for label information.
That file is **reference data, not an event log**: unlike `sessions.csv` it is mutable and
may be rewritten in place. The append-only rule of ADR-0003/ADR-0005 governs records of
things that happened, not the vocabulary used to describe them.

If a label is deleted, the application must ask the user where the sessions previously
associated with that label should be attributed. The reassignment is recorded in the label
storage as a forwarding pointer on the deleted label — the label row is marked deleted and
carries the identifier it was merged into (a *tombstone with forwarding*). Analysis
resolves the pointer at read time. No session record is ever modified.

## Consequences

- Labels can be created dynamically by the user.
- Labels can be renamed without modifying historical Pomodoro records.
- Pomodoro records reference labels through stable identifiers.
- Deleting a label requires an explicit reassignment decision from the user, and costs one
  write to the label file — never a rewrite of session history.
- The design provides a foundation for the planned **Analysis Core**.

What it costs:

- **`sessions.csv` stops being self-describing.** A row now reads `category_id=3`, which
  means nothing without the second file. Readability of the raw data has been traded for
  renameability; anyone inspecting the store by hand needs both files.
- **Nothing enforces referential integrity.** A real database would reject a session
  referencing a label that does not exist. Two CSV files can drift apart, and only
  application code stands between the store and a dangling reference. No check for this
  currently exists.
- **Every reader now needs a join.** Analysis cannot work from `sessions.csv` alone — it
  must load the label file and resolve identifiers before it can aggregate anything.
- **Mutable storage enters a design that was uniformly append-only.** The simple rule
  "nothing in this app ever rewrites a file" no longer holds, and the distinction between
  the two kinds of storage must be understood before either is touched.
- **Forwarding pointers form chains, and chains can form cycles.** Resolution must follow
  A → B → C and must terminate if a cycle is ever created. Preventing or detecting that is
  now application responsibility. *(Mechanism not yet decided.)*
- **The GUI grows a category-management surface** — create, rename, delete-with-
  reassignment. That is new shell work with its own error states, not merely an extra
  input field.

## Notes

The pattern is the CSV equivalent of a foreign key relationship. If storage later moves to
SQLite (roadmap Phase 2), this maps directly onto a `categories` table with a
`FOREIGN KEY` constraint — which would enforce in the database the integrity that
application code has to guarantee here.
