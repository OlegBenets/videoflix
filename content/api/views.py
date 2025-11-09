from django.http import Http404, HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import VideoSerializer
from content.models import Video
import cloudinary

class VideosListView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoHLSPlaylistView(APIView):
    """
    Redirects the request to the Cloudinary HLS playlist for the given video and resolution.
    """
    def get(self, request, movie_id, resolution):
        try:
            Video.objects.get(id=movie_id)

            cloud_url = (
                f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/"
                f"video/upload/videoflix/videos/{movie_id}/{resolution}/index.m3u8"
            )

            return HttpResponseRedirect(cloud_url)

        except Video.DoesNotExist:
            raise Http404("Video not found")
        except Exception as e:
            raise Http404(f"Error loading playlist: {e}")


class GetVideoHLSSegment(APIView):
    def get(self, request, movie_id, resolution, segment):
        try:
            Video.objects.get(id=movie_id)

            cloud_url = (
                f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/"
                f"video/upload/vod/videoflix/videos/{movie_id}/{resolution}/{segment}"
            )

            import requests
            r = requests.get(cloud_url, timeout=10)
            if r.status_code != 200:
                raise Http404(f"Segment not found for {resolution}")

            return HttpResponse(r.content, content_type="video/mp2t")

        except Video.DoesNotExist:
            raise Http404("Video not found")
        except Exception as e:
            raise Http404(f"Error loading segment: {e}")