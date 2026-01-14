from fastapi import FastAPI

from api.routes import health, auth, protected


app = FastAPI(title="Invoice API")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(protected.router)
