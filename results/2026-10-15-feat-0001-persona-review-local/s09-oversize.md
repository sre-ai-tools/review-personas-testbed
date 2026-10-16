# S9: Demo seed data (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 39
- **Files written in the testbed:** none

Check against scenarios/s09-oversize/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 6.7/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 6 | The seed script is simple but nothing in the code stops it running against production, reruns insert duplicate rows, and there are no tests. |
| ☁️ AWS architect | 7 | This is a small seed script that reads DB credentials through a Secrets Manager ARN, but only a docstring stops it from running against production. |
| 🗄️ DBA | 7 | The seed script uses parameterized inserts in a single transaction, but it can run twice and duplicate rows, nothing stops it from running against production, and the seed file's email data could not be checked. |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🟠 `api/app/seed.py:43` Enforce 'never run against production' in code: check the environment or DB\_HOST against an allowlist and abort before connecting.
- 🟠 `api/app/seed.py:47` Make the insert idempotent with ON CONFLICT DO NOTHING on a natural key, or delete existing seed rows first, so reruns don't duplicate items.
- 🟡 `api/app/seed.py:48` Validate seed records and report bad entries clearly instead of failing with a bare KeyError. Add a test that loads seed\_items.json and checks its schema.

**☁️ AWS architect**
- 🟠 `api/app/seed.py:43` Add a runtime guard: refuse to run unless an environment variable or the secret ARN or account ID matches local or staging, and fail otherwise.
- 🟡 `api/app/seed.py:1` Use a staging-only IAM role or secret with INSERT on items only, so production credentials can't be used by mistake.
- 🟡 `api/app/seed.py:47` Make the seed safe to re-run (ON CONFLICT DO NOTHING or a clear-first step) so repeated runs don't duplicate items.

**🗄️ DBA**
- 🟠 `api/app/seed.py:45` Add a hard guard that refuses to run against production, for example by checking an environment or host allowlist. The docstring warning alone does not…
- 🟠 `api/app/seed.py:49` Make the seed idempotent with ON CONFLICT DO NOTHING on a unique key, or check for existing rows first. Reruns currently insert duplicate items.
- 🟡 `api/app/data/seed_items.json` This file was not shown. Confirm owner\_email values are synthetic addresses (example.com), not real user PII.

<sub>Not reviewed: `api/app/data/seed_items.json` (size limit). Reviewed branch scenario/s09-oversize vs main, including uncommitted changes.</sub>

I can add a production guard and make the seed insert safe to re-run if you'd like.
