from rest_framework import serializers
from content.models import Video


class VideoSerializer(serializers.ModelSerializer):#
    """
    Serializer for Video model.
    """

    class Meta:
        model = Video
        fields = "__all__"
