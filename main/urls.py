from django.urls import path 
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
<<<<<<< HEAD
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
=======
>>>>>>> 783d685edba33a5b57c4cf9911d75b11976edfac
]
