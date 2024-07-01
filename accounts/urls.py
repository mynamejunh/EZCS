from django.urls import path 
from . import views
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
<<<<<<< HEAD
    #path('signup/', views.signup, name='signup'),
    #path('login/', views.login_view, name='login'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]

=======
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
>>>>>>> d4f9ed381b72492f33f73c56e90cfdc5e49ee743
