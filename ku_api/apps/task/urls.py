from django.urls import path
from .views import ClaimMinedToken, ListTask, ClaimTaskToken, RecentEarningView, GetCompletedTask


urlpatterns = [
    path("claim-token/<str:pk>/", ClaimMinedToken.as_view(), name="tasks"),
    path("task-claim/<str:pk>/", ClaimTaskToken.as_view(), name="claim-task-token"),
    path("", ListTask.as_view(), name="list-task"),
    path("recent-earnings", RecentEarningView.as_view(), name="recent-earnings"),
    path('completed-task/', GetCompletedTask.as_view(), name="get-completed-task")
]
