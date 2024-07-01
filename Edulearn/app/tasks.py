from celery import shared_task
from celery.utils.log import get_task_logger
from .email import send_review_email

logger = get_task_logger(__name__)

@shared_task(name="send_review_email_task", bind=True)
def send_review_email_task(self, name, email, review):
    logger.info("Sent review email")
    return send_review_email(name=name, email=email, review=review)
