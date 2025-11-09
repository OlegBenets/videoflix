import subprocess
import os
import logging
from django.conf import settings
from .models import Video
import cloudinary.uploader
import requests
import tempfile


logger = logging.getLogger(__name__)


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


def convert_video_from_cloudinary(video_id):
    """
    Download the video from Cloudinary and convert it into HLS locally.
    """
    try:
        video = Video.objects.get(id=video_id)
        input_url = video.file.url

        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_video:
            r = requests.get(input_url, stream=True)
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp_video.write(chunk)
            tmp_video.flush()  

            convert_video_into_hls(tmp_video.name, video_id)

    except Video.DoesNotExist:
        logger.error(f"Video {video_id} does not exist")
    except requests.RequestException as e:
        logger.error(f"Failed to download video {video_id} from Cloudinary: {e}")
    except Exception as e:
        logger.error(f"Error converting video {video_id} to HLS: {e}")


def convert_video_into_specific_resolution(resolution, scale, input_file, video_id):
    """
    Convert video into a specific resolution.
    """
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id), resolution)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "index.m3u8")

        cmd = [
            "ffmpeg",
            "-i", input_file,
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
        logger.info(f"Video converted to {resolution} for video id={video_id}")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed for video id={video_id}, resolution={resolution}: {e}")


def convert_video_into_hls(input_file, video_id):
    """
    Convert video into HLS format.
    """
    RESOLUTION_MAP = {
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080",
    }

    for resolution, scale in RESOLUTION_MAP.items():
        convert_video_into_specific_resolution(resolution, scale, input_file, video_id)
