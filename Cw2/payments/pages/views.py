from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests 
import json
import re


# Create your views here.

def index(request):
    return HttpResponse("<h1> test </h1>")

url = "http://127.0.0.1:8000/payments"
#response = requests.get(url)

@csrf_exempt
def paymentsForm(request):
    if request.method == "GET":
        fields = {'fields':{'cardNumber' : 'string', 'CVV': 'string', 'expiryDate' : 'string', 'name' : 'string', 'email' : 'string'}}
        return JsonResponse(fields)


@csrf_exempt 
def paymentsPay(request):
    if request.method == "POST":
        print(request.POST)
        for items in request.POST.items():
            print(items)
        cardNumber = request.POST['cardNumber']
        cvv = request.POST['CVV']
        expiryDate = request.POST['expiryDate']
        name = request.POST['name']
        email = request.POST['email']

        cardNumRegEx = re.compile(r"[0-9]{16}")
        cvvRegEx = re.compile(r"[0-9]{3}")
        expiryDateRegEx = re.compile(r"[0-9]{2}\/[0-9]{2}")
        nameRegex = re.compile(r"[A-Z)][a-zA-Z]*")
        emailRegEx = re.compile(r"[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+")

        if not(re.fullmatch(cardNumRegEx, cardNumber)):
            return HttpResponseBadRequest('Malformed Card Number, payment failed', status = 405)
        if not(re.fullmatch(cvvRegEx, cvv)):
            return HttpResponseBadRequest('Malformed CVV, payment failed', status = 405)
        if not(re.fullmatch(expiryDateRegEx, expiryDate)):
            return HttpResponseBadRequest('Malformed Expiry Date, payment failed', status = 405)
        if not(re.fullmatch(nameRegex, name)):
            return HttpResponseBadRequest('Invalid Name, payment failed', status = 405)
        if not(re.fullmatch(emailRegEx, email)):
            return HttpResponseBadRequest('Inavlid email, payment failed', status = 405)

        
        #error checking values

        success = 1
        if success:
            print('success')
        else:
            print ('failure')


        return JsonResponse({'request' : email})


        return HttpResponse('tesst')


def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")