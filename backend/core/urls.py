from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"

urlpatterns = [
    path('',views.feed, name='feed'),
    path('signup/',views.signup, name='signup'),
    path('login/',auth_views.LoginView.as_view(), name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('post/<int:pk>/',views.post_detail, name='post_detail'),
    path('post/<int:pk>/like',views.like_post, name='like_post'),
     path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<str:username>/', views.chat_view, name='chat_view'),
    path('api/search-users/', views.search_users, name='search_users'),
]
