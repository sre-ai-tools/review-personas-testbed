# S5: DB issue (locking migration)

- [ ] DBA is relevant and catches at least one of: adding a NOT NULL column with no default fails on existing rows; the index is built without CONCURRENTLY and blocks writes on a large table.
- [ ] UI developer: Not relevant.
- [ ] API contract: Not relevant.
- [ ] (CI) Exactly one review comment on the PR.
- [ ] (CI) The check passes.
