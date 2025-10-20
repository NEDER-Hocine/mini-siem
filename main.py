from fastapi import FastAPI
from app.routers import logs, alerts

app = FastAPI(title="Mini SIEM API")

# Include routers
app.include_router(logs.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"message": "Mini SIEM API is running 🚀"}
