# Create your views here.
from django.shortcuts import render , redirect , HttpResponseRedirect,HttpResponse
from django.views import View
from store.models import Products
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from store.models import Customer
from store.models import Category
from django.core.paginator import Paginator, EmptyPage
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from .forms import AddressForm
from django.conf import settings
import logging
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from orders.models import CartItems,Order
from django.db.models import Q


def store(request):

    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    query = request.GET.get('q')

    # Fetch products
    products = Products.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |  
            Q(category__name__icontains=query) |  
            Q(description__icontains=query)
        )
    
    if categoryID:
        products = products.filter(category_id=categoryID)
        selected_category = Category.objects.get(id=categoryID)
    else:
        selected_category = None
    
    # Paginate the products (8 products per page)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    try:
        serviceDataFinal = paginator.get_page(page_number)
    except EmptyPage:
        serviceDataFinal = paginator.get_page(1)

    # Get cart item count
    customer = request.session.get('customer', None)
    cart_item_count = CartItems.objects.filter(cart__customer=customer, cart__is_paid=False).count() if customer else 0

    # Debug print
    print('Logged in user:', request.session.get('email'))

    # Get cart item count
    if request.session.get('customer'):
        customer = request.session.get('customer')
        cart_item_count = CartItems.objects.filter(cart__customer=customer, cart__is_paid=False).count()
    else:
        cart_item_count = 0

    # Merge data into context
    data = {
        'products': serviceDataFinal,
        'lastpage': serviceDataFinal.paginator.num_pages,
        'totalPageList': [i + 1 for i in range(serviceDataFinal.paginator.num_pages)],
        'categories': categories,
        'selected_category': selected_category,
        'cart_item_count': cart_item_count
    }
    
    # **Pass only one dictionary to render**
    return render(request, 'index.html', data)


# class Login(View):
#     return_url = None

#     def get(self, request):
#         Login.return_url = request.GET.get ('return_url')
#         return render (request, 'login.html')

#     def post(self, request):
#         email = request.POST.get ('email')
#         password = request.POST.get ('password')
#         customer = Customer.get_customer_by_email (email)
#         error_message = None
#         if customer:
#             flag = check_password (password, customer.password)
#             if flag:
#                 request.session['customer'] = customer.id

#                 if Login.return_url:
#                     return HttpResponseRedirect (Login.return_url)
#                 else:
#                     Login.return_url = None
#                     return redirect ('homepage')
#             else:
#                 error_message = 'Invalid !!'
#         else:
#             error_message = 'Invalid !!'

#         print (email, password)
#         return render (request, 'login.html', {'error': error_message})
    
class Login(View):
    def get(self, request):
        return_url = request.GET.get('return_url', None)
        return render(request, 'login.html', {'return_url': return_url})

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        return_url = request.POST.get('return_url', None)  # Get return_url from form

        customer = Customer.get_customer_by_email(email)
        error_message = None

        if customer and check_password(password, customer.password):
            request.session['customer'] = customer.id
            if return_url:
                return HttpResponseRedirect(return_url)  # Redirect back to original page
            return redirect('homepage')  # Default redirect
        else:
            error_message = 'Invalid email or password'

        return render(request, 'login.html', {'error': error_message, 'return_url': return_url})

def logout(request):
    request.session.clear()
    return redirect('login')


class OrderView(View):


    def get(self , request ):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request , 'orders.html'  , {'orders' : orders})

