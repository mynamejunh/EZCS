import json
from datetime import datetime, timedelta

from .models import *
from .forms import QuizForm

from django.core.paginator import Paginator
from django.db.models import Q, Avg, F, Case, When, Value
from django.db.models.functions import Round
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from chat import Chatbot
from prompt import Prompt


chatbot = None
evaluation_chatbot = None
prompt = Prompt()
prompt.set_initial_behavior_policy_for_education()


@csrf_exempt
def chat_view(request):
    '''
    AI 트레이너 페이지
    '''
    if request.method == "POST":
        global chatbot
        category = request.POST.get("category", None)
        message = request.POST.get("message", None)
        if message:
            log_header_id = request.POST.get("log_header", None)
            if chatbot is None:
                return JsonResponse({"response": "Chatbot is not initialized. Please select a category first."})
            
            output = chatbot.chat(message)

            evaluation_chatbot = Chatbot(
                model_id="gpt-4o",
                category=category,
                THRESHOLD=2,
                behavior_policy=prompt.get_messages_for_evaluation(output, message),
            )

            evaluation_output = evaluation_chatbot.chat(message)

            accuracy_score = 0
            if "정확성: " in evaluation_output:
                start_idx = evaluation_output.find("정확성: ") + len("정확성: ")
                end_idx = evaluation_output.find(" -", start_idx)
                accuracy_score = int(evaluation_output[start_idx:end_idx])

            kind_score = 0
            if "친절함: " in evaluation_output:
                start_idx = evaluation_output.find("친절함: ") + len("친절함: ")
                end_idx = evaluation_output.find(" -", start_idx)
                kind_score = int(evaluation_output[start_idx:end_idx])

            solving_score = 0
            if "문제 해결 능력: " in evaluation_output:
                start_idx = evaluation_output.find("문제 해결 능력: ") + len("문제 해결 능력: ")
                end_idx = evaluation_output.find(" -", start_idx)
                solving_score = int(evaluation_output[start_idx:end_idx])

            add_score = 0
            if "추가 정보 제공: " in evaluation_output:
                start_idx = evaluation_output.find("추가 정보 제공: ") + len("추가 정보 제공: ")
                end_idx = evaluation_output.find(" -", start_idx)
                add_score = int(evaluation_output[start_idx:end_idx])

            time_score = 0
            if "응답 시간: " in evaluation_output:
                start_idx = evaluation_output.find("응답 시간: ") + len("응답 시간: ")
                end_idx = evaluation_output.find(" -", start_idx)
                time_score = int(evaluation_output[start_idx:end_idx])

            LogItem.objects.create(
                chatbot=output
                , user=message
                , evaluate=evaluation_output
                , accuracy_score=accuracy_score
                , kind_score=kind_score
                , solving_score=solving_score
                , add_score=add_score
                , time_score=time_score
                , log_id=log_header_id
            )

            return JsonResponse({
                "response": output
                , "userInput": message
                , "output": evaluation_output
            })
        elif category:
            chatbot = Chatbot(
                model_id="gpt-4o",
                category=category,
                THRESHOLD=2,
                behavior_policy=prompt.get_behavior_policy(),
            )

            initial_question = chatbot.chat("고객의 역할에서 민원을 말해줘")
            if category == '모바일 > 부가서비스':
                category = 0
            elif category == '모바일 > 서비스정책':
                category = 1
            else:
                category = 2

            log_header = Log.objects.create(
                category=category
                , auth_user_id=request.user.id
            )

            LogItem.objects.create(
                chatbot=initial_question
                , log_id=log_header.id
            )
            
            return JsonResponse({
                "status": "success"
                , "initial_question": initial_question
                , "log_header": log_header.id
            })
        
    return render(request, "education/index.html")
    

