# S1: Add item photos (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 56
- **Files written in the testbed:** none

Check against scenarios/s01-item-photos/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 6.8/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 6 | The owner check and the presigned POST are sound, but photo\_key is saved before the upload succeeds, and no tests cover the new endpoint. |
| ☁️ AWS architect | 7 | The S3 photo design is sound: the bucket is private, encrypted and scoped by IAM, and uploads use presigned POST with size and type limits. |
| 🗄️ DBA | 7 | The migration is safe: it adds a nullable column with no default to items, sets lock\_timeout and does not touch loans, but photo\_key is committed before any upload succeeds. |
| 🎨 UI developer | 7 | The photo upload UI is accessible and mostly sound, but it is shown to users who cannot upload, and the image can break when an upload fails or its URL expires. |
| 🔌 API contract | 7 | The new photo fields match between models.py and api.ts and stay backward compatible, but photo\_url can point to an object that does not exist yet, and its link expires after five minutes. |

**🧑‍💻 App developer**
- 🟠 `api/app/routes/items.py:66` photo\_key is saved before the upload. A failed upload, or a new file type, leaves a broken image link. Save the key only after the…
- 🟠 `api/app/routes/items.py:54` Add tests for POST /items/{id}/photo: 404, 403 for non-owners, a rejected content\_type, and photo\_url in the list and get responses.
- 🟡 `web/src/components/ItemDetail.tsx:52` PhotoUploader shows for every user, so non-owners only get a 403. Render it only when item.owner\_email matches the current user.

**☁️ AWS architect**
- 🟠 `infra/photos.tf:243` Lambda only signs URLs locally, so this endpoint is unneeded. If kept, attach it to the Lambda subnets' private route tables, not the main table,…
- 🟠 `api/app/routes/items.py:162` photo\_key is saved before the S3 upload succeeds, so a failed upload leaves a broken image. Record the key after the upload, or check it…
- 🟡 `infra/photos.tf:199` Add a bucket policy that denies requests where aws:SecureTransport is false. Set the boto3 client to s3v4 with an explicit region so presigned URLs stay…

**🗄️ DBA**
- 🟠 `api/app/routes/items.py:66` photo\_key is saved before the S3 upload, so a failed upload leaves a key with no object behind it. Set the key only after the…
- 🟡 `api/app/routes/items.py:60` Replace SELECT ... FOR UPDATE plus UPDATE with one UPDATE ... WHERE id = %s AND owner\_email = %s RETURNING id, and split 404 and…
- 🟡 `api/app/routes/items.py:66` Switching content type overwrites photo\_key, so the old items/{id}/photo.\* object is never deleted. Delete the previous key, or use a key without an extension.

**🎨 UI developer**
- 🟠 `web/src/components/ItemDetail.tsx:52` Show PhotoUploader only when the current user owns the item. Non-owners currently see a form that always fails with a 403.
- 🟠 `api/app/routes/items.py:162` photo\_key is saved before the S3 upload succeeds, so a failed or abandoned upload leaves a broken image. Save the key only after the upload…
- 🟡 `web/src/components/ItemDetail.tsx:33` The presigned image URL expires after 300 seconds. Handle the img onError by refetching the item, or use a longer TTL, so the photo doesn't…

**🔌 API contract**
- 🟠 `api/app/routes/items.py:163` photo\_key is saved before the S3 upload succeeds, so a failed upload leaves photo\_url pointing to a missing object. Set the key only after the…
- 🟠 `api/app/photos.py:94` photo\_url expires after 300 seconds, so clients that keep item data see broken images. Use a longer TTL or document that photo\_url is short-lived and…
- 🟡 `api/app/routes/items.py:155` The key includes the file extension, so changing the photo's type leaves the old object orphaned. Use one key per item, or delete the previous…

<sub>Reviewed branch scenario/s01-item-photos vs main, including uncommitted changes.</sub>

All five personas flagged that `photo_key` gets saved before the upload succeeds, so I'd start there if you want help fixing these.
