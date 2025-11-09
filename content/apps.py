from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content"

    def ready(self):
        import content.signals

        if os.environ.get("DYNO") and os.environ.get("DYNO").startswith("web"):
            from .models import Video
            import django_rq
            from django.conf import settings
            from .tasks import convert_video_from_cloudinary

            queue = django_rq.get_queue("default", autocommit=True)

            for video in Video.objects.all():
                base_path = os.path.join(settings.MEDIA_ROOT, "videos", str(video.id))
                
                if not os.path.exists(base_path) or not os.listdir(base_path):
                    try:
                        queue.enqueue(convert_video_from_cloudinary, video.id)
                        logger.info(f"Enqueued HLS generation for video id={video.id}")
                    except Exception as e:
                        logger.error(f"Failed to enqueue HLS for video id={video.id}: {e}")