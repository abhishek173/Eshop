from django.contrib import admin
from django.urls import path
from .views import * 
from .middlewares.auth import auth_middleware


urlpatterns = [
    # path('', Index.as_view(), name='homepage'),
    path('', store, name='homepage'),
    # path('store', store , name='store'),
    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout , name='logout'),
    # path('cart', auth_middleware(Cart.as_view()) , name='cart'),
    # path('check-out', CheckOut.as_view() , name='checkout'),
    path('orders', auth_middleware(OrderView.as_view()), name='orders'),
    path('checkout/<int:product_id>/', BuyNowView.as_view(), name='buy_now'),
    path('product/<int:product_id>/', ProductView.as_view(), name='product_detail'),
    # path('address/<int:product_id>/', AddressView.as_view(), name='address'),
    path('buy_success/', BuySuccessView.as_view(), name='buy_success'),
    path('submit-repair-request/',repair_request , name='repair_request'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-of-service/', terms_of_service, name='terms_of_service'),
    path('cancellation-refund/', cancellation_refund, name='cancellation_refund'),
    path('shipping-delivery/', shipping_delivery, name='shipping_delivery'),
    path('contact/', contact_us, name='contact_us'),
]
