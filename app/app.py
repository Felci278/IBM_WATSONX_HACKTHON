from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import routes_closet, routes_actions, routes_watsonx
import os

app = FastAPI()

# Register routes
app.include_router(routes_closet.router, prefix="/api/routes_closet")
app.include_router(routes_actions.router, prefix="/api/routes_actions")
app.include_router(routes_watsonx.router, prefix="/api/routes_watsonx")

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "ui", "web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))
