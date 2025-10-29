"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from . import routes

app = FastAPI(title="EchoGraph API", version="0.1.0")
app.include_router(routes.router)


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
