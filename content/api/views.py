from django.http import Http404, HttpResponse
import requests
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import generics
from content.models import Video
from django.conf import settings
import os


class VideosListView(generics.ListAPIView):
    """
    View to list all videos.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoHLSPlaylistView(APIView):
    """
    Stream HLS playlist from Cloudinary, keeping original URLs for frontend.
    """

    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(id=movie_id)

            cloudinary_base_url = f"https://res.cloudinary.com/docbhvsjl/video/upload/vod/videos/{video.id}/{resolution}/index.m3u8"

            r = requests.get(cloudinary_base_url, timeout=10)
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
    Stream a HLS segment from Cloudinary.
    """

    def get(self, request, movie_id, resolution, segment):
        try:
            cloudinary_segment_url = f"https://res.cloudinary.com/docbhvsjl/video/upload/vod/videos/{movie_id}/{resolution}/{segment}"
            r = requests.get(cloudinary_segment_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Segment not found on Cloudinary")

            return HttpResponse(
                r.content,
                content_type="video/mp2t",
                status=200
            )

        except Video.DoesNotExist:
            raise Http404("Video not found")
