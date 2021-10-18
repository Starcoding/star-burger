# Generated by Django 3.2 on 2021-10-14 16:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_rename_registration_date_order_registration_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderelement',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_order_element', to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]
