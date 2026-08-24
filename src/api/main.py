from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import exchange_rates, indicators, dashboard, websocket

app = FastAPI(
    title="Bangladesh Financial Data Platform API",
    description="REST API serving exchange rates, inflation, reserves, trade, and remittance data for Bangladesh.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; tighten this before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exchange_rates.router)
app.include_router(indicators.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Bangladesh Financial Data Platform API is running"}
