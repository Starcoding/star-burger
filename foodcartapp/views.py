import phonenumbers
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import Order, OrderElement, Product


class OrderElementSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderElementSerializer(write_only=True,
                                      many=True,
                                      allow_empty=False)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products']


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


REQUIRED_FIELDS = ['firstname', 'lastname', 'phonenumber', 'address']


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)
    products_in_order = order_serializer.validated_data['products']
    first_name = order_serializer.validated_data['firstname']
    last_name = order_serializer.validated_data['lastname']
    phone_number_from_order = phonenumbers.parse(order_serializer.validated_data[
                                                    'phonenumber'], None)
    delivery_address = order_serializer.validated_data['address']
    new_order = Order.objects.create(firstname=first_name,
                                            lastname=last_name,
                                            phonenumber=phone_number_from_order,
                                            address=delivery_address)
    for item in products_in_order:
        product = Product.objects.get(name=item['product'])
        element = OrderElement.objects.create(product=item['product'],
                                                quantity=item['quantity'],
                                                order=new_order,
                                                price=product.price)
    response = {
        "id": new_order.id,
        "firstname": new_order.firstname,
        "lastname": new_order.lastname,
        "phonenumber": str(new_order.phonenumber),
        "address": new_order.address,
    }
    return Response(response)
