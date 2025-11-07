from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import generics
from content.models import Video
import cloudinary
import requests


class VideosListView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoHLSPlaylistView(APIView):
    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(id=movie_id)
            public_id = video.file.public_id  
            cloud_url = f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/video/upload/vod/{public_id}/index.m3u8"
            r = requests.get(cloud_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Playlist not found")
            return HttpResponse(r.content, content_type="application/vnd.apple.mpegurl")
        except Video.DoesNotExist:
            raise Http404("Video not found")


class GetVideoHLSSegment(APIView):
    def get(self, request, movie_id, resolution, segment):
        try:
            video = Video.objects.get(id=movie_id)
            public_id = video.file.public_id
            cloud_url = f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/video/upload/vod/{public_id}/{segment}"
            r = requests.get(cloud_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Segment not found")
            return HttpResponse(r.content, content_type="video/mp2t")
        except Video.DoesNotExist:
            raise Http404("Video not found")
        except Exception:
            raise Http404("Segment not found")
