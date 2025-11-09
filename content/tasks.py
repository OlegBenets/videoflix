import subprocess
import tempfile
import logging
import os
import cloudinary.uploader
import glob
from .models import Video

logger = logging.getLogger(__name__)

RESOLUTIONS = {
    "480p": "854:480",
    "720p": "1280:720",
    "1080p": "1920:1080",
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
                tmp_file.name,
                "-y",
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
    Convert video into HLS format in multiple resolutions and upload to Cloudinary.
    """
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url
        logger.info(f"Starting HLS conversion for video id={video_id}")

        for resolution, scale in RESOLUTIONS.items():
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, "index.m3u8")

                cmd = [
                    "ffmpeg",
                    "-i", input_url,
                    "-vf", f"scale={scale}",
                    "-c:v", "h264",
                    "-c:a", "aac",
                    "-f", "hls",
                    "-hls_time", "10",
                    "-hls_playlist_type", "vod",
                    output_file,
                    "-y",
                ]
                subprocess.run(cmd, check=True)

                for f in glob.glob(f"{tmp_dir}/*"):
                    cloudinary.uploader.upload(
                        f,
                        folder=f"videoflix/videos/{video.id}/{resolution}/",
                        resource_type="video",
                        overwrite=True,
                    )

                logger.info(f"Uploaded {resolution} version for video id={video_id}")

        logger.info(f"Finished all resolutions for video id={video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed for video id={video_id}: {e}")
    except Exception as e:
        logger.error(f"Error during HLS conversion for video id={video_id}: {e}")
