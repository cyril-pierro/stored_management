from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    DATABASE_URL: str = "sqlite:///test.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AppSettings()
