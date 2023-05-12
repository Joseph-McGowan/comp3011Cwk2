from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests 
import json
import re
from pages.models import creditCard, billingDetails, transactions, Currencies
from datetime import date
from decimal import Decimal

# Create your views here.

def index(request):
    return HttpResponse("<h1> test </h1>")

url = "https://sc19jt.pythonanywhere.com/bank"
#response = requests.get(url)

@csrf_exempt
def paymentsForm(request):
    if request.method == "GET":
        fields = {'fields':{'cardNumber' : '16 digit card number', 'cvv': '3 digit CVV', 'expiryDate' : 'MM/YY', 'name' : 'first letter must be capitalised, e.g: Bob', 'email' : 'e.g : johndoe@gmail.com'}}
        return JsonResponse(fields)


@csrf_exempt 
def paymentsPay(request):
    if request.method == "POST":
        #print(request.POST)
        #for items in request.POST.items():
        #    print(items)
       
        try:    
            payload = json.loads(request.body)
            formData = payload.get("form")
            transactionData = payload.get("transaction")

            requestCardNumber = formData.get("cardNumber")
            cvv = formData.get("cvv")
            expiryDate = formData.get("expiryDate")
            name = formData.get("name")
            email = formData.get("email")

            rAmount = transactionData.get("amount")
            rCurrency = transactionData.get("currency")
            rRecipAccount = transactionData.get("recipientAccount")
            rReservationId = transactionData.get("reservationId")

        except json.JSONDecodeError:
            return HttpResponseBadRequest("invalid json data")
        #Parse request data

       

        #requestCardNumber = request.POST['cardNumber']
        #cvv = request.POST['cvv']
        #expiryDate = request.POST['expiryDate']
        #name = request.POST['name']
        #email = request.POST['email']

        #rAmount = request.POST.get('amount')
        #rCurrency = request.POST['currency']
        #rRecipAccount = request.POST['recipientAccount']
        #rReservationId = request.POST['reservationId']

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
        cardExists = creditCard.objects.filter(cardNumber = requestCardNumber).exists()

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
        #if transactionCard.cardCurrencyId != rCurrency:
         #   AmountPreConversion = rAmount
          #  rAmount = requests.get(url+'/exchange/'+rCurrency+'/'+str(AmountPreConversion))

        #update users card balance
        balanceToUpdate = Decimal(transactionCard.cardBalance) 
        balanceToUpdate-= Decimal(rAmount)
        transactionCard.cardBalance = balanceToUpdate
        transactionCard.save()

        #relevant data for bank api
        data = {'transaction' : {'amount' : rAmount, 'currency' : rCurrency, 'recipientAccount' : rRecipAccount, 'reservationId' : rReservationId} }

        #send post request to bank api to make paument to airline
        response = requests.post(url+'/pay', data= data)

        if response.status_code == 200:
            #successful
            #send email
            #Create a transaction
            transaction = transactions()
            transaction.tUserId = tBillingDetails.userId
            transaction.tDate = date.today()
            transaction.tAmount = rAmount
            transaction.tCurrencyID = rCurrency
            transaction.tTransactionFee = 50
            transaction.tConfirmed = True
            transaction.tRecipAccountId = rRecipAccount
            transaction.save()

            return JsonResponse('status : success', transaction.id )

        else:
            return JsonResponse('status : failed')


def paymentsRefund(request):
    if request.method == 'POST':

        #parse bank details
        requestCardNumber = request.POST['cardNumber']
        cvv = request.POST['cvv']
        expiryDate = request.POST['expiryDate']
        name = request.POST['name']
        email = request.POST['email']

        rTransaction = request.POST['transactionId']
        rReservation = request.POST['reservationId']

        #query database for card in request
        transactionCard = creditCard.objects.get(cardNumber = requestCardNumber)
        cardExists = creditCard.objects.filter(cardNumber = requestCardNumber).exists()

        if not(cardExists):
            return JsonResponse('status : failed', "message : card Doesn't exist")
        
        #check other card details match
        if cvv != transactionCard.cardCVV:
            return JsonResponse('status : failed')
        if expiryDate != transactionCard.cardExpiryDate:
            return JsonResponse('status : failed')
        if name != transactionCard.cardUserName:
            return JsonResponse('status : failed')

        rBillingDetails = transactionCard.cardBillingId

        rTransactionDB = transactions.objects.get(id = rReservation)

        transactionUser = rTransactionDB.tUserId

        #Make sure person making request made original transaction
        if transactionUser.userFirstName != rBillingDetails.userFirstName:
            return JsonResponse("error : transaction made under different user")
        
        #Refund money to recip account
        balanceToUpdate = Decimal(transactionCard.cardBalance) 
        balanceToUpdate +=  float(rTransaction.tAmount)
        transactionCard.cardBalance = balanceToUpdate
        
        transactionCard.save()

        currencyID = rTransactionDB.tCurrencyID


        data = {'transactionId' : rTransaction, 'reservationId' : rReservation }
        

        #send refund post request to bank
        response = requests.post(url+'/refund', data = data)

        if response.status_code == 200:
            return JsonResponse('Status : success')


        return JsonResponse('status : error')

def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")