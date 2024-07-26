from django.urls import path 
from . import views

app_name = 'education'

urlpatterns = [
    # AI 트레이너 페이지
    path('', views.chat_view, name='chat_view'),

    # AI 트레이너 바로 종료 시 데이터 삭제
    path('del_train_data', views.delete_training_init_data, name='delTrainData'),

    # AI 트레이너 이력 페이지
    path('edu_history/', views.edu_history, name='edu_history'),

    # AI 트레이너이력 상세 페이지
    path('edu_details/<int:id>/', views.edu_details, name='edu_details'),

    # 퀴즈 페이지 
    path('quiz/', views.quiz, name='quiz'),

    # 퀴즈 이력 페이지
    path('quiz_history/', views.quiz_history, name='quiz_history'),

    # 퀴즈 이력 상세페이지
    path('quiz_details/<int:log_id>/', views.quiz_details, name='quiz_details'),
]