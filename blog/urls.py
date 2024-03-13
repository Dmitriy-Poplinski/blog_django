from django.urls import path
from .views import post_list, post_detail, PostListView

app_name = "blog"

urlpatterns = [
    # path("", post_list, name="post-list"),
    path("", PostListView.as_view(), name="post-list"),
    path("<int:year>/<int:month>/<int:day>/<slug:post>", post_detail, name="post-detail"),
]
