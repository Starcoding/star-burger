# Generated by Django 3.2 on 2021-08-19 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_auto_20210819_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('CS', 'Наличные'), ('CC', 'Картой курьеру'), ('CO', 'Картой онлайн')], default='CS', max_length=2),
        ),
    ]
