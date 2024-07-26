from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import *
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import Board
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage


def list(request, flag):
    """
    직원 관리 페이지
    """
    search_select = request.GET.get("searchSelect", "")
    search_text = request.GET.get("searchText", "")
    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")
    superuser_query = Q()

    if flag == 'm':
        superuser_query &= Q(auth_user__is_superuser=False)
        superuser_query |= Q(active_status=1)
        superuser_query |= Q(active_status=2)
        superuser_query |= Q(active_status=3)
    elif flag == 'ad':
        superuser_query &= Q(auth_user__is_superuser=True)
    else:
        superuser_query &= Q(auth_user__is_superuser=False)
        superuser_query &= Q(active_status=0)
    
    search_query = Q()
    if search_select:
        valid_fields = {
            'name': 'auth_user__first_name__icontains',
            'id': 'auth_user__username__icontains',
            'email': 'auth_user__email__icontains',
        }

        if search_select == 'all':
            for val in valid_fields.values():
                search_query |= Q(**{val: search_text})
        else:
            search_field = valid_fields[search_select]
            search_query = Q(**{search_field: search_text})

    date_query = Q()
    if not (start_date and end_date):
        one_month_ago = datetime.now() - timedelta(days=30)
        start_date = one_month_ago.strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    date_query = Q(auth_user__date_joined__range=[start_date+" 09:00:00", datetime.strptime(end_date+" 09:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)])

    if flag == 'ad':
        data = AdministratorProfile.objects.filter(superuser_query & search_query & date_query)
    else:
        data = CounselorProfile.objects.filter(superuser_query & search_query & date_query)
    
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    data = paginator.get_page(page)
    
    for profile in data:
        profile.masked_name = mask_name(profile.auth_user.first_name)

    context = {
        'flag': flag,
        'data': data,
        'searchSelect': search_select,
        'searchText': search_text,
        'startDate': start_date,
        'endDate': end_date,
        'is_paginated': data.has_other_pages(),
    }

    return render(request, 'management/list.html', context)


def detail(request, id, flag):
    """
    유저 상세 페이지
    
    """
    if flag == 'ad':
        data = get_object_or_404(AdministratorProfile, id=id)
    else:
        data = get_object_or_404(CounselorProfile, id=id)

    context = {
        'flag': flag,
        'data': data
    }
    return render(request, 'management/detail.html', context)


def edit(request, id, flag):
    """
    개인정보 수정
    """
    if flag == 'ad':
        user_profile = get_object_or_404(AdministratorProfile, id=id)
    else:
        user_profile = get_object_or_404(CounselorProfile, id=id)
        
    auth_user = user_profile.auth_user
    
    if request.method == 'GET':
        context = {
            'flag': flag,
            'user': user_profile
        }
        return render(request, 'management/edit.html', context)
    else:
        auth_user.username = request.POST.get('loginUsername')
        auth_user.first_name = request.POST.get('name')
        auth_user.email = request.POST.get('emailLocal') + '@' + request.POST.get('emailDomain')
        user_profile.phone_number = request.POST.get('phone')
        user_profile.department = request.POST.get('department')
        user_profile.birth_date = request.POST.get('birth_date')
        user_profile.address_code = request.POST.get('addressCode')
        user_profile.address = request.POST.get('address')
        user_profile.address_detail = request.POST.get('addressDetail')
        user_profile.active_status = request.POST.get('active_status')
        user_profile.save()
        auth_user.save()
        return redirect("management:detail", id=id, flag=flag)
    
    
def update_auth(request, id, status):
    """
    UPDATE counselor_profile SET active_status = ?
    """
    user = CounselorProfile.objects.get(id=id)
    user.active_status = status
    user.save()
    
    flag = 'm'
    if status == 1:
        flag = 'a'

    return redirect('management:list', flag)


@csrf_exempt
def adminsignup(request):
    """
    관리자 생성
    """
    if request.method == 'GET':
        return render(request, 'management/adminsignup.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        birth_date = request.POST.get('birthdate')
        address_code = request.POST.get('addressCode')
        address = request.POST.get('address')
        address_detail = request.POST.get('addressDetail')
        
        user = User.objects.create_user(
            username = username,
            password = password,
            first_name = name,
            email = email,
            is_superuser = 1,
            is_active = 1
        )
        
        AdministratorProfile.objects.create(
            auth_user=user
            , birth_date=birth_date
            , phone_number=phone_number
            , address_code=address_code
            , address=address
            , address_detail=address_detail
            , department='관리자'
        )

        result = True
        msg = "회원가입 요청이 완료되었습니다."

        return JsonResponse({'result': result, 'msg': msg})


@csrf_exempt
def admincheck_username(request):
    """
    ID 중복 확인
    """
    username = request.POST.get('username')
    is_taken = User.objects.filter(username=username).exists()
    print(is_taken)
    return JsonResponse({'is_taken': is_taken})


def admincheck_email(request):
    """
    이메일 중복 확인
    """
    email = request.GET.get('email')
    is_taken = User.objects.filter(email=email).exists()
    return JsonResponse({'is_taken': is_taken})


def admincheck_phone(request): 
    """
    핸드폰 번호 중복 확인
    """
    phone_number = request.GET.get('phone_number')
    is_taken = CounselorProfile.objects.filter(phone_number=phone_number).exists()
    return JsonResponse({'is_taken': is_taken})


def board_list(request):
    """
    공지사항 목록
    """
    search_select = request.GET.get("searchSelect", "")
    search_text = request.GET.get("searchText", "")
    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")

    search_query = Q()
    if search_select:
        valid_fields = {
            '1': 'title__icontains',
            '2': 'body__icontains',
            '3': 'auth_user__first_name__icontains',
        }

        if search_select == '0':
            for val in valid_fields.values():
                search_query |= Q(**{val: search_text})
        else:
            search_field = valid_fields[search_select]
            search_query = Q(**{search_field: search_text})

    date_query = Q()
    if not (start_date and end_date):
        one_month_ago = datetime.now() - timedelta(days=30)
        start_date = one_month_ago.strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    date_query = Q(auth_user__date_joined__range=[start_date+" 09:00:00", datetime.strptime(end_date+" 09:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)])

    data = Board.objects.filter(search_query & date_query)
    
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    data = paginator.get_page(page)
    
    for item in data:
        item.masked_name = mask_name(item.auth_user.first_name)
        soup = BeautifulSoup(item.body, 'html.parser')
        text = soup.get_text()
        item.body = text
        if len(text) > 10:
            item.body = text[:10]
            item.body += "..."
  
    context = {
        'data': data,
        'searchSelect': search_select,
        'searchText': search_text,
        'startDate': start_date,
        'endDate': end_date,
        'is_paginated': data.has_other_pages(),
    }

    return render(request, 'management/board_list.html', context)


def board_create(request):
    """
    공지사항 생성
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        flag = request.POST.get('flag', 0)

        # 파일 형식 검증
        if 'file' in request.FILES:
            file = request.FILES['file']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                return render(request, 'management/board_create.html', {'error': '파일 형식이 유효하지 않습니다. jpg, jpeg, png 형식만 업로드 가능합니다.'})

        board = Board.objects.create(
            auth_user=request.user,
            title=title,
            body=body,
            flag=flag
        )

        if 'file' in request.FILES:
            board.file = request.FILES['file']
            board.save()

        return redirect('management:board_list')  # 공지사항 목록 페이지로 리디렉션
    return render(request, 'management/board_create.html')


def board_detail(request, id):
    """
    공지사항 상세
    """
    board = get_object_or_404(Board, id=id)
    return render(request, 'management/board_detail.html', {'board': board})


def board_edit(request, id):
    """
    공지사항 수정
    """
    board = get_object_or_404(Board, id=id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        flag = request.POST.get('flag')
        file = request.FILES.get('file')
        
        if 'file' in request.FILES:
            file = request.FILES['file']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                return render(request, 'management/board_detail.html', {'error': '파일 형식이 유효하지 않습니다. jpg, jpeg, png 형식만 업로드 가능합니다.'})
            
        board.title = title
        board.body = body
        board.flag = flag
        
        if file:
            if board.file and default_storage.exists(board.file.name):
                default_storage.delete(board.file.name)
            if 'file' in request.FILES:
                board.file = request.FILES['file']
                board.save()
        
        board.save()
        return redirect('management:board_detail', id=board.id)
    return render(request, 'management/board_edit.html', {'board': board})


def board_delete(request, id):
    """
    공지사항 삭제
    """
    board = get_object_or_404(Board, id=id)
    if board.file:
        if board.file and default_storage.exists(board.file.name):
            default_storage.delete(board.file.name)
    board.delete()
    return redirect('management:board_list')


def mask_name(full_name):
    """
    마스킹 처리
    """
    if len(full_name) <= 2:
        return full_name[:-1] + '*'
    else:
        return full_name[0] + '*' * (len(full_name) - 2) + full_name[-1]
