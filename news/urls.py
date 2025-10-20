from django.urls import path
from .views import NewsListCreateAPIView, NewsDetailAPIView, NewsLikeAPIView

urlpatterns = [
    path('', NewsListCreateAPIView.as_view(), name='news-list-create'),
    path('<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),
    path('<int:pk>/like/', NewsLikeAPIView.as_view(), name='news-like'),
]
