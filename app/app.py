from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api import routes_closet, routes_actions  # add watsonx later if needed

app = FastAPI(title="Sustainable Clothing Assistant")

# Register API routes
app.include_router(routes_closet.router, prefix="/api/closet", tags=["Closet"])
app.include_router(routes_actions.router, prefix="/api/actions", tags=["Actions"])


# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), "ui", "web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Make `/` serve index.html directly
@app.get("/")
async def serve_home():
    return FileResponse(os.path.join(static_dir, "index.html"))
