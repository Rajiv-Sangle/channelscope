---
type: template
status: active
created: 2026-10-18
updated: 2026-10-18
last_edited_by: agent_claude
tags: [template, mission]
---

# Template: a mission, the test of one premise

A mission opens only when every field below can be filled before the test runs. Until then the idea belongs in the
backlog or an issue. This is a shortened form of aDNA's mission (its standard, version 2.5, section 9), shaped for a
test of one premise.

```markdown
---
type: mission
status: proposed          # proposed until reviewed; then active; then done
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_edited_by: <who or which agent>
tags: [mission, <the premise's theme>]
---

# Mission: <the premise, in a few words>

## The premise
Quoted from README.md, *Roadmap*, with its theme.

## The test
What is measured, on which inputs (each with its source, identifier and version), and by which method.

## What would count against the premise
The result, its metric and its margin, fixed before the test runs.

## Controls
Each check run first on input with a fault planted in it, which it must catch.

## Outcome
Filled in only after the test has run: the result, whether it counts against the premise, and the evidence.
```

A mission's outcome is reported whichever way it falls; a premise that fails is reported as a failure.
