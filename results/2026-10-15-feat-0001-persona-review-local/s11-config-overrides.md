# S11: Index items by kind (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 31
- **Files written in the testbed:** none

Check against scenarios/s11-config-overrides/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 8.5/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 8 | The non-blocking index migration and its rollback look correct, but a failed concurrent build leaves an invalid index behind that the up step cannot recover from. |
| 🗄️ DBA | 9 | The new index is built with CREATE INDEX CONCURRENTLY outside a transaction, so it does not block writes, and the down migration reverses it cleanly; the only gap is cleanup if the build fails. |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🟡 `db/migrations/004_items_kind_idx.sql:3` A failed CREATE INDEX CONCURRENTLY leaves an invalid index, so a rerun fails. Add 'DROP INDEX CONCURRENTLY IF EXISTS' before the create.

**🗄️ DBA**
- 🟡 `db/migrations/004_items_kind_idx.sql:3` A failed concurrent build leaves an INVALID index that blocks re-running. Add a runbook note: check pg\_index.indisvalid, then DROP INDEX CONCURRENTLY and retry.

<sub>Reviewed branch scenario/s11-config-overrides vs main, including uncommitted changes.</sub>

Want me to add the `DROP INDEX CONCURRENTLY IF EXISTS` guard to the migration?
