from django.urls import path 
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'accounts'

urlpatterns = [
<<<<<<< HEAD
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('userSetting/', views.userSetting_View, name='userSetting'),
]
=======

    #path('signup/', views.signup, name='signup'),
    #path('login/', views.login_view, name='login'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
>>>>>>> acfe340e4b4a4a5de7d8011315378812c1d2e564
