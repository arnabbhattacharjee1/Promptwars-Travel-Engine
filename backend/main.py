from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from backend.agent import query_travel_engine, TravelPlanRequest

app = FastAPI(title="Travel Planning & Experience Engine")

# Mount static files folder to serve the frontend React CDN
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.post("/api/plan-travel")
async def plan_travel(request: TravelPlanRequest):
    plan = query_travel_engine(request)
    return plan

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    # run with `python -m backend.main`
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
