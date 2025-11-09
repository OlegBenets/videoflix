from django.http import Http404, HttpResponse
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
    View to stream HLS playlist for a video.
    """
    def get(self, request, movie_id, resolution):

        index_m3u8_path = os.path.join(
            settings.MEDIA_ROOT, "videos", str(movie_id), resolution, "index.m3u8"
        )

        if not os.path.exists(index_m3u8_path):
            raise Http404("Playlist not found")

        with open(index_m3u8_path, "r") as f:
            playlist_content = f.read()

        return HttpResponse(
            playlist_content, 
            content_type="application/vnd.apple.mpegurl",
            status=200
        )


class GetVideoHLSSegment(APIView):
    """
    View to stream a specific HLS segment for a video.
    """

    def get(self, request, movie_id, resolution, segment):
        segment_path = os.path.join(
            settings.MEDIA_ROOT, "videos", str(movie_id), resolution, segment
        )

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        with open(segment_path, "rb") as f:
            segment_file = f.read()

        return HttpResponse(
            segment_file, 
            content_type="video/mp2t",
            status=200
        )
