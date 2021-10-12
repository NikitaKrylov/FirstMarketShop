from django import forms
from django.forms import fields, models
from accounts.models import Order


class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['email', 'first_name', 'last_name',
                  'phone_number', 'buying_type', 'addres',  'comment', 'order_date']

    def __init__(self, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        for field_name in self.Meta.fields:
            self.fields[field_name].widget.attrs['class'] = 'login-input'
            label = self.fields[field_name].label
            self.fields[field_name].widget.attrs['placeholder'] = label
            
