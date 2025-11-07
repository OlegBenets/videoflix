import logging
import os

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq

from .models import Video
from .tasks import generate_thumbnail, convert_video_into_hls

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
            (convert_video_into_hls, (instance.file.path, instance.id)),
        ]
        for func, args in tasks:
            try:
                queue.enqueue(func, *args)
                logger.info(f"Enqueued task {func.__name__} for video id={instance.id}")
            except Exception as e:
                logger.error(f"Failed to enqueue {func.__name__} for video id={instance.id}: {e}")


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes the video file and thumbnail from the filesystem
    when the corresponding Video object is deleted.
    """
    if not instance.file:
        return

    paths_to_delete = [
        instance.file.path,
        os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{instance.id}.jpg")
    ]

    for path in paths_to_delete:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted file {path}")
