# Architecture

```
browser ──▶ CloudFront ──▶ S3 (web/ build)
   │
   └──────▶ API Gateway (JWT authorizer, company SSO) ──▶ Lambda (api/) ──▶ RDS Postgres (private subnets)
```

- **Identity.** API Gateway verifies the SSO token. The API reads the caller's email from the verified claims and never trusts an email in the request body.
- **Loans.** An item has at most one open loan. The API checks it inside a transaction with the item row locked, and a partial unique index enforces it in the database.
- **Late fees.** 50 cents for each day late, capped at $20. Fees are stored in whole cents, so there is no rounding.
- **Database credentials.** RDS manages the master password in Secrets Manager. The Lambda reads it through a VPC endpoint; nothing is stored in code or environment variables.
- **Migrations.** dbmate applies `db/migrations/` in order. Migrations that touch existing large tables must not block writes: build indexes `CONCURRENTLY` (with `transaction:false`) and add columns in steps.
