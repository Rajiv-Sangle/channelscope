---
type: template
status: active
created: 2026-10-18
updated: 2026-10-18
last_edited_by: agent_claude
tags: [template, session]
---

# Template: a working session

Copy this file to `how/sessions/` in your own copy of the repository, named for the date and the task, and fill it in
as the session goes. A session file is the agent's record; it is not merged into the project. This is a shortened
form of aDNA's session file (its standard, version 2.5, section 8): a full one adds a session ID (section 8.2), a
SITREP at the close (8.4) and a prompt for the next session (8.5).

```markdown
---
type: session
status: active            # active while working; completed at the close
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_edited_by: <who or which agent>
tags: [session, <topic>]
---

# Session: <the task, in a few words>

## Objective
What this session sets out to do, and how you will know it is done.

## Read first
README.md, MANIFEST.md, STATE.md, and the parts of .agentic/ the task needs.

## Log
What was done, in order, with the time of each step taken from the clock, not estimated.

## Checks
Each check run: its command, what it compared, and its result, failures included.

## Close
What was finished, what was not, and what the next session should do first.
```

**The project's rules apply to every session** (the root `CLAUDE.md`, *Rules to keep*): every value with its
provenance, signals rather than verdicts, no claim beyond the README, the numbering named, transfer kept a premise,
checks that can fail, and each source's terms kept.
