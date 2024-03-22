from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count, QuerySet

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(
        request: HttpRequest,
        tag_slug: str | None = None
) -> HttpResponse:
    posts: QuerySet[Post] = Post.published.all()

    tag: Tag | None = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    paginator: Paginator = Paginator(posts, 3)
    page_number: int = request.GET.get("page", 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(
        request: HttpRequest,
        year: int,
        month: int,
        day: int,
        post: str,
) -> HttpResponse:
    post: Post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments: QuerySet[Comment] = post.comments.filter(active=True)
    form: CommentForm = CommentForm()

    post_tags_ids: list[int] = post.tags.values_list("id", flat=True)
    similar_posts: QuerySet[Post] = (
        Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    )
    similar_posts: QuerySet[Tag] = (
        similar_posts.annotate(same_tags=Count("tags")).order_by(
            "-same_tags", "-publish"
        )
    )[:4]

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(
        request: HttpRequest,
        post_id: int
) -> HttpResponse:
    post: Post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent: bool = False

    if request.method == "POST":
        form: EmailPostForm = EmailPostForm(request.POST)

        if form.is_valid():
            cd: dict = form.cleaned_data
            post_url: str = request.build_absolute_uri(post.get_absolute_url())
            subject: str = f"{cd['name']} reccomend you to read " f"{post.title}"
            message: str = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            # TODO Need to configure SMTP Server
            send_mail(subject, message, "super.shepard2@gmail.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {
            "post": post,
            "form": form,
            "sent": sent,
        },
    )


@require_POST
def post_comment(
        request: HttpRequest,
        post_id: HttpResponse
) -> HttpResponse:
    post: Post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )
    comment: Comment | None = None
    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post

        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {
            "post": post,
            "form": form,
            "comment": comment,
        },
    )
