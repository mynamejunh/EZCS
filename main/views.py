from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import User, CounselorProfile  
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from management.models import Board
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from counseling.models import Log as CounselLog
from education.models import Log as EducationLog, QuizHistory
from django.db.models.functions import TruncDate
from django.db.models import Count

def user_dashboard(request):
    counsel_data = CounselLog.objects.filter(auth_user=request.user.id)\
                                     .annotate(date=TruncDate('create_time'))\
                                     .values('date')\
                                     .annotate(count=Count('id'))\
                                     .values('date', 'count')
    
    # EducationLog 데이터를 'create_time' 기준으로 그룹화
    education_data = EducationLog.objects.filter(auth_user=request.user.id)\
                                         .annotate(date=TruncDate('create_time'))\
                                         .values('date')\
                                         .annotate(count=Count('id'))\
                                         .values('date', 'count')
    
    # QuizHistory 데이터를 'create_time' 기준으로 그룹화
    quiz_data = QuizHistory.objects.filter(auth_user=request.user.id)\
                                   .annotate(date=TruncDate('create_time'))\
                                   .values('date')\
                                   .annotate(count=Count('id'))\
                                   .values('date', 'count')
    
    # JSON으로 변환할 수 있도록 데이터 병합
    data = list(counsel_data) + list(education_data) + list(quiz_data)


    notices = Board.objects.filter(flag=0).order_by('-create_time')
    paginator = Paginator(notices, 10)
    page = request.GET.get('page')
    notices = paginator.get_page(page)
    return render(request, 'main/index.html', {'notices': notices, 'data':data})

def notice_detail(request, id):
    notice = get_object_or_404(Board, id=id)
    is_image = False
    if notice.file:
        is_image = notice.file.url.lower().endswith(('.jpg', '.jpeg', '.png'))
    return render(request, 'main/notice_detail.html', {'notice': notice, 'is_image': is_image})

def start_ezcs(request):
    return render(request, 'main/startezcs.html')

@login_required
def edit_profile(request):
    user = request.user
    profile = get_object_or_404(CounselorProfile, auth_user=user)  # 수정된 부분

    if request.method == 'POST':
        user.first_name = request.POST.get('name')
        user.email = request.POST.get('email') 
        profile.phone_number = request.POST.get('phone_number')  # CounselorProfile 모델의 phone_number 필드 수정
        profile.birth_date = request.POST.get('birth_date')  # CounselorProfile 모델의 birth_date 필드 수정
        profile.address_code = request.POST.get('address_code')  # CounselorProfile 모델의 address_code 필드 수정
        profile.address = request.POST.get('address')  # CounselorProfile 모델의 address 필드 수정
        profile.address_detail = request.POST.get('address_detail')  # CounselorProfile 모델의 address_detail 필드 수정
        password = request.POST.get('password')
        if password:
            try:
                validate_password(password, user)
                user.password = make_password(password)
            except ValidationError as e:
                return JsonResponse({'result': False, 'msg': '비밀번호가 유효하지 않습니다. ' + ' '.join(e.messages)})

        user.save()
        profile.save()  
        return JsonResponse({'result': True, 'msg': '회원정보가 성공적으로 수정되었습니다.'})

    return render(request, 'main/edit_profile.html', {'user': user, 'profile': profile})  # 프로필 정보 전달

def contract(request):
    return render(request, 'main/contract.html')

def privacy(request):
    return render(request, 'main/privacy.html')


@csrf_exempt
def verify_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        authenticated_user = authenticate(username=user.username, password=password)

        if authenticated_user is not None:
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False})

    return JsonResponse({'valid': False})