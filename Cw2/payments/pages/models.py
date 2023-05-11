from django.db import models

# Create your models here.
class creditCard(models.Model):
    cardId = models.CharField(max_length=20, primary_key= True)
    cardNumber = models.CharField()
    cardType = models.CharField()
    cardCVV = models.CharField()
    cardExpiryDate = models.CharField()
    cardSalt = models.CharField()
    cardUserName = models.CharField()
    cardBalance = models.DecimalField(decimal_places= 2)
    cardCurrencyId = models.ForeignKey('Currencies', on_delete= models.CASCADE)
    cardBillingId = models.ForeignKey('billingDetails', on_delete= models.CASCADE)

class billingDetails(models.Model):
    userId = models.AutoField(primary_key= True)
    userFirstName = models.CharField()
    userLastName = models.CharField()
    userAddrLineOne = models.CharField()
    userAddrLineTwo = models.CharField()
    userCountry = models.CharField()
    userPhoneNumber = models.CharField()
    userEmail = models.EmailField()

class transactions(models.Model):
    tUserId = models.ForeignKey()
    tDate = models.DateField()
    tAmount = models.FloatField()
    tCurrencyID = models.ForeignKey("creditCard", on_delete= models.CASCADE)
    tTransactionFee = models.FloatField()
    tConfirmed = models.BooleanField()
    tRecipAccountId = models.IntegerField()


class Currencies(models.Model):
    cName = models.CharField()
    cSymbol = models.CharField()
    cRate = models.DecimalField(decimal_places= 2)
