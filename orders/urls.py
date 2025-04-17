from django.urls import path
from .views import *
from store.middlewares.auth import auth_middleware


urlpatterns = [
    path('add_Item_to_Cart/',auth_middleware(add_Item_to_Cart)),
    path('add-to-cart/', auth_middleware(add_to_cart)), 
    path('remove-cart-item/',remove_to_cart),
    path('cart/',auth_middleware(get_cart), name='cart'),
    path('success/',payment_success,name='payment_callback')
]
    