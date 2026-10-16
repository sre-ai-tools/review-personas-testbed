# S7: Local env file and prod settings (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 43
- **Files written in the testbed:** none

Check against scenarios/s07-sensitive-files/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 7.0/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 4 | The only code change is a version bump, but the PR also adds api/.env and config/prod/settings.yml, which look like committed secrets. |
| ☁️ AWS architect | – | Not relevant |
| 🗄️ DBA | – | Not relevant |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | 10 | The only visible API change is a patch-level OpenAPI version bump from 1.4.0 to 1.4.1, which changes no routes, fields, status codes or error shapes. |

**🧑‍💻 App developer**
- 🔴 `api/.env` Remove the committed .env file, add it to .gitignore, rotate any credentials it held and load secrets from a secret manager.
- 🔴 `config/prod/settings.yml` Keep prod secrets out of the repository. Reference environment variables or secret-store keys instead, and rotate anything that was exposed.
- 🟡 `api/app/main.py:8` Read the version from package metadata, not a hardcoded string, so it can't drift from the release.

<sub>Not reviewed: `api/.env` (sensitive), `config/prod/settings.yml` (sensitive). Reviewed branch scenario/s07-sensitive-files vs main, including uncommitted changes.</sub>

I can help with these if you like, starting with taking the two sensitive files out of the branch and adding them to `.gitignore`.
