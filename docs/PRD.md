# PRD — CocoClock v0.3.0

| Field | Value |
|---|---|
| Status | Draft |
| Owner | Max |
| Created | 2026-08-05 |
| Milestone | Tracker v0.3.0 with live LLM progress indicator |
| References | Administration `decisions.md` D-0002 · [REQUIREMENTS.md](REQUIREMENTS.md) US-5/US-6 |

## Change Log

| Date | Change |
|---|---|
| 2026-08-05 | Created: vision + empty scaffold. Sections below are written by Max. |
| 2026-08-05 | First drafts added (problem / MVP / success criteria). Document translated to English (project docs are kept in English). |
| 2026-08-05 | Structure slimmed: Non-Goals merged into "Out of Scope / Later"; Cut Line reduced to one line; the anomaly set is stated once (Success Criteria) and referenced from the MVP. |
| 2026-08-11 | LLM requirement to report on +/- 25% effort was replaced with live progress tracking. |
| 2026-08-11 | Pivot: feature is a live, always-visible progress indicator (today + 7-day retrospective) refreshed on app launch/break, not a weekly batch summary. Reasoning: a live signal during the day is more actionable than a retrospective report. Trade-off accepted: the two pattern checks (missing weekday, weekend work) are left to the LLM's own reading of the daily data rather than built as separate tested Python functions — saves build time within the KW33 3-day cap, at the cost of guaranteed-correct detection for those two. |
| 2026-08-19 | Milestone renumbered v0.2.0 → v0.3.0. Reasoning: v0.2.0 was the category/label integration, already shipped (v0.2.0–v0.2.3 on `main`); this LLM feature is a separate, distinct milestone and gets its own version rather than being folded into the one that already shipped. |
| 2026-08-24 | Deduping scratched in order to make time for UX and Portfolio polish. |


---

## Vision (North Star)

> Aspirational. Not the v0.2.0 scope — the direction v0.2.0 points toward.

For self-taught learners without an externally enforced curriculum — who risk missing their strategic goals, in substance or in time, despite daily, intensive work — CocoClock is a study-management software that provides accountability over a self-assembled study plan, unlike alternative learning offerings, which provide this at most in isolation, for their own course content only.

---

## Problem / Target User (v0.2.0)

> Which *narrower slice* of the vision does v0.2.0 solve — for whom, and what pain?

The self-taught learner might measure his time investment, however measured data on its own is dead information; it does not necessarily demand any critical engagement with it.

## MVP v0.2.0 — What

> The thinnest end-to-end value that points toward the vision and is buildable *now*.
> Core decision (05.08.): **Mirror**, not accountability.

An LLM instance reports the work done and names gaps and achievements — for the progress of the current day and retrospectively for the last 7 days. The model gets called at startup and at break.
(The specific, testable anomalies it must name are listed once, under Success Criteria.)

## Success Criteria (measurable)

> How do you recognize *in binary terms* that v0.2.0 is done? Testable, not "nice".

An LLM instance reports autonomously on the learning history and names anomalies with useful latency (<15sec).

It successfully identifies all patterns in a test set:
- Weekdays missing work.
- Weekend days with work.
- Correctly reports daily progress (`today_total / target_by_day`) towards the daily target (hardcoded 15 x Pomodoros for now).

## Scope + Cut Line

> In scope for the v0.2.0 milestone. Timeline and cut per D-0002.

**In scope**
- GUI integration of the category labels: selection interface with a drop-down menu.
- LLM live progress + 7-day retrospective reporting (the Mirror — see MVP / Success Criteria).

**Timeline (D-0002):** foundation (category GUI) done by **Fri 07.08.**, LLM reporting from **Mon 10.08.** Whatever is not standing by Friday gets cut, not extended.

**Cut line (first to give, in order):** the reworked/simplified appealing UI first, then manual adding/editing of categories. 

## API Provider

> Decision + rationale. Criteria: cost/token · quality of the Python SDK · free credits / onboarding · docs.

OpenAI GPT-5 nano has been chosen for OpenAI’s market position, the existing credits, a good SDK and support features, and because GPT-5 nano is very cost-efficient and fast and most likely largely sufficient. for the task at hand

## Assumptions & Open Questions

OpenAI GPT-5 Nano has been chosen after some research, however in the end it is my first use of an LLM tool, so its capabilities might not match my expectations.

## Out of Scope / Later (parking lot)

> Deliberately not in v0.2.0 — the single home for non-goals and future ideas, so they don't creep into scope. See also [BACKLOG.md](BACKLOG.md).

- Pomodoro Settings to be adjustable (Lenght, Targets, Days etc)
- Run models locally.
- Transcription feature for user input.
- Give the LLM access to study plans.
- Break-pattern analysis: days where the five-minute breaks are skipped and the resulting pattern has, in total, longer breaks (+50%) than a respected Pomodoro pattern would.
- Break timer indicates a possible break extension due to overtime work.
- manual adding/editing of work session entries.
- The ability to comment on worksession manually or using the LLM.
- last selected category as UX Hint -> config
