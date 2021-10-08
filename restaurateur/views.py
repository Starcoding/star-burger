from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from coordinates.models import Coordinates

from foodcartapp.models import OrderElement, Product, Restaurant, Order, RestaurantMenuItem
import copy
import requests
from geopy import distance
from star_burger.settings import YANDEX_KEY


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


def fetch_coordinates_from_geocoder(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": YANDEX_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    Coordinates.objects.create(address=address, longtitude=lon, latitude=lat)
    return lon, lat


def fetch_coordinates(address, coordinates):
    if coordinates:
        order_address = coordinates.filter(address=address).first()
        if order_address:
            lon = order_address.longtitude
            lat = order_address.latitude
            return lon, lat
        else:
            return fetch_coordinates_from_geocoder(address)
    else:
        return fetch_coordinates_from_geocoder(address)


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    original_orders = Order.objects.price()
    restaurants = []
    for restaurant in Restaurant.objects.all():
        temp_restaurant = {}
        temp_restaurant['name'] = restaurant.name
        temp_restaurant['address'] = restaurant.address
        temp_restaurant['distance'] = -1
    extended_orders = []
    for order in original_orders:
        temp_restaurants = copy.deepcopy(restaurants)
        order_elements = OrderElement.objects.filter(order=order)
        order_coordinates = fetch_coordinates(order.address, coordinates)
        vacant_restaurants = []
        for restaurant in temp_restaurants:
            restaurant_coordinates = fetch_coordinates(restaurant['address'],
                                                       coordinates)
            restaurant['distance'] = copy.copy(round(distance.distance(order_coordinates,
                                                                       restaurant_coordinates).km, 3))
            vacant_restaurants.append(restaurant.copy())
        for order_element in order_elements:
            order_element_restaurants = [
                {'name': possible_restaurant.restaurant.name,
                 'address': possible_restaurant.restaurant.address} for possible_restaurant in RestaurantMenuItem.objects.filter(product=order_element.product)]
            for reference_restaurant in restaurants:
                if reference_restaurant not in order_element_restaurants:
                    try:
                        vacant_restaurants.remove(reference_restaurant)
                    except ValueError:
                        pass
        extended_orders.append({'order': order,
                                'vacant_restaurants': vacant_restaurants})
    return render(request, template_name='order_items.html', context={
        'order_items': extended_orders,
    })
