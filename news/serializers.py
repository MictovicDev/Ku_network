from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    image1_url = serializers.SerializerMethodField(read_only=True)
    image2_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image1', 'image2',
            'image1_url', 'image2_url',
            'author', 'author_name', 'likes_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['likes_count', 'created_at', 'updated_at', 'author', 'image1_url', 'image2_url']

    def get_image1_url(self, obj):
        if obj.image1:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image1.url)
            return obj.image1.url
        return None

    def get_image2_url(self, obj):
        if obj.image2:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image2.url)
            return obj.image2.url
        return None
