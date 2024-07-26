from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, DateField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from accounts.models import CounselorProfile  
from counseling.models import Log as CounselLog
from education.models import Log as EducationLog, QuizHistory
from management.models import Board


def user_dashboard(request):
    """
        메인 페이지 대시보드
    """
    notices = Board.objects.filter(flag=0).order_by('-create_time')
    paginator = Paginator(notices, 10)
    page = request.GET.get('page')
    notices = paginator.get_page(page)
    return render(request, 'main/index.html', {'notices': notices})


def get_calendar(request, start, end):
    """
    사용자의 요청에 따라 로그 데이터를 날짜별로 조회하여 JSON 형식으로 반환합니다.

    :param request: HTTP 요청 객체
    :param start: 조회 시작 날짜 (형식: 'YYYY-MM-DD')
    :param end: 조회 종료 날짜 (형식: 'YYYY-MM-DD')
    :return: 날짜별 로그 수와 모델 정보를 포함하는 JSON 응답
    """

    # 슈퍼유저인 경우 모든 사용자의 로그를 조회, 그렇지 않으면 현재 사용자의 로그를 조회
    if request.user.is_superuser:
        counsel_data = get_log_data(CounselLog, start, end)
        education_data = get_log_data(EducationLog, start, end)
        quiz_data = get_log_data(QuizHistory, start, end)
    else:
        counsel_data = get_log_data(CounselLog, start, end, request.user.id)
        education_data = get_log_data(EducationLog, start, end, request.user.id)
        quiz_data = get_log_data(QuizHistory, start, end, request.user.id)
    
    # 모든 모델 데이터 합치기
    data = counsel_data + education_data + quiz_data

    # JSON 형식으로 응답 반환
    return JsonResponse(data, safe=False)


def notice_detail(request, id):
    """
    공지 사항 상세
    """
    notice = get_object_or_404(Board, id=id)
    is_image = False
    if notice.file:
        is_image = notice.file.url.lower().endswith(('.jpg', '.jpeg', '.png'))
    return render(request, 'main/notice_detail.html', {'notice': notice, 'is_image': is_image})


@csrf_exempt
def verify_password(request):
    """
    비밀번호 확인
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        authenticated_user = authenticate(username=user.username, password=password)

        if authenticated_user is not None:
            request.session['password_verified'] = True
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False})

    return JsonResponse({'valid': False})


def edit_profile(request):
    """
    내 정보 수정
    """
    if not request.session.get('password_verified'):
        return redirect('main:user_dashboard')  # 비밀번호 확인 안된 경우 대시보드로 리다이렉트

    user = request.user
    profile = get_object_or_404(CounselorProfile, auth_user=user)  # 수정된 부분
    email_local, email_domain = user.email.split('@')


    if request.method == 'POST':
        user.first_name = request.POST.get('name')
        user.email = request.POST.get('email') 

        profile.phone_number = request.POST.get('phone_number')
        profile.birth_date = request.POST.get('birth_date')
        profile.address_code = request.POST.get('address_code')
        profile.address = request.POST.get('address')
        profile.address_detail = request.POST.get('address_detail')
        password = request.POST.get('password')
        if password:
            try:
                validate_password(password, user)
                user.password = make_password(password)
            except ValidationError as e:
                return JsonResponse({'result': False, 'msg': '비밀번호가 유효하지 않습니다. ' + ' '.join(e.messages)})

        user.save()
        profile.save()  
        request.session['password_verified'] = False  # 수정 후 세션 상태 초기화

        return JsonResponse({'result': True, 'msg': '회원정보가 성공적으로 수정되었습니다.'})
    email_domains = ["naver.com", "gmail.com", "daum.net", "nate.com"]

    return render(request, 'main/edit_profile.html', {
        'user': user,
        'profile': profile,
        'email_local': email_local,
        'email_domain': email_domain,
        'email_domains': email_domains
    })


def contract(request):
    """
        이용약관 페이지
    """
    return render(request, 'main/contract.html')


def privacy(request):
    """
        개인정보 처리방침 페이지
    """
    return render(request, 'main/privacy.html')


def get_log_data(model_class, start, end, request_user_id=None):
    """
    특정 모델 클래스의 로그 데이터를 조회하여, 주어진 기간 동안의 로그 수를 날짜별로 집계합니다.

    :param model_class: 로그를 조회할 모델 클래스 (예: CounselLog, EducationLog, QuizHistory)
    :param start: 조회 시작 날짜 (형식: 'YYYY-MM-DD')
    :param end: 조회 종료 날짜 (형식: 'YYYY-MM-DD')
    :param request_user_id: 필터링할 사용자 ID (옵션, None일 경우 모든 사용자의 로그 조회)
    :return: 날짜별 로그 수와 모델 정보를 포함하는 딕셔너리 리스트
    """
    # 주어진 기간 동안의 데이터 필터링
    queryset = model_class.objects.filter(create_time__range=[start+" 09:00:00", datetime.strptime(end+" 09:00:00", "%Y-%m-%d %H:%M:%S")])
    
    # 사용자가 지정된 경우, 해당 사용자 ID로 추가 필터링
    if request_user_id is not None:
        queryset = queryset.filter(auth_user=request_user_id)
    
    # 날짜별로 집계할 수 있도록 날짜 필드 생성 및 로그 수 계산
    queryset = queryset.annotate(
        date=Cast('create_time', output_field=DateField())
    ).values('date').annotate(count=Count('id')).order_by('date')

    # 결과를 딕셔너리 리스트로 변환
    return [{'type': str(model_class), 'date': item['date'], 'count': item['count']} for item in queryset]