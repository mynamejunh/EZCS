from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from chat import Chatbot
from accounts.models import User
import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import EducationChatbotLog

def list(request):
    return render(request, 'education/index.html')

def details(request):
    return render(request, 'education/details.html')

# 퀴즈페이지
from .models import Quiz, QuizHistroy
from .forms import QuizForm

def quiz(request):
    results = {}
    quizzes = Quiz.objects.order_by('?')[:5]
    
    if request.method == 'POST':
        answers = request.POST.getlist('answers')
        quiz_ids = request.POST.getlist('quiz_ids')
        
        correct_answers = 0

        for idx, answer in enumerate(answers):
            quiz = Quiz.objects.get(id=quiz_ids[idx])
            is_correct = False
            if quiz.flag == 0 and quiz.answer == answer:
                is_correct = True
                correct_answers += 1
            elif quiz.flag == 1 and str(quiz.answer) == answer:
                is_correct = True
                correct_answers += 1
            
            results[quiz.id] = {
                'is_correct': is_correct,
                'user_answer': answer
            }

        is_passed = correct_answers >= 3
        categories = [Quiz.objects.get(id=quiz_id).category for quiz_id in quiz_ids]
        category = categories[0] if categories else 1

        history = QuizHistroy(
            category=category,
            is_passed=is_passed,
            user_id=request.user  # request.user를 직접 할당
        )
        history.save()

        return JsonResponse({'results': results})

    return render(request, 'education/quiz.html', {'quizzes': quizzes, 'results': results})


# 교육이력페이지
def edu_history(request):
    logs = EducationChatbotLog.objects.all()

    return render(request, 'education/edu_history.html', {'logs': logs})

# 교육이력 상세페이지
def edu_detail(request):
    user = User.objects.get(id=id)
    return render(request, 'education/details.html', {'user':user})


# 웹에서 동작하는 Chatbot(미완성)
messages ="너는 통신회사의 고객센터 상담사를 육성하는 챗봇이다.  \
      '시작'이라는 신호를 받으면 고객센터에 전화하는 고객 역할을 맡고, 나에게 민원을 제기한다. \
        나의 답변을 듣고, 그 답변에 대해 교육자의 입장에서 평가를 해준다. 그런 다음 다시 고객 역할로 돌아가서 다음 연관 질문을 던진다. \
            정확하고 친절하게 고객의 역할을 수행하고, 교육자의 평가에서는 구체적이고 도움이 되는 피드백을 제공하도록 한다. \
                질문이 명확하지 않으면 추가 정보를 요청할 수 있다. \
                    고객의 역할을 수행할 때는 다양한 민원 사항을 제기하며, 명확하고 구체적인 질문을 던진다. \
                        고객이 명세서를 확인할 수 있는 방법과 구체적인 확인 사항을 안내하고, 문제 해결을 위한 추가 조치를 제시한다."

chatbot = Chatbot(os.getenv("OPENAI_API_KEY"), 'database/chroma.sqlite3') # chatbot 객체 생성


def chat_view(request):
    global chatbot
    if request.method == 'POST':
        print('request.POST:', request.POST)
        if 'category' in request.POST:
            # 카테고리 선택 및 챗봇 초기화
            category = request.POST.get('category')
            print("####################################")
            print('category:', category)
            print("####################################")

            api_key = os.environ['OPENAI_API_KEY']
            db_path = '../db'

            # Chatbot 객체 초기화
            chatbot = Chatbot(api_key=api_key, 
                              db_path=db_path, 
                              category=category, 
                              THRESHOLD=2,
                               behavior_policy=messages)

            # 첫 질문 생성
            initial_question = chatbot.chat("고객의 역할에서 민원을 말해줘")

            return JsonResponse({'status': 'success', 'initial_question': initial_question})

        elif 'message' in request.POST:
            # 사용자 메시지 처리
            message = request.POST.get('message')
            print("####################################")
            print('Received message:', message)
            print("####################################")

            if chatbot is None:
                return JsonResponse({'response': 'Chatbot is not initialized. Please select a category first.'})

            # 사용자 메시지에 대한 응답 생성
            output = chatbot.chat(message)
            print("####################################")
            print('message:', message)
            print('output:', output)
            print("####################################")

            return JsonResponse({'response': output})

    return render(request, 'education/index.html')