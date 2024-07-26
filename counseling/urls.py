from django.urls import path
from . import views

app_name = "counseling"

urlpatterns = [
    # AI 상담
    path("", views.counsel, name="counsel"),

    # 고객 정보 수정
    path("update_log/", views.update_log, name="updateLog"),

    # 상담 바로 종료 시 데이터 삭제
    path("delCounselData/", views.delete_counseling_init_data, name="delCounselData"),

    # 대화 내용 INSERT
    path("ai/", views.ai_model, name="aiModel"),

    # AI 상담 이력
    path("history/", views.history, name="history"),

    # AI 상담 이력 상세 페이지
    path("detail/<int:id>/", views.detail, name="detail"),
]
