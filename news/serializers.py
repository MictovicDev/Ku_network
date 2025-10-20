from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image1', 'image2',
            'author', 'author_name', 'likes_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['likes_count', 'created_at', 'updated_at', 'author']
