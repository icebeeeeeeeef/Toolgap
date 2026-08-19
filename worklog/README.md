# ToolGap Worklog

`worklog/` preserves the reasoning that helps a later contributor understand a
local task, a decision, or a corrected assumption. It is an operational history
layer, not a second project plan and not evidence that a proposed feature has
been implemented.

## Layout

```text
worklog/
  README.md
  plans/YYYY-MM-DD/<topic>.md
  reviews/YYYY-MM-DD/<topic>.md
  lessons/YYYY-MM-DD/<topic>.md
```

Each date is a directory, so one day can contain several related documents
without making search or file names noisy. Create a date directory only when a
record is needed. Use concise, lowercase, hyphenated topic names.

## Authority

Worklog entries explain *why* a local action was taken. They never supersede
the canonical document that owns the fact:

- `docs/PROJECT.md` — project scope and current project-level truth;
- `docs/ROADMAP.md` — Gate order and exit decisions;
- `docs/DEMOTION_CONTRACT.md` — checked-demotion semantics;
- `docs/DECISIONS.md` — durable project decisions and their historical
  rationale;
- `experiments/<gate>/` — frozen Gate specifications and execution evidence.

When a worklog entry changes one of those facts, update the owner first and
link to it from the entry. A worklog entry does not promote a claim beyond its
declared state (`roadmap`, `shipped`, `experimentally validated`, or
`simulated`).

## What to write

- **Plan** — goal, scope and non-goals, acceptance evidence, dependencies, and
  final status. Create one for a non-trivial executable task.
- **Review** — decision question, evidence, viable alternatives, decision,
  rejected alternatives, and canonical follow-up. Record only discussions that
  changed a decision.
- **Lesson** — trigger, incorrect assumption, evidence, correction, and the
  rule a future contributor should apply. Record a real counterexample or
  error, not generic advice.

Before starting relevant work, search this directory by topic and component.
When work finishes, update its plan status and add a review or lesson only if
the work exposed a material decision or a corrected assumption.

Do not put raw chat transcripts, private reasoning, secrets, generated logs,
or copies of frozen experiment artifacts here. Preserve prior records; append a
correction or supersession instead of rewriting history.
