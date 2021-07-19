from django.urls import path
from . import views


urlpatterns = [
    path('posts/', views.list_posts),
    path('login_old/', views.request_login),
    path('signup_old/', views.signup),
    path('categories/', views.get_categories),
    path('create_post/', views.create_post),
    path('category/create/', views.create_category),
    path('category/delete/', views.delete_category),
    path('category/update/', views.update_category),
    path('is_admin/', views.is_admin),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
]
