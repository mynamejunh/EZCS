from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import User
from django.http import HttpResponse, Http404
from django.urls import reverse

#관리자 메인페이지 DB에서 정보 받아오는 부분
def manager_dashboard(request):
    data = User.objects.all()
    return render(request, 'management/manager_dashboard.html',{'data':data})

#상세페이지
def manager_detail(request, id):
    user = get_object_or_404(User, id=id)
    # print(post.user)
    return render(request, 'management/management_detail.html', {'user':user})

#개인정보 수정
def manager_edit(request, id):
    user = get_object_or_404(User, id=id)
    data = {'user': user}
    if request.method == 'GET':
        return render(request, 'management/management_edit.html', data)
    else:
        print(request.method)
        return render(request, 'management/manager_dashboard.html')
    