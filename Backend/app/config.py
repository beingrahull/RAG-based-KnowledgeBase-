from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "RAG KBEng"
    env: str = "development"
    port: int = 8000

    # Database
    mongo_uri: str
    mongo_db_name: str = "rag_kbeng"

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7    # 7 days

    # LLM (fill these in when you reach the embedding stage)
    openai_api_key: str = ""

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k_retrieve: int = 5

    # In Settings class
    gemini_api_key: str
    embedding_model: str = "gemini-embedding-2"
    embedding_dim: int = 1536 

    pinecone_api_key: str
    pinecone_index_name: str = "rag-kbeng"

    

settings = Settings()