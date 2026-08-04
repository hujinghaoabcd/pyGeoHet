# Handoff policy

The repository must remain understandable without access to the chat in which a change was made.

At the end of every development batch:

1. update `PROJECT_STATUS.md` with facts, not intentions;
2. update `VALIDATION_MATRIX.md` with evidence actually completed;
3. update `CHANGELOG.md`;
4. update `DECISIONS.md` for any durable statistical or API choice;
5. rewrite `HANDOFF_NEXT_CONVERSATION.md` with the authoritative branch/commit, current task, completed work, known disagreements, exact next files, and required commands;
6. verify that the handoff does not claim unimplemented features.

A new conversation begins by reading, in order: `HANDOFF_NEXT_CONVERSATION.md`, `PROJECT_STATUS.md`, `DECISIONS.md`, `VALIDATION_MATRIX.md`, `ROADMAP.md`, then model-specific source, tests and documentation.
