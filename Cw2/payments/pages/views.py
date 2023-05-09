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
        fields = {'fields':{'Card Number' : 'string', 'CVV': 'string', 'Expiry Date' : 'date', 'Name' : 'string', 'Email' : 'string'}}
        return JsonResponse(fields)

def paymentsPay(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        fields = json.loads(body)
        return JsonResponse(fields)




def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")