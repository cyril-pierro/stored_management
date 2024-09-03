from cron import celery_app
from typing import Any
from asgiref.sync import async_to_sync
from utils.email import EmailService


@celery_app.task(autoretry_for=(Exception,), max_retries=7, retry_backoff=True)
def send_email(
    email: list[str], subject: str, content: dict[str, Any], email_template: str = None
):
    if email_template:
        async_to_sync(EmailService.send)(
            email=email, subject=subject, content=content, email_template=email_template
        )
    else:
        async_to_sync(EmailService.send)(
            email=email, subject=subject, content=content
        )
    return True