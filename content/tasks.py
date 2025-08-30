import subprocess
import os
import logging
from django.conf import settings
from .models import Video

logger = logging.getLogger(__name__)

def generate_thumbnail(video_id):
    """
    Generate a thumbnail for the video.
    """
    try:
        video = Video.objects.get(id=video_id)
        input_path = video.file.path

        output_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video.id}.jpg")

        cmd = [
            "ffmpeg",
            "-ss", "00:00:05.000",
            "-i", input_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path,
            "-y", 
        ]

        subprocess.run(cmd, check=True)
        video.thumbnail_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}thumbnails/{video.id}.jpg"
        video.save()
        logger.info(f"Thumbnail generated for video id={video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with id={video_id} does not exist")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed for video id={video_id}: {e}")


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
