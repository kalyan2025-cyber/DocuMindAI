from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from app.db.mongo import check_database, client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()


app = FastAPI(
    title="DocuMind AI",
    description="Business Knowledge Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def home():
    return {
        "project": "DocuMind AI",
        "message": "Backend is running",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "DocuMind AI"}


@app.get("/api/health/database")
def database_health():
    if check_database():
        return {"status": "ok"}

    return JSONResponse(
        status_code=503,
        content={"status": "unavailable"},
    )
