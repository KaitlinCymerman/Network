import json
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow, Like


def index(request):
    # Create posts
    if request.method == "POST":
        Post.objects.create(user = request.user, post = request.POST["post"], date = datetime.now(), likes = 0)

    # Get all posts, ordered by time/date posted
    posts = Post.objects.all().order_by('-date')
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()

    # Every 10 posts, allow users to go to next page or previous to see other posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    return render(request, "network/index.html", {
        "page_obj": paginator.get_page(page_number)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    username = User.objects.get(id=username)
    follower = request.user
    follow_button = "Follow" if Follow.objects.filter(
        follower=follower, following=username).count() == 0 else "Unfollow"

    if request.method == "POST":
        if request.POST["follow_button"] == "Follow":
            follow_button = "Unfollow"
            Follow.objects.create(follower=follower, following=username)
        else:
            follow_button = "Follow"
            Follow.objects.filter(follower=follower, following=username).delete()
    # Get all posts, ordered by time/date posted
    posts = Post.objects.filter(user=username.id).order_by('-date')
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()
    # Every 10 posts, allow users to go to next page or previous to see other posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    return render(request, "network/profile.html", {
        "username": username,
        "followers": Follow.objects.filter(following=username).count(),
        "following": Follow.objects.filter(follower=username).count(),
        "page_obj": paginator.get_page(page_number),
        "follow_button": follow_button
    })


def following(request):
    user = request.user
    # Get followers
    following = Follow.objects.filter(follower=user)
    # Get all posts, ordered by time/date posted
    posts = Post.objects.filter(user__in=following.values('following_id')).order_by('-date')
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()

    # Every 10 posts, allow users to go to next page or previous to see other posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    return render(request, "network/following.html", {
        "page_obj": paginator.get_page(page_number)
    })


@csrf_exempt
def edit(request, post_id):
    # Allow users to edit their own posts
    post = Post.objects.get(id=post_id)
    data = json.loads(request.body)
    data.get("post")
    post.post = data["post"]
    # Once post is edited, save it
    post.save()
    return HttpResponse(status=204)

@csrf_exempt
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Get likes
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("like"):
            # Like post
            Like.objects.create(user=user, post=post)
            post.likes = Like.objects.filter(post=post).count()
        else:
            # Unlike post
            Like.objects.filter(user=user, post=post).delete()
            post.likes = Like.objects.filter(post=post).count()
        # Save like/unlike to coutner
        post.save()
        return HttpResponse(status=201)