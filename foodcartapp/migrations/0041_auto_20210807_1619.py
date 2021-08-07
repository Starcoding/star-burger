# Generated by Django 3.2 on 2021-08-07 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20210807_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderelement',
            options={'verbose_name': 'элемент заказа', 'verbose_name_plural': 'элементы заказа'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_elements',
        ),
        migrations.AddField(
            model_name='orderelement',
            name='order',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='order_elements', to='foodcartapp.order', verbose_name='заказ'),
            preserve_default=False,
        ),
    ]
