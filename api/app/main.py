from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from api.config.db import engine
from api.routes import health, auth, protected

from api.middlewares.logging import logging_middleware
from starlette.middleware.base import BaseHTTPMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK")
    except Exception as e:
        print("Database connection FAILED:", e)
        raise e

    yield

app = FastAPI(title="Invoice API", lifespan=lifespan)

# Add middleware for logging
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

# Add routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(protected.router)
