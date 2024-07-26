from django.urls import path 
from . import views

app_name = 'management'

urlpatterns = [
    path('list/<str:flag>/', views.list, name='list'),
    path('detail/<int:id>/<str:flag>/', views.detail, name='detail'),
    path('edit/<int:id>/<str:flag>/', views.edit, name='edit'),
    path('update_auth/<int:id>/<int:status>', views.update_auth, name='update_auth'),
    path('adminsignup', views.adminsignup, name='adminsignup'),
    path('admincheck-username/', views.admincheck_username, name='admincheck-username'),
    path('admincheck-email/', views.admincheck_email, name='admincheck-email'),
    path('admincheck-phone/', views.admincheck_phone, name='admincheck-phone'), 

    # 공지사항 목록
    path('board/', views.board_list, name='board_list'),

    # 공지사항 작성
    path('board/create/', views.board_create, name='board_create'),

    # 공지사항 상세보기
    path('board/<int:id>/', views.board_detail, name='board_detail'),

    # 공지사항 상세보기
    path('board/<int:id>/board_edit', views.board_edit, name='board_edit'),

    # 삭제 URL 추가
    path('board/<int:id>/delete/', views.board_delete, name='board_delete'),
]