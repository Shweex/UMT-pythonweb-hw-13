"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Contacts REST API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    web_port: int = 8000

    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "contacts_db"
    db_user: str = "postgres"
    db_password: str = "postgres"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_user_cache_ttl_seconds: int = 3600

    auth_jwt_secret: str
    auth_jwt_algorithm: str = "HS256"
    auth_jwt_access_expiration_seconds: int = 3600

    mail_jwt_secret: str
    mail_jwt_expiration_seconds: int = 172800
    password_reset_jwt_expiration_seconds: int = 3600
    mail_server: str
    mail_port: int = 465
    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str = "Contacts API"
    mail_starttls: bool = False
    mail_ssl_tls: bool = True

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    default_avatar_url: str = "https://res.cloudinary.com/demo/image/upload/avatar_default.png"

    test_database_url: str | None = None

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy database URL from individual settings."""
        if self.test_database_url:
            return self.test_database_url
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        """Build the Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return configured CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
