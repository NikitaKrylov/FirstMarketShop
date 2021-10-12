from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import *

    
# Register your models here.
admin.site.register(Comment)
admin.site.register(GenericCategory)

@admin.register(Shoes)
class ShoesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
    def save_model(self, request, obj, form, change):
        obj.name = obj.name.lower()
        return super().save_model(request, obj, form, change)
    
    
@admin.register(Garment)
class GarmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
    def save_model(self, request, obj, form, change):
        obj.name = obj.name.lower()
        return super().save_model(request, obj, form, change)
    
    
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
    def save_model(self, request, obj, form, change):
        obj.name = obj.name.lower()
        return super().save_model(request, obj, form, change)
    

