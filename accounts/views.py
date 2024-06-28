# accounts 앱의 views.py 파일 예시

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('some-redirect-url')  # 회원가입 후 리다이렉트할 URL
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('some-redirect-url')  # 로그인 후 리다이렉트할 URL
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('some-redirect-url')  # 로그아웃 후 리다이렉트할 URL
    

def userSetting_View(request):
    return render(request, 'accounts/userSetting.html')
