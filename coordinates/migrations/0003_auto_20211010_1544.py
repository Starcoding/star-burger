# Generated by Django 3.2 on 2021-10-10 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0002_auto_20211010_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinates',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='latitude',
            field=models.DecimalField(decimal_places=9, max_digits=12, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='longtitude',
            field=models.DecimalField(decimal_places=9, max_digits=12, null=True, verbose_name='долгота'),
        ),
    ]