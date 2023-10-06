from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()

POSTS_PER_PAGE = 10


def paginate_posts(query_set, page_number):
    paginator = Paginator(query_set, POSTS_PER_PAGE)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = "posts/index.html"
    post_list = Post.objects.all()
    page_number = request.GET.get("page")
    context = {"page_obj": paginate_posts(post_list, page_number)}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = "posts/group_list.html"
    post_list = group.posts.all()
    page_number = request.GET.get("page")
    context = {
        "group": group,
        "page_obj": paginate_posts(post_list, page_number),
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    page_number = request.GET.get("page")
    following = False
    if request.user.is_authenticated:
        follow_list = Follow.objects.filter(
            author=author, user=request.user
        ).exists()
        following = follow_list

    context = {
        "page_obj": paginate_posts(post_list, page_number),
        "author": author,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = Comment.objects.select_related("author").filter(post=post)
    context = {
        "post": post,
        "count": count,
        "button": post.author.username == request.user.username,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"

    if request.method == "POST":
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", request.user)
        return render(request, template, {"form": form})

    form = PostForm()
    return render(request, template, {"form": form})


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    edit_post = get_object_or_404(Post, pk=post_id)

    if edit_post.author != request.user:
        return redirect("posts:post_detail", post_id)

    if request.method == "POST":
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=edit_post,
        )
        form.save()
        return redirect("posts:post_detail", post_id)

    form = PostForm(instance=edit_post)
    context = {"form": form, "is_edit": True, "id": post_id}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    template = "posts:post_detail"
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    user = request.user

    post_list = Post.objects.select_related("group").filter(
        author__following__user=user
    )
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.username != username:
        Follow.objects.get_or_create(user=request.user, author=author)
        template = "posts:profile"
        return redirect(template, username=username)
    return redirect("posts:index")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    obj = Follow.objects.filter(user=request.user, author=author)
    obj.delete()
    template = "posts:profile"
    return redirect(template, username=username)
