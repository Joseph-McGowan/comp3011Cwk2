from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests 
import json
import re
from pages.models import creditCard, billingDetails, transactions, Currencies
from datetime import date

# Create your views here.

def index(request):
    return HttpResponse("<h1> test </h1>")

url = "https://sc19jt.pythonanywhere.com/bank"
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
       
        #Parse request data

        requestCardNumber = request.POST['cardNumber']
        cvv = request.POST['CVV']
        expiryDate = request.POST['expiryDate']
        name = request.POST['name']
        email = request.POST['email']

        rAmmount = request.POST['amount']
        rCurrency = request.POST['currency']
        rRecipAccount = request.POST['recipientAccount']
        rReservationId = request.POST['reservationId']

        #Check input data is formed correctly

        cardNumRegEx = re.compile(r"[0-9]{16}")
        cvvRegEx = re.compile(r"[0-9]{3}")
        expiryDateRegEx = re.compile(r"[0-9]{2}\/[0-9]{2}")
        nameRegex = re.compile(r"[A-Z)][a-zA-Z]*")
        emailRegEx = re.compile(r"[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+")

        if not(re.fullmatch(cardNumRegEx, requestCardNumber)):
            return HttpResponseBadRequest('Malformed Card Number, payment failed', status = 405)
        if not(re.fullmatch(cvvRegEx, cvv)):
            return HttpResponseBadRequest('Malformed CVV, payment failed', status = 405)
        if not(re.fullmatch(expiryDateRegEx, expiryDate)):
            return HttpResponseBadRequest('Malformed Expiry Date, payment failed', status = 405)
        if not(re.fullmatch(nameRegex, name)):
            return HttpResponseBadRequest('Invalid Name, payment failed', status = 405)
        if not(re.fullmatch(emailRegEx, email)):
            return HttpResponseBadRequest('Inavlid email, payment failed', status = 405)

        #query database for card matching form data
        
        transactionCard = creditCard.objects.get(cardNumber = requestCardNumber)
        cardExists = creditCard.objects.get(cardNumber = requestCardNumber).exists()

        if not(cardExists):
            return JsonResponse('status : failed', "message : card Doesn't exist")

        #check other card details
        if cvv != transactionCard.cardCVV:
            return JsonResponse('status : failed')
        if expiryDate != transactionCard.cardExpiryDate:
            return JsonResponse('status : failed')
        if name != transactionCard.cardUserName:
            return JsonResponse('status : failed')

        #access users billing details through foreign key relation
        tBillingDetails = transactionCard.cardBillingId

        #check whether currency needs to be converted before making payment reqeust
        if transactionCard.cardCurrencyId != rCurrency:
            ammountPreConversion = rAmmount
            rAmmount = requests.get(url+'/exchange/'+rCurrency+'/'+ammountPreConversion)

        #update users card balance
        transactionCard.cardBalance -= rAmmount
        transactionCard.save()

        #relevant data for bank api
        data = {'transaction' : {'amount' : rAmmount, 'currency' : rCurrency, 'recipientAccount' : rRecipAccount, 'reservationId' : rReservationId} }

        #send post request to bank api to make paument to airline
        response = requests.post(url+'/pay', data= data)

        if response.status_code == 200:
            #successful
            #send email
            #Create a transaction
            transaction = transactions()
            transaction.tUserId = tBillingDetails.userId
            transaction.tDate = date.today()
            transaction.tAmount = rAmmount
            transaction.tCurrencyID = rCurrency
            transaction.tTransactionFee = "50"
            transaction.tConfirmed = True
            transaction.tRecipAccountId = rRecipAccount
            transaction.save()

            return JsonResponse('status : success', transaction.id )

        else:
            return JsonResponse('status : failed')


def paymentsRefund(request):
    if request.method == 'POST':
        return JsonResponse('status : success')

def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")