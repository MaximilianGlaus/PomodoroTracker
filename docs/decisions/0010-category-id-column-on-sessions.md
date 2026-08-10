# ADR-0010 — `category_id` as a fifth column on `sessions.csv`

**Status:** Accepted
**Date:** 2026-08-10

## Context

ADR-0009 decided that labels are referenced by surrogate key, resolved through a
second file (`category_storage.json`), so that a rename never touches session
history. That ADR fixed the *reference mechanism*. It left open how the reference
actually lands in `sessions.csv`, which already had four columns
(`type,start,end,duration_sec`) and is append-only per ADR-0003/ADR-0005.

The store had 61 existing rows with no category information at all, written before
the label feature existed.

## Options

- **New column, appended at the end** (`type,start,end,duration_sec,category_id`) —
  existing rows read as short rows with a missing trailing field; new rows carry a
  value or an empty string for "uncategorised."
- **Separate CSV keyed by session** — session identity and category live in different
  files, joined by some session key. Rejected: sessions have no existing identity
  column to join on (rows are identified positionally by their `start`/`end`
  timestamps at best), so this would have required inventing an identifier the
  domain does not otherwise need.
- **Rewrite `sessions.csv` in place** to backfill a value for old rows. Rejected
  outright: ADR-0003/ADR-0005 make the file append-only; rewriting history to fit a
  new column would break the invariant the whole storage design rests on.

## Decision

`category_id` is a fifth column, appended to the end of the existing header order.
`core.py`'s `csv_fieldnames` tuple became
`("type", "start", "end", "duration_sec", "category_id")`, and `_construct_dataline`
writes `self.current_category_id` into it on every row (`core.py:30`, `core.py:128`).

The value is an opaque surrogate key from `categories.py` (or `None`) — `core.py`
never interprets it, never imports `categories`, and never validates it against the
category store. It writes whatever `set_category_id` was last called with, verbatim.

Old rows are **not** rewritten. `_save_csv` already writes the header itself when the
file is missing (self-healing, per CLAUDE.md), which meant the new 5-column header
was written automatically the first time a v0.2.0 build touched a fresh file. The
61 pre-existing rows were migrated once, by hand, outside the application: a trailing
comma was added to each so every row has five fields, with `category_id` empty. A
backup (`sessions.csv.backup-2026-08-06`) was taken first. This was a one-time,
manual data-hygiene step — not a capability the application gained.

"Uncategorised" is legal and permanent: an empty `category_id` field is a valid,
expected value, not a migration artifact to be cleaned up later.

## Consequences

- Every session, old or new, can be attributed to a category without a second
  session-identity column being invented.
- The column is purely additive — nothing about the first four columns changed, so
  every existing reader that ignored unknown trailing fields kept working.
- `core.py` stays ignorant of what a `category_id` *means* — it stores an opaque
  value, same boundary ADR-0009 already drew between the domain and the label
  vocabulary.

What it costs:

- **The header format is no longer uniform across the file's history.** Rows written
  before 06.08.2026 have `category_id` set by a manual one-off edit, not by the
  application. Anyone auditing the file by hand needs to know that boundary exists;
  nothing in the file itself marks where it is.
- **No validation that `category_id` refers to a real, live category.** Same gap
  ADR-0009 already named for the label store in general — restated here because this
  is the column where it would actually be caught, if anything caught it.
- **A second silent migration would look the same as the first.** Nothing prevents
  or flags manual, out-of-band edits to `sessions.csv`; the file's self-healing
  header write masks that this already happened once.

## Notes

If storage moves to SQLite (roadmap Phase 2), this column maps directly onto a
`category_id` foreign-key column on a `sessions` table, exactly as ADR-0009's Notes
section anticipated for the label relationship itself.
