from celery import Celery
from cron.config import Config

celery_app = Celery("cron", include=["cron.task"])
celery_app.config_from_object(Config)

if __name__ == "__main__":
    celery_app.start()