from celery import Celery
from src.settings import REDIS_BROKER_URL, REDIS_BACKEND_URL, conf
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
import asyncio
import logging
from pydantic import EmailStr
from src.repository.auth import create_email_token

celery = Celery("tasks", broker=REDIS_BROKER_URL, backend=REDIS_BACKEND_URL)


@celery.task
def sed_notification(user_id: int):
    return 'Notification sent'


@celery.task
def send_test_email_task(email_to_send: EmailStr):
    asyncio.run(send_test_email(email_to_send))


async def send_test_email(email_to_send: EmailStr):
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[email_to_send],
        template_body={"fullname": "Billy Jones"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='example_mail.html')
    logging.info(f'Test email for {email_to_send} successful')


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
