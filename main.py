from fastapi import FastAPI
from app.routers import logs

app = FastAPI(title="Mini SIEM API")

# Include routers
app.include_router(logs.router)

@app.get("/")
def root():
    return {"message": "Mini SIEM API is running 🚀"}
