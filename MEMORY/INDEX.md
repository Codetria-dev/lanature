# memory
## vault
path:.claude-memory
last-sync:2026-04-18T18:25:03.002Z
notes-total:10
tagged:#persistent=0 pinned=0

## how-to-use
- Tag any note `#persistent` → always pulled into this index
- Add folders to pinnedFolders in .persistent.json → always pulled
- All other notes: top 5 most recently modified

## hot-notes

### memories/concepts/concept-1776536366095-q2wg.md
> source:recent · modified:2026-04-18
```
# Current Work Focus

review and publish
```

### memories/concepts/concept-1776536366087-cvmo.md
> source:recent · modified:2026-04-18
```
# Project Overview

Lanature SAAS - animal welfare tracking product
```

### _templates/session.md
> source:recent · modified:2026-04-18
```
# Session: {{date:YYYY-MM-DD HH:mm}}

## Focus
<!-- What was the main goal of this session? -->

## Accomplishments
<!-- What was completed? -->

## Key Learnings
<!-- Important discoveries or insights -->

## Decisions Made
<!-- Any decisions reached (link to ADRs if created) -->

## Open Questions
<!-- Unresolved items to follow up on -->

## Next Steps
<!-- Action items for future sessions -->
```

### _templates/troubleshooting.md
> source:recent · modified:2026-04-18
```
# {{title}}

## Symptoms
<!-- What is happening? Error messages, unexpected behavior. -->

## Investigation
<!-- What have you tried? What did you find? -->

## Possible Causes
<!-- Hypotheses about the root cause -->

## Current Status
<!-- In progress / Blocked / Resolved -->

## Solution
<!-- If resolved, how was it fixed? -->
```

### _templates/question.md
> source:recent · modified:2026-04-18
```
## Question
<!-- What needs to be figured out? -->

## Context
<!-- Why is this important? Background info. -->

## Status
Open

## Resolution
<!-- Fill in when resolved -->
```

## cmds
`persistent sync`                          → refresh this file from vault
`persistent sync --pin "Projects/MyApp"`  → add a folder to always-pull list
