import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq
from .models import Video
from .tasks import generate_thumbnail

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    When a new video is uploaded, queue thumbnail generation.
    """
    if created and instance.file:
        queue = django_rq.get_queue("default", autocommit=True)
        try:
            queue.enqueue(generate_thumbnail, instance.id)
            logger.info(f"Enqueued thumbnail generation for video id={instance.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue thumbnail generation for video id={instance.id}: {e}")
