 # Changed import
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="database_url")
    REDIS_URL: str = Field(..., env="redis_url")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    DEBUG: bool = Field(default=False)
    ALLOWED_HOSTS: str = Field(default="*")
    
    class Config:
        env_file = ".env"

settings = Settings()
