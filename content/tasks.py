import subprocess
import tempfile
import logging
import cloudinary.uploader
from .models import Video

logger = logging.getLogger(__name__)

RESOLUTIONS = {
    "480p": 854,
    "720p": 1280,
    "1080p": 1920,
}


def generate_thumbnail(video_id):
    """
    Generate a thumbnail (5s in) and upload to Cloudinary.
    """
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
                "-update", "1",
                tmp_file.name,
                "-y"
            ]
            subprocess.run(cmd, check=True)

            upload_result = cloudinary.uploader.upload(
                tmp_file.name,
                folder="videoflix/thumbnails/",
                resource_type="image",
                overwrite=True,
            )

        video.thumbnail_url = upload_result["secure_url"]
        video.save()
        logger.info(f"Thumbnail generated for video id={video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed for video id={video_id}: {e}")
    except Exception as e:
        logger.error(f"Error generating thumbnail for video id={video_id}: {e}")


def convert_video_into_hls(video_id):
    """
    Upload video to Cloudinary and generate HLS streams for multiple resolutions.
    """
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url

        eager_transformations = []
        for res, width in RESOLUTIONS.items():
            eager_transformations.append({
                "format": "m3u8",
                "transformation": {"width": width, "crop": "scale"}
            })

        upload_result = cloudinary.uploader.upload(
            input_url,
            folder=f"videoflix/videos/{video.id}/",
            resource_type="video",
            eager=eager_transformations,
            eager_async=True
        )

        logger.info(f"HLS variants triggered for video id={video_id}")
        return upload_result

    except Video.DoesNotExist:
        logger.error(f"Video {video_id} does not exist")
    except Exception as e:
        logger.error(f"Error uploading HLS for video {video_id}: {e}")