from fastapi import FastAPI
from backend.routes_closet import router as closet_router
from backend.routes_actions import router as actions_router

app = FastAPI()