class Signup (View):
    def get(self, request):
        return render (request, 'signup.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get ('firstname')
        last_name = postData.get ('lastname')
        phone = postData.get ('phone')
        email = postData.get ('email')
        password = postData.get ('password')
        # validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer (first_name=first_name,
                             last_name=last_name,
                             phone=phone,
                             email=email,
                             password=password)
        error_message = self.validateCustomer (customer)

        if not error_message:
            print (first_name, last_name, phone, email, password)
            customer.password = make_password (customer.password)
            customer.register ()
            return redirect ('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render (request, 'signup.html', data)

    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = "Please Enter your First Name !!"
        elif len (customer.first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name:
            error_message = 'Please Enter your Last Name'
        elif len (customer.last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len (customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len (customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len (customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists ():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message


class ProductView(View):

    def get(self,request,product_id):
        customer =  request.session.get('customer')
        product = get_object_or_404(Products, id=product_id)
        images = product.images.all()
        return render(request, 'product_detail.html', {'product': product, 'images': images,'customer':customer})

# class AddressView(View):
#     def get(self, request, product_id):
#         customer = request.session.get('customer')
#         product = get_object_or_404(Products, id=product_id)
#         images = product.images.all()
#         form = AddressForm()
#         return render(request, 'address_form.html', {'form': form, 'product': product, 'images': images,'customer':customer})
    
#     def post(self, request, product_id):
#         product = get_object_or_404(Products, id=product_id)
#         form = AddressForm(request.POST)
        
#         if form.is_valid():
#             try:
#                 # Get customer information from session
#                 customer_id = request.session.get('customer')
#                 if not customer_id:
#                     return redirect('login')  # Redirect if customer not in session
                
#                 customer = Customer.objects.get(id=customer_id)
                
#                 # Get address details from form
#                 address = form.cleaned_data['street_address']
#                 city = form.cleaned_data['city']
#                 postal_code = form.cleaned_data['postal_code']
#                 country = form.cleaned_data['country']
#                 contact_no = form.cleaned_data['contact_number']

#                 # Create an order instance (store the order in the database)
#                 with transaction.atomic():
#                     order = Order.objects.create(
#                         product=product,
#                         customer=customer,
#                         price=product.price,
#                         status=False
#                     )

#                     # Prepare email details
#                     customer_email = customer.email
#                     customer_name = f"{customer.first_name} {customer.last_name}"
#                     order_details = (
#                         f"Product Name: {product.name}\n"
#                         f"Price: {product.price}\n"
#                     )
#                     shipping_address = f"{address}, {city}, {postal_code}, {country}"
                    
#                     # Email subject and message
#                     subject = "Order Placed Successfully"
#                     message = (
#                         f"Dear {customer_name},\n\n"
#                         f"Your order has been placed successfully.\n\n"
#                         f"Order Details:\n{order_details}"
#                         f"Contact Number: {contact_no}\n"
#                         f"Shipping Address:\n{shipping_address}\n\n"
#                         "Thank you for shopping with us!"
#                     )

#                     # Send email to the customer
#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [customer_email],
#                         fail_silently=False,
#                     )

#                 # Store order details in session for the success page
#                 request.session['order_details'] = order_details

#                 # Redirect to the success page
#                 return redirect(reverse('buy_success'))
            
#             except ObjectDoesNotExist:
#                 logging.error("Customer does not exist or invalid customer ID.")
#                 return redirect('login')  # Redirect to login if customer not found
            
#             except Exception as e:
#                 logging.error(f"Error processing order: {str(e)}")
#                 return render(request, 'error_page.html', {'error': "Order processing failed."})
        
#         return render(request, 'address_form.html', {'form': form, 'product': product,'customer':customer})


class BuyNowView(View):
    def get(self, request, product_id):
        # Redirect to the address form page
        return redirect(reverse('address', args=[product_id]))

# BuySuccessView displays the success message
class BuySuccessView(TemplateView):
    template_name = 'buy_success.html'

def repair_request(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        description = request.POST['description']
        contact_info = request.POST['contact_info']

        # Compose the email message
        subject = f"Repair Request for {product_name}"
        message = f"Product Name: {product_name}\nDescription: {description}\nContact Info: {contact_info}"
        recipient_email = 'munnakumar@gmail.com'

        # Send the email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        # Redirect or show a success message
        return HttpResponse('<center> Repair request submitted successfully!<center>')
    

def contact_us(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')  # Customer's email
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            # Sending email to Admin
            send_mail(
                f'Contact Us Form - {subject}',
                f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                settings.EMAIL_HOST_USER,  # Sender Email (must be your configured email)
                ['zamzamelectronicsonline98944@gmail.com'],  # Admin's email
                fail_silently=False,
            )

            # Sending confirmation email to Customer
            send_mail(
                f'Thank You for Contacting Us - {subject}',
                f'Dear {name},\n\nThank you for reaching out to us! '
                'We have received your message and will get back to you soon.\n\n'
                'Best regards,\nZamZam Electronics Team',
                settings.EMAIL_HOST_USER,  # Sender Email
                [email],  # Customer's Email
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact_us')
        else:
            messages.error(request, "All fields are required!")

    return render(request, 'contact_us.html')



def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def cancellation_refund(request):
    return render(request, 'cancellation_refund.html')

def shipping_delivery(request):
    return render(request, 'shipping_delivery.html')

