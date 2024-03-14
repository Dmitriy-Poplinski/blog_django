from django.urls import path
from .views import (
    post_list,
    post_detail,
    PostListView,
    post_share,
    post_comment,
)

app_name = "blog"

urlpatterns = [
    path("", post_list, name="post-list"),
    path("tag/<slug:tag_slug>/", post_list, name="post-list-by-tag"),
    # path("", PostListView.as_view(), name="post-list"),
    path("<int:year>/<int:month>/<int:day>/<slug:post>/", post_detail, name="post-detail"),
    path("<int:post_id>/share/", post_share, name="post-share"),
    path("<int:post_id>/comment/", post_comment, name="post-comment"),
]
