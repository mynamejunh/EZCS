from django.urls import path 
from . import views

app_name = 'main'

urlpatterns = [
    # 대시보드
    path('', views.user_dashboard, name='user_dashboard'),

    # 달력 정보
    path('get_calendar/<start>/<end>', views.get_calendar, name='get_calendar'),

    # 공지 사항 상세
    path('notice/<int:id>/', views.notice_detail, name='notice_detail'),

    # 비밀번호 확인
    path('verify-password/', views.verify_password, name='verify_password'),

    # 내정보 수정
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # 이용약관
    path('contract/', views.contract, name='contract'),

    # 개인정보 처리방침
    path('privacy/', views.privacy, name='privacy'),
]
