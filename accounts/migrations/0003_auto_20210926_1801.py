# Generated by Django 3.2 on 2021-09-26 15:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_delete_order'),
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buying_type', models.CharField(choices=[('self', 'Самовывоз'), ('delivery', 'Доставка')], default='delivery', max_length=50, verbose_name='Тип доставки')),
                ('status', models.CharField(choices=[('new', 'Новый заказ'), ('in_progress', 'Заказ в обработке'), ('is_ready', 'Заказ собран'), ('delivered', 'Доставляется'), ('completed', 'Отдан покупателю')], default='new', max_length=50, verbose_name='Статус заказа')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('phone_number', models.CharField(max_length=13, verbose_name='Номер телефона')),
                ('addres', models.CharField(max_length=300, verbose_name='Адрес доставки')),
                ('comment', models.TextField(blank=True, max_length=300, null=True, verbose_name='Комментарий к заказу')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Жедаемая дата доставки')),
                ('cart', models.ManyToManyField(related_name='related_order', to='orders.CartProduct', verbose_name='продукты заказа')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_orders', to='accounts.account', verbose_name='Владелец заказа')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='orders',
            field=models.ManyToManyField(blank=True, null=True, related_name='related_account', to='accounts.Order', verbose_name='Заказы'),
        ),
    ]
