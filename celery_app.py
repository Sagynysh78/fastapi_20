from celery import Celery
from settings import settings

celery = Celery(
    "worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

@celery.task
def send_mock_email(email: str):
    import time
    time.sleep(10)
    print(f"Email sent to {email}") 