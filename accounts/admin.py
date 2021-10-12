from shop.models import Accessory
from django.contrib import admin
from accounts.models import *

# Register your models here.
admin.site.register(Account)



@admin.register(Order)
class ShoesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'final_price', 'created')