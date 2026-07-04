# Semantic Alignment Skill

## Current Semantic Frame

### Goal

Create an agent skill/package that records and audits semantic alignment across a project or design process, then publish it to GitHub. It may be packaged first as a Codex-compatible skill, but the semantic record model should remain platform-neutral.

### Global Semantics

- The skill should preserve the user's real objective through changes in conversation, design, implementation, and constraints.
- The skill should treat semantics as layered between user semantics and realization semantics, with real artifacts checked against those semantics.
- The skill should record semantic change history and reasons so later audits have traceable material.
- Constraint memory is a subcase, not the top-level concept.

### Local Semantics

- The skill name is `semantic-alignment`.
- The skill should include durable per-project records under `.semantic-alignment/`; workspace-level storage is acceptable when distinct project slugs keep project baselines separate.
- Agents should derive project slugs from explicit user input, repository roots, project manifests, or project directory names, normalize them to lowercase kebab-case, and ask when the project is ambiguous.
- Semantic records should be split by source so user semantics, realization semantics, artifact checks, and audits remain distinguishable.
- `user-semantics.md` should be the current user-semantic state, while `user-semantic-ledger.md` preserves add/update/delete history with reasons.
- The skill should define operational triggers so agents know when to write files, which files to update, and when to escalate from light to standard or deep records.
- The core `SKILL.md` should stay concise and load detailed guidance from references only when needed.
- Semantic-alignment records should stay as project metadata under `.semantic-alignment/` and should not pollute source code, design exports, release artifacts, or user-facing documentation.
- Confirmation, closure, and history-compression rules are part of the skill's operational behavior.
- Repeated audits should use a current summary plus audit events; update status or archive old resolved events instead of deleting normal audit history.
- Full audits should be user-initiated or user-accepted; agent should recommend audits at checkpoints and proactively warn only on narrow contradictions or clearly resolved stale constraints.
- Full audits should exhaustively cover every current user semantic and active realization semantic, and a script should check that coverage before the audit is treated as complete.
- Full audits should first refresh realization semantics against the real project, then refresh artifact checks, and only then use the updated active realization semantics for audit coverage.
- Agents should maintain realization semantics during implementation so audits do not have to reconstruct intended artifact meaning later.
- Realization and audit records should remain current working records; old non-current realization rows and old resolved/accepted/superseded audit events can move to `archive/` when they make routine reads noisy.
- Agents must read relevant semantic records at project start, before planning, before risky inference, before audit recommendations, before constraint rechecks, and before final delivery.
- Agents may reuse already-loaded semantic records when the current semantic frame is fresh; they should reread on new sessions, context uncertainty, record edits, audits, or likely semantic changes.
- Constraint-driven user semantic changes must include concrete recheck triggers in `user-semantic-ledger.md` so reminders are based on observable signals.
- Active recheck triggers should be generated into `recheck-triggers.md` with `scripts/sync_triggers.py` so routine monitoring can avoid scanning the complete ledger.
- Detailed semantic model, operational workflow, audit rules, and record schemas should live in separate focused reference files.
- The current project should use the skill on itself as the first practice case.
- Publish-facing README files should open with a concise story hook about agent drift, name semantic-alignment as the guardrail, and remind users to initiate audits at key checkpoints.
- README audit/reopen content should explain per-item audit, agent-added details, conflicts, artifact mismatch, and stale-route reopening without repeating the same problem story.
- Recheck trigger rules should explicitly define trigger purpose, read timing, evidence sources, linked-ledger procedure, and user-visible reminder behavior.

### Known Unknowns

- The final GitHub repository layout is not yet chosen: standalone `semantic-alignment` repository or multi-skill repository.
- GitHub upload is pending.
- The current Codex shell process has not refreshed PATH after installation; use full tool paths in this session.
