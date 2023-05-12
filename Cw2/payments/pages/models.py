from django.db import models

# Create your models here.
class creditCard(models.Model):
    cardId = models.CharField(max_length=20, primary_key= True)
    cardNumber = models.CharField(max_length=20)
    cardType = models.CharField(max_length=20)
    cardCVV = models.CharField(max_length=20)
    cardExpiryDate = models.CharField(max_length=20)
    cardSalt = models.CharField(max_length=20)
    cardUserName = models.CharField(max_length=20)
    cardBalance = models.DecimalField(decimal_places= 2, max_digits=10)
    cardCurrencyId = models.ForeignKey('Currencies', on_delete= models.CASCADE)
    cardBillingId = models.ForeignKey('billingDetails', on_delete= models.CASCADE)

class billingDetails(models.Model):
    userId = models.AutoField(primary_key= True)
    userFirstName = models.CharField(max_length=20)
    userLastName = models.CharField(max_length=20)
    userAddrLineOne = models.CharField(max_length=20)
    userAddrLineTwo = models.CharField(max_length=20)
    userCountry = models.CharField(max_length=20)
    userPhoneNumber = models.CharField(max_length=20)
    userEmail = models.EmailField()

class transactions(models.Model):
    tUserId = models.ForeignKey("billingDetails", on_delete= models.CASCADE)
    tDate = models.DateField()
    tAmount = models.FloatField()
    tCurrencyID = models.ForeignKey("Currencies", on_delete= models.CASCADE)
    tTransactionFee = models.FloatField()
    tConfirmed = models.BooleanField()
    tRecipAccountId = models.IntegerField()


class Currencies(models.Model):
    cName = models.CharField(max_length=20)
    cSymbol = models.CharField(max_length=20)
    cRate = models.DecimalField(decimal_places= 2, max_digits= 8)
