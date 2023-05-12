from django.contrib import admin

from .models import creditCard, billingDetails, transactions, Currencies
# Register your models here.
admin.site.register(creditCard)
admin.site.register(transactions)
admin.site.register(Currencies)
admin.site.register(billingDetails)