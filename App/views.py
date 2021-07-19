"""
Programing and algorithms 2 Assignment
Student: Ionut Petrescu
ID: D19124760
Course: DT249
Stage 2

Django API
"""
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework import generics
from . import models
# Create your views here.


@permission_classes([AllowAny])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


def get_categories(request):
    return JsonResponse({'categories': models.Category.get_categories()})


def list_posts(request):
    if "category" in request.GET.keys():
        posts = models.Post.objects.filter(category=models.Category.get_from_description(request.GET["category"]))
    else:
        posts = models.Post.objects.all()
    lst = []
    if posts:
        for post in posts:
            d = post.as_dict
            lst.append(d)

    return JsonResponse({'posts': lst}, status=200)


def signup(request):
    """
    I wrote this function before you gave us the tip to use Django rest framework
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return JsonResponse({}, status=200)


def request_login(request):
    """
    I wrote this function before you gave us the tip to use Django rest framework
    """
    print(request)
    if request.method == 'GET':
        return JsonResponse({"message": "Please submit POST request"}, status=200)
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        print("login successfull")

        return JsonResponse({"user_id": user.id}, status=200)
    else:
        return JsonResponse({"message": "Failed to login"}, status=401)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_post(request):
    user = request.user
    category = models.Category.get_from_description(request.POST["category"])
    post = models.Post.objects.create(
        author=user,
        category=category,
        title=request.POST["title"],
        content=request.POST["content"]
        )

    return JsonResponse({"Message": "Post created"}, status=200)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_category(request):
    try:
        post = models.Category.objects.create(
            description=request.POST["description"],
            hashtag=request.POST["hashtag"]
            )

        return JsonResponse({"Message": "Category created"}, status=201)
    except:
        return JsonResponse({"Message": "A category with that description already exists"}, status=409)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_category(request):
    try:
        category = models.Category.get_from_description(request.POST["category"])
        category.description = request.POST["new_description"]
        category.hashtag = request.POST["new_hashtag"]
        category.save()
        return JsonResponse({"Message": "Category was changed"}, status=200)
    except:
        return JsonResponse({"Failed": "Something went wrong"}, status=409)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_category(request):
    cat_object = models.Category.get_from_description(request.POST["category"])
    models.Category.delete(cat_object)

    return JsonResponse({"Message": "Category deleted"}, status=200)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def is_admin(requests):
    return JsonResponse({"Message": "User has admin privilege"}, status=200)
