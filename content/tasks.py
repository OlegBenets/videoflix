import subprocess
import tempfile
import logging
import cloudinary.uploader
from .models import Video
logger = logging.getLogger(__name__)


def generate_thumbnail(video_id):
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url

        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:
            cmd = [
                "ffmpeg",
                "-ss", "00:00:05.000",
                "-i", input_url,
                "-vframes", "1",
                "-q:v", "2",
                tmp_file.name,
                "-y"
            ]
            subprocess.run(cmd, check=True)

            upload_result = cloudinary.uploader.upload(
                tmp_file.name,
                folder="videoflix/thumbnails/",
                resource_type="image"
            )

        video.thumbnail_url = upload_result["secure_url"]
        video.save()
        logger.info(f"Thumbnail generated and uploaded for video id={video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed for video id={video_id}: {e}")
    except Exception as e:
        logger.error(f"Error generating thumbnail for video id={video_id}: {e}")


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