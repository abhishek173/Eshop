from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from .models import Cart,CartItems,Products,Customer
from django.contrib import messages
from .payment import RazorPayPayment
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

def add_Item_to_Cart(request):
    try:
        customer_id = request.session.get('customer')
        customer = Customer.objects.get(id=customer_id)
        product_id = request.GET.get('product_id')
        product = Products.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(customer=customer,is_paid=False)
        cart_item, _ = CartItems.objects.get_or_create(cart=cart,product=product)
        if cart_item.quantity == 0:
            cart_item.quantity = 1 
        cart_item.save()
        return HttpResponseRedirect('/order/cart/')
    except Exception as e:
        print(e)
        messages.error(request,'Invalid Product ID')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_to_cart(request):
    try:
        customer_id = request.session.get('customer')
        customer = Customer.objects.get(id=customer_id)
        product_id = request.GET.get('product_id')
        product = Products.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(customer=customer,is_paid=False)
        cart_item, _ = CartItems.objects.get_or_create(cart=cart,product=product)
        cart_item.quantity += 1 
        cart_item.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        print(e)
        messages.error(request,'Invalid Product ID')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def remove_to_cart(request):
    try:
        customer_id = request.session.get('customer')
        customer = Customer.objects.get(id=customer_id)
        product_id = request.GET.get('product_id')
        product = Products.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(customer=customer,is_paid=False)
        cart_item = CartItems.objects.filter(cart=cart,product=product)
        if cart_item.exists():
            cart_item = cart_item[0]
            cart_item.quantity -= 1 

            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        print(e)
        messages.error(request,'Invalid Product ID')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

def get_cart(request):
    cart = None
    payment_info = {}
    customer_id = request.session.get('customer')
    try:
        customer = Customer.objects.get(id=customer_id)
        cart = Cart.objects.get(customer=customer,is_paid=False)
        amount = cart.getCartTotal()
        receipt = cart.customer.first_name
        payment = RazorPayPayment("INR")
        payment_info = payment.processPayment(amount*100,receipt)
        cart.order_id = payment_info['id']
        print("cart order id generated at processing :",payment_info['id'])
        cart.save()
    except Exception as e:
        print(e)
    return render(request,'cart.html',context={'cart':cart, 'payment_info':payment_info})


import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from orders.models import Cart  # Ensure correct import

@csrf_exempt
def payment_success(request):
    try:
        # Try to decode JSON first
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)
        else:
            data = request.POST  # Handle form data

        # Extract Razorpay details
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        print("Cart order ID generated at querying:", razorpay_order_id)

        # Validate order ID
        if not razorpay_order_id:
            return JsonResponse({"error": "Missing order_id"}, status=400)

        # Fetch and update cart
        cart = Cart.objects.get(order_id=razorpay_order_id)
        cart.is_paid = True
        cart.payment_id = razorpay_payment_id
        cart.payment_signature = razorpay_signature
        cart.save()
        
        # Convert cart to order if required
        if hasattr(cart, 'convert_to_order'):
            cart.convert_to_order()

        return render(request, 'success.html')

    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart not found for given order ID"}, status=404)

    except Exception as e:
        print("Payment success error:", e)
        return JsonResponse({"error": str(e)}, status=500)


    
    