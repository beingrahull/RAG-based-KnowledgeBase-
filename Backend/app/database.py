from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.config import settings
from app.models.user import User
from app.models.document import UploadedDocument
from app.models.chunk import Chunk

async def init_db() -> None:
    try:
        if settings.mongo_uri.startswith("mongomock://"):
            import mongomock_motor
            client = mongomock_motor.AsyncMongoMockClient()
        else:
            client = AsyncMongoClient(settings.mongo_uri, serverSelectionTimeoutMS=2000)
        await init_beanie(
            database=client[settings.mongo_db_name],
            document_models=[User, UploadedDocument,Chunk]
        )
        print(f"Connected to MongoDB: {settings.mongo_db_name}")
    except Exception as e:
        print(f"Database initialization warning/error: {e}")