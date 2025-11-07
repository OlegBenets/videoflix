import logging
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from .models import Video

logger = logging.getLogger(__name__)


def generate_thumbnail(video_id):
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url

        thumbnail_url, options = cloudinary_url(
            input_url,
            resource_type="video",
            format="jpg",
            transformation=[{"start_offset": 5, "width": 640, "crop": "scale"}]
        )

        video.thumbnail_url = thumbnail_url
        video.save()
        logger.info(f"Thumbnail generated for video id={video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except Exception as e:
        logger.error(f"Thumbnail generation failed for video id={video_id}: {e}")


def convert_video_into_hls(video_id):
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url

        upload_result = cloudinary.uploader.upload(
            input_url,
            folder=f"videoflix/videos/{video.id}/",
            resource_type="video",
            format="hls",
            public_id="index",
            overwrite=True
        )

        logger.info(f"Video converted to HLS and uploaded for video id={video_id}")
        logger.info(f"HLS Playlist URL: {upload_result['secure_url']}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except Exception as e:
        logger.error(f"HLS conversion/upload failed for video id={video_id}: {e}")