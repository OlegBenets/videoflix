from django.db import transaction
import django_rq
from rq import Retry
import logging

logger = logging.getLogger(__name__)
DEFAULT_RETRY = Retry(max=3, interval=[10, 30, 60])
DEFAULT_QUEUE = "default"

def enqueue_after_commit(task, *args, retry=DEFAULT_RETRY, queue=DEFAULT_QUEUE, **kwargs):
    """
    Queue a Task after DB-commit, with Retry and logging.
    """
    def _enqueue():
        django_rq.enqueue(task, *args, retry=retry, **kwargs, queue=queue)
        logger.info(f"Task {task.__name__} enqueued with args={args} kwargs={kwargs} in queue='{queue}'")

    transaction.on_commit(_enqueue)
