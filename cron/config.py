from config.setting import settings


class Config:
    broker_url = f"redis://@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    result_backend = f"redis://@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    broker_connection_retry_on_startup = True