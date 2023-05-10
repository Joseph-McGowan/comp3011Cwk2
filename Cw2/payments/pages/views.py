from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests 
import json


# Create your views here.

def index(request):
    return HttpResponse("<h1> test </h1>")

url = "http://127.0.0.1:8000/payments"
#response = requests.get(url)

@csrf_exempt
def paymentsForm(request):
    if request.method == "GET":
        fields = {'fields':{'cardNumber' : 'string', 'CVV': 'string', 'expiryDate' : 'date', 'name' : 'string', 'Email' : 'string'}}
        return JsonResponse(fields)


@csrf_exempt 
def paymentsPay(request):
    if request.method == "POST":
        for items in request.POST.items():
            print(items)
        cardNumber = request.POST['cardNumber']
        cvv = request.POST['CVV']
        expiryDate = request.POST['expiryDate']
        name = request.POST['name']
        email = request.POST['email']

        #error checking values

        success = 1
        if success:
            


        return JsonResponse({'request' : 'success'})


        return HttpResponse('tesst')


def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")