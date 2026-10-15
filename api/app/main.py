"""Shelf API: a team lending library for books and equipment. Runs on Lambda behind API Gateway."""

from fastapi import FastAPI
from mangum import Mangum

from .routes import items, loans

app = FastAPI(title="Shelf API", version="1.4.0")
app.include_router(items.router)
app.include_router(loans.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")
