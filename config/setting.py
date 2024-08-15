from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    DATABASE_URL: str
    APP_SECRET_KEY: str
    APP_SECRET_KEY_EXPIRES_IN: int
    REDIS_DB: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_SSL_TLS: bool
    MAIL_STARTTLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: str
    MAIL_DEBUG: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AppSettings()
