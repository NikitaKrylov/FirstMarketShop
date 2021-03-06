# Generated by Django 3.2 on 2021-09-26 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20210926_1801'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='final_price',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=12, verbose_name='Общая цена товара/ов'),
        ),
    ]