def delete_training_init_data(request):
    """
        AI 트레이너 바로 종료 시 데이터 삭제
    """
    if request.method == "POST":
        id = request.POST.get('id')
        LogItem.objects.filter(log=id).delete()
        Log.objects.filter(id=id).delete()
        return JsonResponse({"response": "True"})
    return JsonResponse({"response": "False"})


def edu_history(request):
    '''
    AI 트레이너 이력 페이지
    '''

    search_text = request.GET.get("searchText", "")
    search_select = request.GET.get("searchSelect", "")
    
    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")

    superuser_query = Q()
    if not request.user.is_superuser:
        superuser_query = Q(auth_user=request.user.id)
    
    search_query = Q()
    if search_select:
        search_query = Q(category=search_select)

    date_query = Q()
    if not (start_date and end_date):
        one_month_ago = datetime.now() - timedelta(days=30)
        date_query = Q(create_time__range=[one_month_ago, datetime.now()])
        start_date = one_month_ago.strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    date_query = Q(create_time__range=[start_date+" 09:00:00", datetime.strptime(end_date+" 09:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)])

    data = Log.objects.filter(superuser_query & search_query & date_query).order_by('-create_time', 'category')
    
    data = data.annotate(
        avg_accuracy_score=Round(Avg('education_log_items__accuracy_score'), 2),
        avg_kind_score=Round(Avg('education_log_items__kind_score'), 2),
        avg_solving_score=Round(Avg('education_log_items__solving_score'), 2),
        avg_add_score=Round(Avg('education_log_items__add_score'), 2),
        avg_time_score=Round(Avg('education_log_items__time_score'), 2),
        overall_avg_score=Round(Avg(
            F('education_log_items__accuracy_score') +
            F('education_log_items__kind_score') +
            F('education_log_items__solving_score') +
            F('education_log_items__add_score') +
            F('education_log_items__time_score')
        ) / 5, 2),
        category_display=Case(
            When(category=0, then=Value('부가 서비스')),
            When(category=1, then=Value('서비스 정책')),
            When(category=2, then=Value('요금 관련')),
            default=Value('-')
        )
    ).values(
        'id',
        'category',
        'category_display',
        'create_time',
        'auth_user__username',
        'avg_accuracy_score',
        'avg_kind_score',
        'avg_solving_score',
        'avg_add_score',
        'avg_time_score',
        'overall_avg_score'
    )
    
    filtered_data = []
    for item in data:
        if None not in [
            item['avg_accuracy_score'],
            item['avg_kind_score'],
            item['avg_solving_score'],
            item['avg_add_score'],
            item['avg_time_score'],
            item['overall_avg_score']
        ]:
            filtered_data.append(item)

    paginator = Paginator(filtered_data, 10)
    page = request.GET.get('page')
    data = paginator.get_page(page)

    context = {
        'data': data,
        'searchSelect': search_select,
        'searchText': search_text,
        'startDate': start_date,
        'endDate': end_date,
        'is_paginated': data.has_other_pages(),
    }

    return render(request, "education/edu_history.html", context)


def edu_details(request, id):
    '''
    AI 트레이너 이력 상세 페이지
    '''
    head = Log.objects.get(id=id)
    data = LogItem.objects.filter(log_id=id)
    context = {
        'head': head
        , 'data': data
    }
    return render(request, 'education/edu_details.html', context)


@csrf_exempt
def quiz(request):
    '''
    퀴즈페이지
    '''
    quizzes = Quiz.objects.order_by('?')[:5]  # 퀴즈 5개를 랜덤으로 가져오기

    if request.method == "POST":  # 폼 제출이 POST 요청으로 이루어질 때
        form = QuizForm(request.POST)
        if form.is_valid():
            answers = json.loads(form.cleaned_data["answers"])
            quiz_ids = [int(id) for id in json.loads(form.cleaned_data["quiz_ids"])]

            results = {}
            correct_answers = 0  # 정답 개수를 세기 위한 변수 초기화

            for idx, answer in enumerate(answers):  # 제출된 답변들을 순회하면서
                try:
                    quiz = Quiz.objects.get(id=quiz_ids[idx])  # 현재 퀴즈 ID로 퀴즈 객체 가져오기
                except Quiz.DoesNotExist:
                    continue

                is_correct = False  # 초기 값은 오답으로 설정
                if (quiz.flag == 0 and quiz.answer.strip().lower() == answer.strip().lower()):  # 단답형 퀴즈의 경우
                    is_correct = True  # 정답일 경우
                    correct_answers += 1  # 정답 개수 증가
                elif (quiz.flag == 1 and str(quiz.answer) == answer):  # 객관식 퀴즈의 경우
                    is_correct = True  # 정답일 경우
                    correct_answers += 1  # 정답 개수 증가
                
                results[quiz.id] = {  # 결과 딕셔너리에 현재 퀴즈의 정답 여부와 사용자의 답변 저장
                    'is_correct': is_correct,
                    'user_answer': answer,
                    'commentary': quiz.commentary,  # 해설 추가
                    'correct_answer': quiz.answer
                }

            is_passed = correct_answers >= 3  # 3개 이상의 정답이면 통과로 설정
            categories = [Quiz.objects.get(id=quiz_id).category for quiz_id in quiz_ids]  # 퀴즈 ID로 각 퀴즈의 카테고리 가져오기
            category = (categories[0] if categories else 1)  # 카테고리가 존재하면 첫 번째 카테고리, 아니면 기본값 1

            # QuizHistory 객체 생성 및 저장
            history = QuizHistory(
                category=category,
                is_passed=is_passed,
                auth_user_id=request.user.id,  # 현재 로그인된 사용자 객체
            )
            history.save()

            # QuizHistoryItem 객체 생성 및 저장
            for idx, answer in enumerate(answers):
                quiz = Quiz.objects.get(id=quiz_ids[idx])
                item = QuizHistoryItem.objects.create(
                    quiz_history=history,
                    quiz=quiz,
                    answer=answer,
                )

            return JsonResponse({"results": results})  # 결과를 JSON 형태로 반환

    else:
        form = QuizForm()

    return render(request, 'education/quiz.html', {'quizzes': quizzes, 'form': form})


def quiz_history(request):
    '''
    퀴즈 이력
    '''
    # 검색 필터링 처리
    search_select = request.GET.get("searchSelect", "")
    result = request.GET.get("result", "")
    
    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")

    result = request.GET.get("result", "")

    superuser_query = Q()
    if not request.user.is_superuser:
        superuser_query = Q(auth_user_id=request.user.id)

    search_query = Q()
    if search_select:
        search_query = Q(category=search_select)

    pass_query = Q()
    if result:
        pass_query = Q(is_passed=result)

    date_query = Q()
    if not (start_date and end_date):
        one_month_ago = datetime.now() - timedelta(days=30)
        date_query = Q(create_time__range=[one_month_ago, datetime.now()])
        start_date = one_month_ago.strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    date_query = Q(create_time__range=[start_date+" 09:00:00", datetime.strptime(end_date+" 09:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)])

    data = QuizHistory.objects.filter(superuser_query & search_query & pass_query & date_query).select_related('auth_user').order_by('-create_time', 'category')

    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    data = paginator.get_page(page)

    context = {
        'data': data,
        'searchSelect': search_select,
        'startDate': start_date,
        'endDate': end_date,
        'result': result,
        'is_paginated': data.has_other_pages(),
    }

    return render(request, "education/quiz_history.html", context)


def quiz_details(request, log_id):
    '''
    퀴즈 이력 상세
    '''
    head = get_object_or_404(QuizHistory, id=log_id)

    data = QuizHistoryItem.objects.filter(quiz_history=log_id).select_related('quiz')
    context = {
        'head': head
        , 'data': data
    }
    return render(request, 'education/quiz_details.html', context)
