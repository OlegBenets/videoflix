from django.http import Http404, HttpResponse
import requests
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import generics
from content.models import Video

class VideosListView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoHLSPlaylistView(APIView):
    """
    Proxy HLS playlist from Cloudinary using the old API URL.
    """

    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(id=movie_id)

            cloudinary_hls_url = str(video.file)
            cloudinary_hls_url = cloudinary_hls_url.replace("/upload/", "/upload/v_hls/")

            r = requests.get(cloudinary_hls_url, timeout=10)
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
    Proxy HLS segment from Cloudinary.
    """

    def get(self, request, movie_id, resolution, segment):
        try:
            video = Video.objects.get(id=movie_id)
            cloudinary_base_url = str(video.file).replace("/upload/", "/upload/v_hls/")
            segment_url = f"{cloudinary_base_url}/{segment}"

            r = requests.get(segment_url, timeout=10)
            if r.status_code != 200:
                raise Http404("Segment not found on Cloudinary")

            return HttpResponse(
                r.content,
                content_type="video/mp2t",
                status=200
            )

        except Video.DoesNotExist:
            raise Http404("Video not found")
