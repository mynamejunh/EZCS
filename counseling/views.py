from django.shortcuts import render
from django.http import JsonResponse
import os
from chat import Chatbot
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import *
import json
from django.http import HttpResponse

# def list(request):
#     data = CustomerInfo.objects.get(phone_number='01011112222')
#     print(data)
#     return render(request, "counseling/index.html",{'data':data})

def list(request):
    customer_info = CustomerInfo.objects.all()
    counsel_logs = CounselLog.objects.all()

    # counsel_logs의 memo 필드를 JSON 형식으로 파싱
    for log in counsel_logs:
        try:
            memo_json = json.loads(log.memo)  # memo 필드를 JSON 형식으로 파싱
            log.memo = memo_json.get('text', '')  # memo 필드의 text 값을 가져옴
        except (TypeError, json.JSONDecodeError):
            log.memo = log.memo  # JSON 형식이 아닐 경우 기존 문자열 그대로 사용

    context = {
        'customer_info': customer_info,
        'counsel_logs': counsel_logs
    }
    return render(request, "counseling/index.html", context)

# 상담이력 뷰
def history(request):
    query = request.POST.get('searchText', '')

    if query:
        logs = CounselLog.objects.filter(body__icontains=query)
    else:
        logs = CounselLog.objects.all()

    return render(request, 'counseling/history.html', {'logs': logs})



@csrf_exempt
def save_customer_info(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer-name")
        birth_date = request.POST.get("birthdate")
        phone_number = request.POST.get("phone")
        address = request.POST.get("address")
        joined_date = request.POST.get("join-date")

        print(customer_name)
        print(birth_date)
        print(phone_number)
        print(address)
        print(joined_date)

        try:
            customer_info = CustomerInfo(
                phone_number=phone_number,
                name=customer_name,
                birth_date=birth_date,
                joined_date=joined_date,
                address=address,
            )
            customer_info.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def save_counseling_log(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            username = data.get("username")
            phone_number_str = data.get("phone_number")

            try:
                phone_number = CustomerInfo.objects.get(phone_number=phone_number_str)
            except CustomerInfo.DoesNotExist:
                return JsonResponse({"success": False, "error": "CustomerInfo not found"})

            chat_data = json.dumps(data.get("chat_data", {}), ensure_ascii=False)
            memo_data = json.dumps(data.get("memo_data", {}), ensure_ascii=False)
            
            print(f"Username: {username}")
            print(f"Phone Number: {phone_number}")
            print(f"Chat Data: {chat_data}")
            print(f"Memo Data: {memo_data}")

            counselLog = CounselLog(
                username=username,
                phone_number=phone_number,
                body=chat_data,
                memo=memo_data,
            )
            counselLog.save()

            return JsonResponse({"success": True})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def save_consultation(request):
    if request.method == 'POST':
        try:
            log_id = request.POST.get('log_id')
            inquiry_text = request.POST.get('inquiry_text')

            if log_id and inquiry_text:
                counsel_log = CounselLog.objects.get(id=log_id)
                counsel_log.memo = {"text": inquiry_text}  
                counsel_log.save()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Missing log_id or inquiry_text'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
