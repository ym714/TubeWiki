from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.api import notes, payment

# ... (existing code)

app.include_router(notes.router, prefix="/api/v1")
app.include_router(payment.router, prefix="/api/v1")

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
