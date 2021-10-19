from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


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
        related_name='category',
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
    def calculate_price(self):
        return self.annotate(
                             total_sum=Sum(F('order_elements__price') * F(
                                             'order_elements__quantity')))


class Order(models.Model):
    NOT_PROCESSED = 'NP'
    CANCELLED = 'CC'
    COMPLETED = 'CM'
    STATUSES = [
        (NOT_PROCESSED, 'Необработанный'),
        (CANCELLED, 'Отменён'),
        (COMPLETED, 'Выполнен'),
    ]
    CASH = 'CS'
    CARD_TO_COURIER = 'CC'
    CARD_ONLINE = "CO"
    CHECK_WITH_CLIENT = 'CK'
    PAYMENT_TYPES = [
        (CASH, 'Наличные'),
        (CARD_TO_COURIER, 'Картой курьеру'),
        (CARD_ONLINE, 'Картой онлайн'),
        (CHECK_WITH_CLIENT, 'Уточнить у клиента')
    ]
    firstname = models.CharField(
        'имя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField(
        'номер телефона',
        db_index=True,
    )
    address = models.CharField(
        'адрес доставки',
        max_length=100
    )
    status = models.CharField(
        'Статус заказа',
        max_length=2,
        choices=STATUSES,
        default=NOT_PROCESSED,
        db_index=True,
    )
    payment_type = models.CharField(
        'Вид оплаты',
        max_length=2,
        choices=PAYMENT_TYPES,
        default=CHECK_WITH_CLIENT,
        db_index=True,
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
    registration_at = models.DateTimeField(
        'Время регистрации заказа',
        default=timezone.now,
        db_index=True,
    )
    call_date = models.DateTimeField(
        'Время звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivery_date = models.DateTimeField(
        'Когда доставлено',
        blank=True,
        null=True,
        db_index=True,
    )
    objects = OrderQuerySet.as_manager()

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
        related_name='order_elements',
    )
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1)]
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_elements',
        verbose_name='заказ',
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
