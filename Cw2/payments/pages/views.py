from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests 


# Create your views here.

def index(request):
    return HttpResponse("<h1> test </h1>")

url = "http://127.0.0.1:8000/payments"
#response = requests.get(url)

@csrf_exempt
def paymentsForm(request):
    if request.method == "GET":
        fields = {'fields':{'cardNumber' : 'string', 'CVV': 'string'}}
        return JsonResponse(fields)
    #if request.method == "POST":
     #    return HttpResponse("<h1> testpost </h1>")

