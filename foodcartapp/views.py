from django.http import JsonResponse
from django.templatetags.static import static
import phonenumbers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.db import transaction
from .models import Product
from .models import Order, OrderElement


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


def save_order(order_info):
    products_in_order = order_serializer.validated_data.get('products')
    first_name = order_serializer.validated_data.get('firstname')
    last_name = order_serializer.validated_data.get('lastname')
    phone_number_from_order = phonenumbers.parse(order_serializer.validated_data.get(
                                                 'phonenumber'), None)
    phone_number = phone_number_from_order
    delivery_address = order_serializer.validated_data.get('address')
    new_order = Order.additional_set.create(firstname=first_name,
                                            lastname=last_name,
                                            phonenumber=phone_number,
                                            address=delivery_address)
    new_order.save()
    for item in products_in_order:
        product = Product.objects.get(name=item.get('product'))
        element = OrderElement.objects.create(product=item.get('product'),
                                              quantity=item.get('quantity'),
                                              order=new_order,
                                              price=product.price)
        element.save()
    return new_order


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)
    try:
        products_in_order = order_serializer.validated_data.get('products')
        first_name = order_serializer.validated_data.get('firstname')
        last_name = order_serializer.validated_data.get('lastname')
        phone_number_from_order = phonenumbers.parse(order_serializer.validated_data.get(
                                                     'phonenumber'), None)
        phone_number = phone_number_from_order
        delivery_address = order_serializer.validated_data.get('address')
        new_order = Order.additional_set.create(firstname=first_name,
                                                lastname=last_name,
                                                phonenumber=phone_number,
                                                address=delivery_address)
        new_order.save()
        for item in products_in_order:
            product = Product.objects.get(name=item.get('product'))
            element = OrderElement.objects.create(product=item.get('product'),
                                                  quantity=item.get('quantity'),
                                                  order=new_order,
                                                  price=product.price)
            element.save()
    except Exception as e:
        return Response({'error': f'Error occured: {e}'})
    response = {
        "id": new_order.id,
        "firstname": new_order.firstname,
        "lastname": new_order.lastname,
        "phonenumber": str(new_order.phonenumber),
        "address": new_order.address,
    }
    return Response(response)
