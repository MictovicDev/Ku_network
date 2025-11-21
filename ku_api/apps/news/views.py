from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from .models import News
from rest_framework.response import Response
from .serializers import NewsSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.
class NewsListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        news_posts = News.objects.all()
        serializer = NewsSerializer(news_posts, many=True, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=200)

    def post(self, request):
        serializer = NewsSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response({"status": "success", "data": serializer.data}, status=201)
        return Response({"status": "error", "errors": serializer.errors}, status=400)


class NewsDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # parser_classes = [MultiPartParser, FormParser]  # Add this line

    def get_object(self, pk):
        return get_object_or_404(News, pk=pk)

    def get(self, request, pk):
        news = self.get_object(pk)
        serializer = NewsSerializer(news, context={"request": request})
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        news = self.get_object(pk)
        if news.author != request.user:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NewsSerializer(
            news, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        news = self.get_object(pk)
        if news.author != request.user:
            return Response(
                {"error": "You do not have permission to delete this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        news.delete()
        return Response(
            {"status": "success", "message": "Post deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class NewsLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        news.likes_count += 1
        news.save()
        return Response(
            {"status": "success", "likes_count": news.likes_count},
            status=status.HTTP_200_OK,
        )
