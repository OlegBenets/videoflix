from django.db import models
from cloudinary.models import CloudinaryField


class Video(models.Model):
    """
    Model representing a video.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    file = CloudinaryField(resource_type="video", folder="videoflix/videos/", blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=256, default="Uncategorized")

    def __str__(self):
        return self.title
