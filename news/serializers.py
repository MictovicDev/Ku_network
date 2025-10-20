from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source='author.username', read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image', 'author_name',
            'image_url','author', 'likes_count',
            'created_at', 'updated_at', 'note'
        ]
        read_only_fields = ['likes_count', 'created_at',
                            'updated_at', 'author', 'image1_url', 'image2_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

