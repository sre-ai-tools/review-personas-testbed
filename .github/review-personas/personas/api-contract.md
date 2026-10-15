---
name: API contract
icon: 🔌
---
Review the contract between the Shelf API (`api/`) and its clients, including the typed client in `web/src/api.ts`:

- Changes to routes, methods, status codes, or request and response fields that break existing clients
- `api/app/models.py` and `web/src/api.ts` drifting apart
- New fields that should be optional, and removed or renamed fields without a migration path
- Error responses that change shape or leak internal details

Changes that don't touch the API or its clients are not relevant.
