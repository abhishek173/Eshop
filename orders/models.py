from django.db import models
from store.models import Customer,Products
from django.db.models import Sum,F
from utils.utility import generateOrderId
from datetime import datetime

class Cart(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name="customer_cart")
    is_paid = models.BooleanField(default=False)
    order_id = models.CharField(max_length=100,null=True,blank=True)
    payment_id = models.CharField(max_length=100,null=True,blank=True)
    payment_signature = models.CharField(max_length=1000,null=True,blank=True)

    def getCartTotal(self):
        total = self.cart_items.aggregate(
            total = Sum(F('product__price')*F('quantity'))
        )['total']
        return total or 0
    
    def convert_to_order(self):
        # Check if an order already exists for this cart
        if not Order.objects.filter(cart=self).exists():
            order = Order.objects.create(
                cart=self,
                customer=self.customer,
                payment_id=self.payment_id,
                payment_signature=self.payment_signature,
                total=self.getCartTotal()
            )
            # Copy all cart items to order items
            for cart_item in self.cart_items.all():
                OrderItems.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.getCartItemTotal()
                )



class CartItems(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cart_items")
    product = models.ForeignKey(Products,null=True,on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=0)

    def getCartItemTotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name="customer_order")
    date = models.DateField (default=datetime.today)
    order_id = models.CharField(max_length=100,null=True,blank=True)
    payment_id = models.CharField(max_length=100,null=True,blank=True)
    payment_signature = models.CharField(max_length=1000,null=True,blank=True) 
    total = models.FloatField()

    def save(self, *args,**kwargs):
        self.order_id = generateOrderId(str(Order.objects.count()+1))
        super(Order,self).save(*args,**kwargs)

    def __str__(self):
        return self.order_id
    
    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')
    

class OrderItems(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,null=True,on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=0)
    price = models.FloatField()