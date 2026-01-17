from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware

from api.config.db import Base, engine
from api.routes import health, auth, protected
from api.utils.logger import logger
from api.middlewares.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK")  # print to console
        logger.info("Database connection OK")  # print to log

    except Exception as e:
        print("Database connection FAILED:", e)  # print to console
        logger.error("Database connection FAILED:",
                     exc_info=True)  # print to log
        raise e
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")

app = FastAPI(title="Invoice API", lifespan=lifespan)


# Add middleware for logging
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LoggingMiddleware)

# Add routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(protected.router)

# Temporary solution before Alembic
Base.metadata.create_all(bind=engine)