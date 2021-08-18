from django.http import JsonResponse
from django.templatetags.static import static
import json
import phonenumbers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import Product
from .models import Order, OrderElement



class OrderElementSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderElementSerializer(write_only=True, many=True, allow_empty=False)
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']



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


# {'products': [{'product': 2, 'quantity': 1}, {'product': 1, 'quantity': 1}, {'product': 3, 'quantity': 1}, {'product': 4, 'quantity': 1}, {'product': 6, 'quantity': 1}], 
# 'firstname': 'юрий', 'lastname': 'Старовойт', 'phonenumber': '+79999788032', 'address': 'Брянск, горького 25'}
REQUIRED_FIELDS = ['firstname', 'lastname', 'phonenumber', 'address']


# TODO: Rework saving of new_order.
def save_order(order_info):
    products_in_order = order_info.get('products')
    first_name = order_info.get('firstname')
    last_name = order_info.get('lastname')
    phone_number_from_order = phonenumbers.parse(order_info.get('phonenumber'), None)
    phone_number = phone_number_from_order
    delivery_address = order_info.get('address')
    new_order = Order.info.create(firstname=first_name,
                                                    lastname=last_name,
                                                    phonenumber=phone_number,
                                                    address=delivery_address)
    for item in products_in_order:
        product = Product.objects.get(name=item.get('product'))
        element = OrderElement.objects.create(product=item.get('product'), 
                                                quantity=item.get('quantity'),
                                                order=new_order,
                                                price=product.price)
        element.save()
    return new_order
    


@api_view(['POST'])
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)
    saved_order = save_order(order_serializer.validated_data)
    response = {
        "id": saved_order.id,
        "firstname": saved_order.firstname,
        "lastname": saved_order.lastname,
        "phonenumber": str(saved_order.phonenumber),
        "address": saved_order.address,
    }
    return Response(response)

