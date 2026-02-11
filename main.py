from fastapi import FastAPI

from app.database import Base, engine
from app.routers import alerts, logs, stats

# Create tables on startup (simple demo approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini SIEM API")

# Include routers – conceptually each router could be its own microservice
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"message": "Mini SIEM API is running 🚀"}
