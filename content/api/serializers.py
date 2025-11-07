from rest_framework import serializers
from content.models import Video
from content.tasks import generate_thumbnail_if_missing


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video model.
    """

    class Meta:
        model = Video
        fields = "__all__"
        
    def to_representation(self, instance):
  
        generate_thumbnail_if_missing(instance)
        return super().to_representation(instance)
