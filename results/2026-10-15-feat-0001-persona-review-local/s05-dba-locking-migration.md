# S5: Record return condition on loans (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 46
- **Files written in the testbed:** none

Check against scenarios/s05-dba-locking-migration/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 1.5/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 2 | Adding a NOT NULL column with no default fails on existing rows, which breaks the migration, and the PR has no application code or tests that use the new column. |
| ☁️ AWS architect | – | Not relevant |
| 🗄️ DBA | 1 | The migration will fail on the 50M-row loans table, and even if it ran it would block writes during a long index build. |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🔴 `db/migrations/004_loans_return_condition.sql:3` NOT NULL without DEFAULT fails on existing rows and breaks inserts for active loans. Make it nullable, since unreturned loans have no condition.
- 🟠 `db/migrations/004_loans_return_condition.sql:3` Free text invites inconsistent values. Use a CHECK constraint or enum for the allowed conditions, and add application code and tests that write them.
- 🟡 `db/migrations/004_loans_return_condition.sql:4` Drop this index unless a query filters by returned\_condition. A low-cardinality index on 50M rows costs writes for little benefit.

**🗄️ DBA**
- 🔴 `db/migrations/004_loans_return_condition.sql:3` Adding a NOT NULL column with no default fails because loans already has rows. Add it as nullable, backfill in batches, then add a NOT…
- 🔴 `db/migrations/004_loans_return_condition.sql:4` A plain CREATE INDEX blocks writes to 50M rows for the whole build. Use CREATE INDEX CONCURRENTLY in its own non-transactional migration, and set lock\_timeout.
- 🟠 `db/migrations/004_loans_return_condition.sql:4` returned\_condition likely has few distinct values, so this index will rarely be used. Drop it, or use a partial or composite index that matches real…

<sub>Reviewed branch scenario/s05-dba-locking-migration vs main, including uncommitted changes.</sub>

Want me to help fix the migration?
