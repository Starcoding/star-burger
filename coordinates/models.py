from django.db import models


class Coordinates(models.Model):
    latitude = models.DecimalField(
        'широта',
        max_digits=11,
        decimal_places=9
    )
    longtitude = models.DecimalField(
        'долгота',
        max_digits=11,
        decimal_places=9
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
