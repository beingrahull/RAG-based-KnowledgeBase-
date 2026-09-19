from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import settings
from app.database import init_db
from app.routers import auth,documents,query




@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print(f"Server on http://127.0.0.1:{settings.port}")
    print(f"Docs on http://127.0.0.1:{settings.port}/docs")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)

@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "upload": "POST /api/documents/upload",
            "list_documents": "GET /api/documents",
            "query": "POST /api/query",
        },
    }