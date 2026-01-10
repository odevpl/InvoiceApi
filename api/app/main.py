from fastapi import FastAPI

from api.routes import health


app = FastAPI(title="Invoice API")

app.include_router(health.router)
