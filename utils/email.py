from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr

from config.setting import settings
from error import AppError

file_loader = FileSystemLoader(searchpath="templates/")
env = Environment(loader=file_loader, auto_reload=True, autoescape=True)


class EmailService:
    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=str(settings.MAIL_PASSWORD).strip(),
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
        TEMPLATE_FOLDER="templates",
        MAIL_DEBUG=settings.MAIL_DEBUG,
    )

    @staticmethod
    async def send(
        email: list[EmailStr],
        subject: str,
        content: dict[str, Any],
        email_template: str = "email.html",
    ):
        template = env.get_template(email_template)
        html = template.render(
            content=content.get("barcode"),
        )
        try:
            message = MessageSchema(
                subject=subject, recipients=email, body=html, subtype=MessageType.html
            )
            if len(email) == 0:
                print("Skipped sending email, no emails configured")
                return
            fm = FastMail(EmailService.mail_config)
            await fm.send_message(message, template_name=email_template)

        except ConnectionErrors as e:
            print(e)
            raise AppError(message="Internal Server Error", status_code=500)
        except Exception as e:
            print(e)
            raise AppError(message="Internal Server Error", status_code=500)
