# Generated by Django 3.2 on 2021-10-10 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinates',
            name='address',
            field=models.CharField(max_length=100, unique=True, verbose_name='адрес'),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='latitude',
            field=models.DecimalField(decimal_places=9, max_digits=11, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='longtitude',
            field=models.DecimalField(decimal_places=9, max_digits=11, null=True, verbose_name='долгота'),
        ),
    ]