# S3: App issue (missing None check)

- [ ] App developer is relevant and catches: `_open_loan` can return None, and `extend` uses the result without checking, so a missing or returned loan gives a 500 instead of a 404.
- [ ] API contract is relevant (new route).
- [ ] AWS architect: Not relevant.
- [ ] UI developer: Not relevant.
- [ ] (CI) Exactly one review comment on the PR.
- [ ] (CI) The check passes.
