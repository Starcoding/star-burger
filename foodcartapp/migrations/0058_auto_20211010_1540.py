# Generated by Django 3.2 on 2021-10-10 12:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_alter_orderelement_product'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('CS', 'Наличные'), ('CC', 'Картой курьеру'), ('CO', 'Картой онлайн'), ('CK', 'Уточнить у клиента')], db_index=True, default='CK', max_length=2, verbose_name='Вид оплаты'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category', to='foodcartapp.productcategory', verbose_name='категория'),
        ),
    ]
