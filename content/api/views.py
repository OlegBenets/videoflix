from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import generics
from content.models import Video
import requests
import cloudinary

class VideosListView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoHLSPlaylistView(APIView):
    """
    Proxy for Cloudinary HLS playlist.
    """

    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(id=movie_id)
            cloudinary_url = f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/video/upload/vod/videoflix/videos/{video.id}/{resolution}/index.m3u8"

            r = requests.get(cloudinary_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Playlist not found on Cloudinary")

            return HttpResponse(
                r.content,
                content_type="application/vnd.apple.mpegurl",
                status=200
            )

        except Video.DoesNotExist:
            raise Http404("Video not found")


class GetVideoHLSSegment(APIView):
    """
    Proxy for HLS segments from Cloudinary.
    """

    def get(self, request, movie_id, resolution, segment):
        try:
            cloudinary_url = f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/video/upload/vod/videoflix/videos/{movie_id}/{resolution}/{segment}"
            r = requests.get(cloudinary_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Segment not found on Cloudinary")

            return HttpResponse(
                r.content,
                content_type="video/mp2t",
                status=200
            )

        except Exception:
            raise Http404("Segment not found")
