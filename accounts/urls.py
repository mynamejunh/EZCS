from django.urls import path 
from . import views
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
<<<<<<< HEAD
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('userSetting/', views.userSetting_View, name='userSetting'),
=======
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    path('searchPW/', views.searchPW, name='searchPW'),

    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),

>>>>>>> 307b05c8221d89bfb6c303c85b6296ecde256078
]
