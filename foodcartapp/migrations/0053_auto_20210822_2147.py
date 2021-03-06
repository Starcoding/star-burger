# Generated by Django 3.2 on 2021-08-22 18:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_order_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('CS', 'Наличные'), ('CC', 'Картой курьеру'), ('CO', 'Картой онлайн')], default='CS', max_length=2, verbose_name='Вид оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NP', 'Необработанный'), ('CC', 'Отменён'), ('CM', 'Выполнен')], default='NP', max_length=2, verbose_name='Статус заказа'),
        ),
    ]
