# Shelf

Shelf is a team lending library: people list books and equipment they own, and colleagues borrow and return them.

| Part | Where | Stack |
|---|---|---|
| Infrastructure | `infra/` | Terraform: VPC, RDS Postgres 16, API Gateway (HTTP API with a JWT authorizer), Lambda, S3 + CloudFront |
| API | `api/` | Python 3.12, FastAPI on Lambda (Mangum), psycopg 3 |
| UI | `web/` | React 18 with TypeScript, built with Vite |
| Database | `db/migrations/` | Postgres migrations, applied in order with dbmate |

See [architecture.md](architecture.md) for how the parts fit together.
