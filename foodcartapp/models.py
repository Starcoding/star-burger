from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def price(self):
        return self.annotate(
                             total_sum=Sum(F('order_elements__price') * F(
                                             'order_elements__quantity')))


class Order(models.Model):
    firstname = models.CharField(
        'имя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField(
        'номер телефона'
    )
    address = models.CharField(
        'адрес доставки',
        max_length=100
    )
    NOT_PROCESSED = 'NP'
    CANCELLED = 'CC'
    COMPLETED = 'CM'
    STATUSES = [
        (NOT_PROCESSED, 'Необработанный'),
        (CANCELLED, 'Отменён'),
        (COMPLETED, 'Выполнен'),
    ]
    status = models.CharField(
        'Статус заказа',
        max_length=2,
        choices=STATUSES,
        default=NOT_PROCESSED,
    )
    CASH = 'CS'
    CARD_TO_COURIER = 'CC'
    CARD_ONLINE = "CO"
    PAYMENT_TYPES = [
        (CASH, 'Наличные'),
        (CARD_TO_COURIER, 'Картой курьеру'),
        (CARD_ONLINE, 'Картой онлайн'),
    ]
    payment_type = models.CharField(
        'Вид оплаты',
        max_length=2,
        choices=PAYMENT_TYPES,
        default=CASH,
    )
    comment = models.TextField(
        'Комментарий',
        blank=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='ресторан',
        related_name='orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    registration_date = models.DateTimeField(
        'Время регистрации заказа',
        default=timezone.now
    )
    call_date = models.DateTimeField(
        'Время звонка',
        blank=True,
        null=True
    )
    delivery_date = models.DateTimeField(
        'Когда доставлено',
        blank=True,
        null=True
    )
    info = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} | {self.address}'


class OrderElement(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='продукт',
    )
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(0)]
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_elements',
        verbose_name='заказ',
        blank=True
    )
    price = models.DecimalField(
        'цена',
        validators=[MinValueValidator(0)],
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product} | {self.order}'
