from django.http import JsonResponse, HttpResponse
from django.templatetags.static import static
import json
import phonenumbers

from .models import Product
from .models import Order, OrderElement

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


def save_order(order_info):
    products_in_order = order_info.get('products')
    if products_in_order:
        first_name = order_info.get('firstname')
        last_name = order_info.get('lastname')
        phone_number_from_order = phonenumbers.parse(order_info.get('phonenumber'), None)
        if phonenumbers.is_possible_number(phone_number_from_order) and phonenumbers.is_valid_number(phone_number_from_order):
            phone_number = phone_number_from_order
        else:
            raise ValueError('Phone number is not valid!')
        delivery_address = order_info.get('address')
        new_order, created = Order.objects.get_or_create(first_name=first_name,
                                                        last_name=last_name,
                                                        phone_number=phone_number,
                                                        delivery_address=delivery_address)
        for item in products_in_order:
            product = Product.objects.get(id=item.get('product'))
            temp_element = OrderElement.objects.create(product=product, 
                                                    quantity=item.get('quantity'),
                                                    order=new_order)


def register_order(request):
    try:
        order_info = json.loads(request.body.decode())
        save_order(order_info)
    except Exception:
        return HttpResponse(status=500)
    return JsonResponse({'status': "Successfull",})
