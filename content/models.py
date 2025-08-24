from django.db import models

# Create your models here.


class Video(models.Model):
    """
    Model representing a video.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    file = models.FileField(upload_to="videos/", blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=256, default="Uncategorized")

    def __str__(self):
        return self.title
