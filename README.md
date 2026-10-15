# review-personas testbed

End-to-end tests for [review-personas](https://github.com/sre-ai-tools/review-personas). This repo is a **caller**: it uses review-personas exactly as a pilot repo would. Each scenario is a prepared PR with a known expected outcome.

It is specified in review-personas' [docs/specs/0002-test-applications](https://github.com/sre-ai-tools/review-personas/tree/main/docs/specs/0002-test-applications). Design decisions are cited as T1–T9.

> **Everything here is fake.** Shelf (below) is never built or deployed. Secrets in scenarios contain `FAKE` and are not real credentials. Scenario S8 contains a prompt-injection attempt on purpose.

## What's here

| Path | What |
|---|---|
| `infra/`, `api/`, `web/`, `db/migrations/` | **Shelf**, a small team lending library: Terraform, a FastAPI app on Lambda, a React UI and Postgres migrations. It's clean on `main`, and every built-in persona has code to review. See [docs/README.md](docs/README.md). |
| `.github/workflows/review-personas.yml` | The caller workflow. It reviews `scenario/*` PRs only. |
| `.github/review-personas.yml` | Caller config: an extra sensitive-file pattern and extra DBA focus. |
| `.github/review-personas/personas/api-contract.md` | A custom persona. |
| `scenarios/sNN-*/` | One folder per scenario: `pr.yml`, `change.patch`, `expect.md` (the checklist) and, for S10, `followup.patch`. |
| `scripts/scenario.py` | Pins a version, opens scenario PRs, sets up local runs and writes results. |
| `results/` | One filled-in checklist per verification run. |

## Scenarios

| ID | Scenario | Paths |
|---|---|---|
| S1 | Clean change touching all four areas (item photos) | CI, local |
| S2 | AWS: SSH open to 0.0.0.0/0 | CI, local |
| S3 | App: missing `None` check | CI, local |
| S4 | UI: accessibility | CI, local |
| S5 | DB: locking migration | CI, local |
| S6 | Docs only: every persona not relevant | CI, local |
| S7 | Sensitive files: `.env` and a caller deny pattern | CI, local |
| S8 | Prompt injection | CI, local |
| S9 | A file over the size limit | CI, local |
| S10 | Re-push updates the same comment | CI |
| S11 | Config: a disabled persona and a per-persona model | CI, local |
| S12 | One persona's model doesn't exist | CI |
| S13 | Invalid config | CI |

## Verify a review-personas version

You need Python 3.12+, `git`, and `gh` logged in with write access to this repo and review-personas. You also need a clone of review-personas next to this one (or pass `--tool-repo`).

### 1. Pin the version (T4)

```sh
scripts/scenario.py pin v1.2.3            # a release tag
scripts/scenario.py pin feat/my-change    # or a branch or commit in the review-personas clone
```

For a release tag, the caller workflow uses it directly. For anything else, `pin` pushes a branch `testbed/<sha7>` to review-personas. That branch is the commit under test plus one commit that points `review.yml`'s action at that commit, so the workflow and the action are the same version. Without this, `review.yml` would run `main`'s action until a release rewrote it. Then `pin` commits the new `uses:` line to this repo's `main`.

### 2. Start a results record

```sh
scripts/scenario.py record v1.2.3        # writes results/<date>-v1.2.3.md
```

Note the start time in it.

### 3. CI path

```sh
scripts/scenario.py run all              # or: run s2 s5
```

`run` closes any open scenario PR, recreates its `scenario/*` branch from `main`, applies the patch and opens a fresh PR. S10 waits for its first review, then pushes the follow-up. `run all` asks once before starting, because each PR calls Bedrock.

Check each PR's comment, run log and job summary against `scenarios/<id>/expect.md`, and fill in the CI column.

### 4. Local path (T7)

Install the plugin from the version under test, in Claude Code:

```
/plugin marketplace remove review-personas
/plugin marketplace add /path/to/review-personas      # the clone, checked out at the version under test
/plugin install prpanel@review-personas
```

Then, for each scenario that isn't CI-only:

```sh
scripts/scenario.py local s2             # local branch with the patch applied; never pushed
```

```
/prpanel:review --base main
```

Fill in the Local column, skipping `(CI)` items. Run `git status` to confirm nothing was written, then `git checkout main`.

### 5. Finish

Fill in the finish time and any failures, with links to review-personas issues. Commit the record to `main`, then clean up:

```sh
scripts/scenario.py clean --pins
```

## Caller setup (copy this for your own repo)

This repo's setup is what a pilot repo needs. The parts specific to this testbed are the `scenario/` branch filter in the workflow's `if:` and the `pin` comment.

### Workflow

See [.github/workflows/review-personas.yml](.github/workflows/review-personas.yml). In your repo, use `@v1` in place of the pinned ref, and keep:

- `on: pull_request` (never `pull_request_target`);
- the `contents: read`, `pull-requests: write` and `id-token: write` permissions;
- the per-PR `concurrency` group.

### AWS role (T9)

The testbed uses the IAM role `review-personas-testbed`, in the same AWS account as the review-personas evals role. Set two repository variables: `TESTBED_AWS_ROLE_ARN`, and optionally `TESTBED_AWS_REGION` (default `us-east-1`).

Trust policy. Only PR runs from this repo can assume it:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com" },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike": { "token.actions.githubusercontent.com:sub": "repo:sre-ai-tools/review-personas-testbed:pull_request" }
      }
    }
  ]
}
```

Permissions. Only the models the scenarios use: the default model, and S11's DBA model.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": [
        "arn:aws:bedrock:*:<ACCOUNT_ID>:inference-profile/global.anthropic.claude-opus-5-5",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-opus-5-5",
        "arn:aws:bedrock:*:<ACCOUNT_ID>:inference-profile/global.anthropic.claude-sonnet-5-5",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-5-5"
      ]
    }
  ]
}
```

`bedrock:InvokeModel` also covers the Converse API that review-personas uses.
