# Generated by Django 3.2 on 2021-08-14 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_rename_amount_orderelement_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='delivery_address',
            new_name='deliveryaddress',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone_number',
            new_name='phonenumber',
        ),
    ]
