# S3: Let borrowers extend a loan (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 52
- **Files written in the testbed:** none

Check against scenarios/s03-app-missing-none-check/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 5.0/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 4 | The new extend endpoint has no None check on the loan lookup, so a missing or already-returned loan causes a 500 error instead of a 404, and there are no tests. |
| ☁️ AWS architect | – | Not relevant |
| 🗄️ DBA | 7 | The extend endpoint takes a FOR UPDATE row lock by primary key inside a transaction, which is sound, but a missing row is not handled and there is no limit on extensions. |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | 4 | The new extend endpoint does not check for a missing loan, so an unknown or already returned loan gives an undocumented 500 instead of a 404 or 409. |

**🧑‍💻 App developer**
- 🔴 `api/app/routes/loans.py:67` \_open\_loan can return None, so loan\["borrower\_email"\] raises TypeError. Raise HTTPException(404) when loan is None before checking who the borrower is.
- 🟠 `api/app/routes/loans.py:71` Extensions have no cap, so repeated calls can push due\_at out forever and dodge late fees. Limit the total extension or block extending overdue loans.
- 🟠 `api/app/routes/loans.py:61` Add tests for the extend endpoint: success, a non-borrower getting 403, a missing or returned loan getting 404, and days outside the allowed range being…

**🗄️ DBA**
- 🟠 `api/app/routes/loans.py:69` If \_open\_loan returns None, the code raises a TypeError and the request fails with a 500 after the transaction rolls back. Return 404 when loan…
- 🟡 `api/app/routes/loans.py:72` Repeated calls can push due\_at out without limit. Track an extension count or maximum due date, and enforce it with a CHECK constraint or in…
- 🟡 `api/app/routes/loans.py:58` Select only the columns you need instead of SELECT \* under FOR UPDATE, so the lookup doesn't pull extra columns and keeps working if the…

**🔌 API contract**
- 🔴 `api/app/routes/loans.py:67` If \_open\_loan returns None, raise HTTPException 404 (or 409 for an already returned loan) before subscripting; right now clients get an opaque 500 TypeError.
- 🟠 `api/app/routes/loans.py:67` Return 404 instead of 403 for loans owned by someone else, so the endpoint doesn't reveal which loan IDs exist, or document the 403 response.
- 🟡 `api/app/models.py:29` Add LoanExtend and an extendLoan method to web/src/api.ts so the typed client matches the new route and its days limit (1 to 30).

<sub>Reviewed branch scenario/s03-app-missing-none-check vs main, including uncommitted changes.</sub>

I can fix these, starting with the missing 404 check for a loan that doesn't exist, if you'd like.
