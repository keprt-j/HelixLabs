from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helixlabs.api.routes import router as runs_router

app = FastAPI(title="HelixLabs API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router)
