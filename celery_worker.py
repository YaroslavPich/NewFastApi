from celery import Celery
from src.settings import BROKER_URL, BACKEND_URL


celery = Celery("tasks", broker=BROKER_URL, backend=BACKEND_URL)


@celery.task(name="Add two numbers")
def add(x, y):
    return x + y
