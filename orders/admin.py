from django.contrib import admin
from .models import *


# admin.site.register(Order) находится в модуле account




@admin.register(Cart)
class ShoesAdmin(admin.ModelAdmin):
    pass


@admin.register(CartProduct)
class ShoesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity')