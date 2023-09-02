from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from user_app.models import *
from cart.models import *
from shop.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from order.models import *
from django.http import JsonResponse



# path('add-cart-quandity/', views.add_cart_quandity, name="add_cart_quandity"),
# path('remove-cart-quandity/', views.remove_cart_quandity, name="remove_cart_quandity"),


@cache_control(no_cache=True, no_store=True)
def add_cart_quandity(request):
    if request.method == 'POST':
        grant_total = 0
        delivery_charge = 99
        total_amount = 0
        variant_id = request.POST.get('product_id')
        product_quantity = request.POST.get('product_quandity')
        variant = ProductVariant.objects.get(id=variant_id)
        
        if 'user' in request.session:
            my_user = request.user

            try:
                cart_item = CartItem.objects.get(customer=my_user, product=variant)
                if variant.stock > cart_item.quantity:
                    cart_item.quantity += 1
                else:
                    messages.error(request, "No more products available in the current variant")

                cart_item.save()
                product_quantity = cart_item.quantity
                total = cart_item.product.product_price * cart_item.quantity

                cart_items = CartItem.objects.filter(customer=my_user)
                
                for item in cart_items: 
                    grant_total += (item.product.product_price * item.quantity)

            except CartItem.DoesNotExist:
                pass

            try:
                #check out handling
                checkout = Checkout.objects.get(user=my_user.id)
                
                checkout.total = grant_total
                if grant_total > 2500:
                    delivery_charge = 0
                checkout.shipping = delivery_charge                         # checkout saving delivery charge
             
                tax = (grant_total * 3) // 100
                checkout.tax = tax
                total_amount = (grant_total + tax + delivery_charge)  # calculating grand total.
                checkout.grand_total = total_amount

                checkout.save()
            except Checkout.DoesNotExist:
                pass

                
            except CartItem.DoesNotExist:
                pass
        return JsonResponse({
            'quantity': product_quantity,
            'total': total,
            'grant_total': grant_total,
            'total_amount': checkout.grand_total,
            'tax': checkout.tax,
        })




@cache_control(no_cache=True, no_store=True)
def remove_cart_quandity(request):
    
    if request.method == 'POST':
        grant_total = 0
        delivery_charge = 99
        total_amount = 0
        variant_id = request.POST.get('product_id')
        product_quantity = request.POST.get('product_quandity')
        variant = ProductVariant.objects.get(id=variant_id)

        if 'user' in request.session:
            my_user = request.user.id
            try:
                cart_item = CartItem.objects.get(product=variant, customer=my_user)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    
                else:
                    cart_item.delete()

                cart_item.save()
                product_quantity = cart_item.quantity
                total = cart_item.product.product_price * cart_item.quantity

                cart_items = CartItem.objects.filter(customer=my_user).order_by('id')
                for item in cart_items: 
                    grant_total += (item.product.product_price * item.quantity)

            except CartItem.DoesNotExist:
                pass

            try:
                #check out handling
                checkout = Checkout.objects.get(user=my_user)
                
                checkout.total = grant_total
                if grant_total > 2500:
                    delivery_charge = 0
                checkout.shipping = delivery_charge                         # checkout saving delivery charge
             
                tax = (grant_total * 3) // 100
                checkout.tax = tax
                total_amount = (grant_total + tax + delivery_charge)  # calculating grand total.
                checkout.grand_total = total_amount

                checkout.save()
            except Checkout.DoesNotExist:
                pass

        return JsonResponse({
            'quantity': product_quantity,
            'total': total,
            'grant_total': grant_total,
            'total_amount': checkout.grand_total,
            'tax': checkout.tax,
            })
    else:
        return redirect('cart')