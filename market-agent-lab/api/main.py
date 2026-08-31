from fastapi import FastAPI

app=FastAPI(title="Market Agent Lab",version="0.1.0",description="Paper/simulation only")
@app.get("/health")
def health():return {"status":"ok","mode":"paper-only"}
@app.get("/safety")
def safety():return {"live_brokerage":False,"prediction_markets":False,"risk_engine":"deterministic"}
