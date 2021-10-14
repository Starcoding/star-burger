import copy

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from coordinates.fetcher import (fetch_coordinates,
                                 fetch_coordinates_from_geocoder)
from coordinates.models import Coordinates
from foodcartapp.models import (Order, OrderElement, Product, Restaurant,
                                RestaurantMenuItem)


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
    coordinates = list(Coordinates.objects.all())
    orders = list(Order.objects.calculate_price().filter(status='NP').prefetch_related('order_elements__product'))
    restaurants = Restaurant.objects.all()
    restaurant_menu_items = RestaurantMenuItem.objects.all().prefetch_related('product').prefetch_related('restaurant')
    extended_orders = []
    for order in orders:
        vacant_restaurants = copy.copy(restaurants)
        order_elements = order.order_elements.all()
        order_coordinates = fetch_coordinates(order.address, coordinates)
        for order_element in order_elements:
            restaurants_with_items = []
            for restaurant_menu_item in restaurant_menu_items:
                if order_element.product == restaurant_menu_item.product:
                    restaurants_with_items.append(restaurant_menu_item.restaurant)
            vacant_restaurants = copy.deepcopy(set(vacant_restaurants).intersection(restaurants_with_items))
        for vacant_restaurant in vacant_restaurants:
            vacant_restaurant.coordinates = fetch_coordinates(vacant_restaurant.address, coordinates)
            vacant_restaurant.distance = round(distance.distance(order_coordinates,
                                                             vacant_restaurant.coordinates).km, 3)
        extended_orders.append({'order': order,
                                'vacant_restaurants': vacant_restaurants})
    return render(request, template_name='order_items.html', context={
        'order_items': extended_orders,
    })
