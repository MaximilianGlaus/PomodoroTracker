# ADR-0006 — First interface: CLI, behind a UI-agnostic domain

**Status:** Superseded by ADR-0008 (delivery interface only — the UI-agnostic-domain principle stands)
**Date:** 2026-07-14

## Context

Constraint C-1 asks for low-friction use "anywhere". Read carefully, that is not a demand
to ship three front-ends — it is a demand that the **domain** (the state machine, the
timer logic, the rule for what counts as a Pomodoro, the writing of rows) must not depend
on any single interface. The moment the domain calls `print()` or touches a window
toolkit, platform independence is already lost.

But a port — the contract the domain exposes (*commands in*: start, pause, resume,
acknowledge, abort; *events out*: tick, phase elapsed, phase stored) — cannot be designed
well in a vacuum. It has to be shaped against one concrete adapter, or it comes out the
wrong shape. So one interface must be chosen to design against first.

This is a first substantial project, learning-focused. The learning value sits in the
domain and in the port design, not in the incidental complexity of a UI framework. Data
is stored locally.

## Options

- **CLI (terminal, text).** Lowest build cost; no external library; a keypress is a
  command and a printed line is output. Keeps effort on the domain.
- **GUI (desktop window).** Medium cost; Python's bundled Tkinter avoids an install, but
  windows, buttons and screen-redraws are a second topic layered on the timer.
- **Web (browser + server).** Highest cost; adds a server framework, HTML/JS and the
  network between them. Payoff is reach (phone, any machine).

## Decision

Build the domain **UI-agnostic behind a port**, and make the **first adapter a minimal
CLI**, treated as **disposable** — its purpose is to drive and validate the domain
end-to-end, not to be the finished product. GUI and Web are deferred; when built, they
plug into the *same* port as additional adapters.

Concretely:
- The domain never imports a UI toolkit and never calls `print`/`input`. All rendering
  and all input handling live in the adapter.
- The port **pushes** events (the domain announces "phase elapsed" the instant it
  happens) rather than making the adapter poll — so a later GUI can react immediately.
- The domain can be exercised from a plain test script with a fake clock, before any
  adapter exists.

## Consequences

- **The boundary must be defended, not assumed.** If any UI concern leaks into the domain,
  C-1 is void in practice even if the docs say otherwise. This needs to be watched in
  review, not trusted to good intentions.
- **Designing the port against the CLI risks under-specifying it.** A CLI is happy to
  poll; a GUI is not. The push-based event design above is a deliberate guard against
  building a port that only the CLI could ever use — but some flaws will still only
  surface when the second adapter is built. Accepted: a port revision at GUI time is
  cheaper than building the GUI now.
- **The CLI is a weak *product*, on purpose.** It is hidden behind other windows (not
  glanceable while you work elsewhere), and its "changed interface + sound" on elapse is
  limited to what a terminal can do. Accepted because the CLI is a validation adapter, not
  the shipped experience.
- **"Anywhere" (C-1) is only partly met by a CLI.** Terminal behaviour, sound and redraw
  differ across operating systems. The full platform-independence goal is carried by the
  clean port, to be realised by later adapters — not claimed for V1.
