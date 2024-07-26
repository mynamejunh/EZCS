import random
import json

from chat import Chatbot
from chat_trans import Chatbot_trans
from prompt import Prompt

from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from abuse_filter import AbuseFilter
from .models import *


abuse_filter = AbuseFilter()
prompt = Prompt()
trans_chat_bot = None
recommend_chat_bot = None


def counsel(request):
    """
        AI 상담
    """
    if request.method == "POST":
        global trans_chat_bot, recommend_chat_bot
        id = request.POST.get("customerId")
        customer = CustomerProfile.objects.get(id=id)
        log = Log.objects.create(auth_user_id=request.user.id, customer_id=id)
        context = {"logId": log.id, "customer": customer}
        trans_chat_bot = Chatbot_trans(
            model_id="ft:gpt-3.5-turbo-0125:personal::9god26fK",
            behavior_policy=prompt.get_behavior_policy_for_trans(),
        )

        recommend_chat_bot = Chatbot(behavior_policy=prompt.get_behavior_policy_for_recommend(), k=1)

        return render(request, "counseling/index.html", context)

    customer = CustomerProfile.objects.order_by("?").first()
    context = {"customer": customer}
    return render(request, "counseling/index.html", context)


def update_log(request):
    """
    고객 정보 수정
    """
    if request.method == "POST":
        customer_id = request.POST.get("customer-id")
        customer_name = request.POST.get("customer-name")
        birth_date = request.POST.get("birthdate")
        phone_number = request.POST.get("phone")
        address = request.POST.get("address")
        joined_date = request.POST.get("join-date")
        log_id = request.POST.get("logId")
        inquiries = request.POST.get("inquiries")
        action = request.POST.get("action")

        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            customer.phone_number = phone_number
            customer.name = customer_name
            customer.birth_date = birth_date
            customer.joined_date = joined_date
            customer.address = address
            customer.save()
            log = Log.objects.get(id=log_id)
            log.inquiries = inquiries
            log.action = action
            log.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)


def delete_counseling_init_data(request):
    """
        상담 초기만 존재하는 데이터 삭제
    """
    if request.method == "POST":
        id = request.POST.get('id')
        LogItem.objects.filter(log=id).delete()
        Log.objects.filter(id=id).delete()
        return JsonResponse({"response": "True"})
    return JsonResponse({"response": "False"})


def ai_model(request):
    """
        대화 내용 INSERT
    """
    if request.method == "POST":
        classify = request.POST.get("classify")
        message = request.POST.get("message")
        log_id = request.POST.get("logId")
        try:
            classify = 0 if classify == "customer" else 1
            columns = {"classify": classify, "message": message, "log_id": log_id}
            result = {"success": True}
            if not classify:
                global trans_chat_bot, recommend_chat_bot
                trans_output = trans_chat_bot.ask(message)
                trans_output = abuse_filter.abuse_clean(trans_output)
                recommend_output = recommend_chat_bot.chat(message)
                columns["recommend"] = recommend_output
                columns["translate"] = trans_output
                result["recommend_output"] = recommend_output
                result["trans_output"] = trans_output

            LogItem.objects.create(**columns)

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)


def history(request):
    """
    상담 이력 페이지
    """
    search_text = request.GET.get("searchText", "")
    search_select = request.GET.get("searchSelect", "")

    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")

    superuser_query = Q()
    if not request.user.is_superuser:
        superuser_query = Q(auth_user=request.user.id)

    search_query = Q()
    if search_select:
        valid_fields = {
            '1': 'customer__name__icontains',
            '2': 'inquiries__icontains',
            '3': 'action__icontains',
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

    date_query = Q(create_time__range=[start_date+" 09:00:00", datetime.strptime(end_date+" 09:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)])

    data = Log.objects.filter(superuser_query & search_query & date_query).order_by("-create_time", "customer_id", "auth_user_id")

    paginator = Paginator(data, 10)
    page = request.GET.get("page")
    data = paginator.get_page(page)
    
    for log in data:
        log.masked_name = mask_name(log.customer.name)

    context = {
        "data": data,
        "searchSelect": search_select,
        "searchText": search_text,
        "startDate": start_date,
        "endDate": end_date,
        "is_paginated": data.has_other_pages(),
    }

    return render(request, "counseling/history.html", context)


def detail(request, id):
    """
        AI 상담 이력 상세 페이지
    """
    head = Log.objects.get(id=id)
    data = LogItem.objects.filter(log_id=id)
    context = {"head": head, "data": data}
    return render(request, "counseling/detail.html", context)


def mask_name(full_name):
    """
        이름 마스킹
    """
    if len(full_name) <= 2:
        return full_name[:-1] + '*'
    else:
        return full_name[0] + '*' * (len(full_name) - 2) + full_name[-1]