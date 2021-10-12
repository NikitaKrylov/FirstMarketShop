from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField, CharField, EmailField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from orders.models import Cart
from orders.models import CartProduct
from django.utils import timezone


# Create your models here.

class Account(models.Model):
    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verificated = models.BooleanField(
        verbose_name='Подтвержденный пользователь', default=False)
    registration_date = models.DateTimeField(
        verbose_name='Дата регистрации', auto_now_add=True)
    cart = OneToOneField(Cart, on_delete=models.SET_NULL,
                         null=True, related_name='related_account')
    delivery_address = CharField(
        verbose_name='Адрес доставки', default='Не указано(', max_length=180, blank=True)
    orders = ManyToManyField('Order', verbose_name='Заказы',
                             blank=True, null=True, related_name='related_account')

    def get_or_create_cart(self):
        if not self.cart:
            self.cart = Cart.objects.create(user=self.user)
            self.save()

        return self.cart

    def __str__(self):
        return f'Пользователь-> {self.user.username} | id-> {self.user.id}'


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        ac = Account.objects.create(user=instance)
        ac.cart = Cart.objects.create(user=ac.user)
        ac.save()


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()


@receiver(pre_delete, sender=User)
def delete_user_account(sender, instance, **kwargs):
    try:
        instance.account.delete()
    except:
        pass


class Order(models.Model):
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    STATUS_CHOICE = (
        ('new', 'Новый заказ'),
        ('in_progress', 'Заказ в обработке'),
        ('is_ready', 'Заказ собран'),
        ('delivered', 'Доставляется'),
        ('completed', 'Отдан покупателю')
    )

    BUYING_TYPE_CHOICE = (
        ('self', 'Самовывоз'),
        ('delivery', 'Доставка')
    )

    customer = ForeignKey('Account', on_delete=models.CASCADE,
                          verbose_name='Владелец заказа', related_name='related_orders')
    cart = ManyToManyField(
        CartProduct, related_name='related_order', verbose_name='продукты заказа')
    buying_type = CharField(choices=BUYING_TYPE_CHOICE,
                            default='delivery', max_length=50, verbose_name='Тип доставки')
    status = CharField(choices=STATUS_CHOICE, default='new',
                       max_length=50, verbose_name='Статус заказа')
    first_name = CharField(max_length=50, verbose_name='Имя')
    last_name = CharField(max_length=50, verbose_name='Фамилия')
    phone_number = CharField(max_length=13, verbose_name='Номер телефона')
    email = EmailField(verbose_name='Электронная почта', null=True)
    addres = CharField(max_length=300, verbose_name='Адрес доставки')
    comment = models.TextField(verbose_name='Комментарий к заказу',
                               max_length=300, null=True, blank=True)
    final_price = models.DecimalField(
        verbose_name='Общая цена товара/ов', max_digits=12, decimal_places=0, blank=True, default=0)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания заказа')
    is_paid = BooleanField(verbose_name='Заказ оплачен', default=False)
    order_date = models.DateTimeField(
        verbose_name='Жедаемая дата доставки', default=timezone.now)

    def __str__(self):
        return str(self.id)
