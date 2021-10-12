from django.db.models.deletion import CASCADE
from functools import total_ordering
import re
from django.utils import timezone
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
from django.db.models.fields import DateField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, TextField, CharField, DateTimeField
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

# Create your models here.

class Cart(models.Model):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    user = OneToOneField(User, on_delete=models.CASCADE,
                         verbose_name='Пользователь корзины', related_name='related_user')
    cart_products = ManyToManyField(
        'CartProduct', related_name='related_cart')
    create_date = DateField(
        auto_now_add=True, verbose_name='Дата создания корзины')

    def get_amount_products(self):
        count = self.cart_products.all().aggregate(
            Sum('quantity')).get('quantity__sum')
        if count:
            return count
        return 0

    def get_final_price(self):
        total_price = 0
        for product in self.cart_products.all():
            total_price += product.calc_finale_price()

        return total_price

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'


class CartProduct(models.Model):
    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'

    cart = ForeignKey(Cart, on_delete=models.CASCADE,
                      related_name='related_product', verbose_name='Корзина')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Колличество товара')
    final_price = models.DecimalField(
        verbose_name='Общая цена товара/ов', max_digits=12, decimal_places=0, blank=True, default=0)

    def get_final_price(self):
        return self.final_price

    def calc_finale_price(self):
        self.final_price = self.content_object.price * self.quantity
        return self.final_price

    def get_price(self):
        return self.content_object.price

    def get_product_model(self):
        return self.content_object.__class__._meta.model_name

    def get_product_slug(self):
        return self.content_object.slug
    

    @property
    def get_name(self):
        if self.content_object:
            return self.content_object.name.title()
        return 'Такого товара больше не существует:('

    def __str__(self):
        return self.get_name
