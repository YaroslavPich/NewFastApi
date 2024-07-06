from celery import Celery
from src.settings import REDIS_BROKER_URL, REDIS_BACKEND_URL, conf
from fastapi_mail import FastMail, MessageSchema, MessageType
import asyncio
import logging

celery = Celery("tasks", broker=REDIS_BROKER_URL, backend=REDIS_BACKEND_URL)


@celery.task
def sed_notification(user_id: int):
	return 'Notification sent'


@celery.task
def send_test_email_task(email_to_send: str):
	asyncio.run(send_test_email(email_to_send))


async def send_test_email(email_to_send: str):
	message = MessageSchema(
		subject="Fastapi mail module",
		recipients=[email_to_send],
		template_body={"fullname": "Billy Jones"},
		subtype=MessageType.html
	)

	fm = FastMail(conf)
	await fm.send_message(message, template_name='example_mail.html')
	logging.info(f'Test email for {email_to_send} successful')



