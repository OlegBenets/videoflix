import logging
import os

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq

from .models import Video
from .tasks import generate_thumbnail, convert_video_from_cloudinary

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Enqueue video processing tasks (HLS conversion, thumbnail generation)
    after a new Video instance is created.
    """
    if created and instance.file:
        queue = django_rq.get_queue("default", autocommit=True)
        tasks = [
            (generate_thumbnail, (instance.id,)),
            (convert_video_from_cloudinary, (instance.id,)),
        ]
        for func, args in tasks:
            try:
                queue.enqueue(func, *args)
                logger.info(f"Enqueued task {func.__name__} for video id={instance.id}")
            except Exception as e:
                logger.error(f"Failed to enqueue {func.__name__} for video id={instance.id}: {e}")
