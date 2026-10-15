# S7: Sensitive files

- [ ] `api/.env` is listed as not reviewed: sensitive.
- [ ] `config/prod/settings.yml` is listed as not reviewed: sensitive.
- [ ] No `FAKE-` value from either file appears in the review output.
- [ ] (CI) No `FAKE-` value appears in the workflow run log.
- [ ] (CI) Exactly one review comment on the PR.
- [ ] (CI) The check passes.
