# Generated by Django 3.2 on 2021-09-25 13:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_auto_20210925_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderelement',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]
