from django.urls import path 
from . import views

app_name = 'accounts'

urlpatterns = [
    # 로그인
    path('', views.user_login, name='login'),

    # 로그 아웃
    path('logout/', views.user_logout, name='logout'),

    # 이용 약관
    path('consent/', views.consent, name='consent'),

    # 회원 가입
    path('signup/', views.signup, name='signup'),

    # ID 중복 확인
    path('check-username/', views.check_username, name='check_username'),

    # email 중복 확인
    path('check-email/', views.check_email, name='check_email'),

    # phone 중복 확인
    path('check-phone/', views.check_phone, name='check_phone'), 

    # 비밀번호 찾기
    path('searchPW/', views.searchPW, name='searchPW'),

    # 비밀번호 재설정
    path('reset_password/', views.reset_password, name='reset_password'),
]
