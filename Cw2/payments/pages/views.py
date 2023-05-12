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
            formData = payload.get("fields")
            transactionData = payload.get("transaction")

            requestCardNumber = formData.get("cardNumber")
            cvv = formData.get("cvv")
            expiryDate = formData.get("expiryDate")
            name = formData.get("name")
            email = formData.get("email")

            rAmount = transactionData.get("amount")
            rCurrency = transactionData.get("currency")
            rRecipAccount = transactionData.get("recipientAccount")
            rBookingId = transactionData.get("bookingID")

        except json.JSONDecodeError:
            return HttpResponseBadRequest("invalid json data")
        #Parse request data


        #Check input data is formed correctly

        cardNumRegEx = re.compile(r"[0-9]{16}")
        cvvRegEx = re.compile(r"[0-9]{3}")
        expiryDateRegEx = re.compile(r"[0-9]{2}\/[0-9]{2}")
        nameRegex = re.compile(r"[A-Z)][a-zA-Z]*")
        emailRegEx = re.compile(r"[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+")

        if not(re.fullmatch(cardNumRegEx, requestCardNumber)):
            return JsonResponse('Malformed Card Number, payment failed', status = 405)
        if not(re.fullmatch(cvvRegEx, cvv)):
            return  JsonResponse('Malformed CVV, payment failed', status = 405)
        if not(re.fullmatch(expiryDateRegEx, expiryDate)):
            return  JsonResponse('Malformed Expiry Date, payment failed', status = 405)
        if not(re.fullmatch(nameRegex, name)):
            return  JsonResponse('Invalid Name, payment failed', status = 405)
        if not(re.fullmatch(emailRegEx, email)):
            return  JsonResponse('Inavlid email, payment failed', status = 405)

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
        if transactionCard.cardCurrencyId != rCurrency:
            AmountPreConversion = rAmount
            response = requests.get(url+'/exchange/'+rCurrency+'/'+str(AmountPreConversion))
            data = response.json()
            rAmount = data.get("convertedAmount") 

        #check user has enough in acccount for transaction (inlcudind transaction fee)

        #update users card balance
        balanceToUpdate = Decimal(transactionCard.cardBalance) 
        balanceToUpdate-= (Decimal(rAmount) + Decimal(50.00))
        transactionCard.cardBalance = balanceToUpdate
        transactionCard.save()

        #relevant data for bank api
        data = {'amount' : rAmount, 'companyName' : rRecipAccount, 'bookingID' : rBookingId}
        #json.dumps()

        #send post request to bank api to make paument to airline
        response = requests.post(url+'/pay', json= data)

        #tCurrency 

        if response.status_code == 200:
            #successful
            #send email
            #Create a transaction
            transaction = transactions()
            transaction.tUserId = tBillingDetails
            transaction.tDate = date.today()
            transaction.tAmount = rAmount
            transaction.tCurrencyID = Currencies.objects.get(cSymbol = rCurrency)
            transaction.tTransactionFee = 50.00
            transaction.tConfirmed = True
            transaction.tRecipAccountId = rRecipAccount
            transaction.save()

            data = {
                'status' : "success",
                'TransactionID' : str(transaction.id)
            }
            return JsonResponse(data)

        else:
            data = {
                'status' : 'failed'            
            }
            return JsonResponse(data)

@csrf_exempt
def paymentsRefund(request):
    if request.method == 'POST':

        #parse bank details

        try:    
            payload = json.loads(request.body)
            formData = payload.get("fields")
            transactionData = payload.get("transaction")

            requestCardNumber = formData.get("cardNumber")
            cvv = formData.get("cvv")
            expiryDate = formData.get("expiryDate")
            name = formData.get("name")
            email = formData.get("email")

            rTransaction = transactionData.get("TransactionID")
            rReservation = transactionData.get("BookingID")
            #rCurrency = transactionData.get("currency")

        except json.JSONDecodeError:
            return HttpResponseBadRequest("invalid json data")

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
        balanceToUpdate +=  float(rTransactionDB.tAmount)
        transactionCard.cardBalance = balanceToUpdate
        
        transactionCard.save()

        currencyID = rTransactionDB.tCurrencyID


        data = {'bookingID' : rReservation }
        

        #send refund post request to bank
        response = requests.post(url+'/refund', json = data)

        if response.status_code == 200:
            data = {'status' : 'success'}
            return JsonResponse(data)

        data = {'status' : 'failed'}
        return JsonResponse(data)

def paymentsBase(request):
    if request.method == 'GET':
        return HttpResponse("<h1> testpost </h1>")