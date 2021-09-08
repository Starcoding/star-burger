from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import OrderElement, Product, Restaurant, Order, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    original_orders = Order.info.price()
    extended_orders = []
    restaurants = [restaurant.name for restaurant in Restaurant.objects.all()]
    for order in original_orders:
        extended_order = {'id': order.id,
        'get_status_display': order.get_status_display,
        'get_payment_type_display': order.total_sum,
        'total_sum': order.total_sum,
        'firstname': order.firstname,
        'lastname': order.lastname,
        'phonenumber': order.phonenumber,
        'comment': order.comment,
        'address': order.address,
        'vacant_restaurants': [],
        }
        order_elements = OrderElement.objects.filter(order=order)
        vacant_restaurants = restaurants.copy()
        for order_element in order_elements:
            order_element_restaurants = [possible_restaurant.restaurant.name for possible_restaurant in RestaurantMenuItem.objects.filter(product=order_element.product)] # рестораны которые могут приготовить продукт из элемента заказа
            for reference_restaurant in restaurants:
                print(order_element_restaurants)
                if reference_restaurant not in order_element_restaurants:
                    try:
                        vacant_restaurants.remove(reference_restaurant)
                    except ValueError:
                        pass
        extended_order['vacant_restaurants'] = vacant_restaurants
        extended_orders.append(extended_order)


    return render(request, template_name='order_items.html', context={
        'order_items': extended_orders,
    })
