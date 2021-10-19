from django.core.validators import MinValueValidator
from django.db import migrations, models


def set_price(apps, schema_editor):
    OrderElement = apps.get_model('foodcartapp', 'OrderElement')

    for element in OrderElement.objects.all().prefetch_related('order_elements').iterator():
        element.price = element.product.price
        element.save(update_fields=['price'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_alter_order_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='OrderElement',
            name='price',
            field=models.DecimalField(
                null=True,
                verbose_name='цена',
                validators=[MinValueValidator(0)],
                max_digits=10,
                decimal_places=2
            )
        ),
        migrations.RunPython(set_price)
    ]
