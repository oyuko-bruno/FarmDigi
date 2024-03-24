from django.shortcuts import render, HttpResponse, redirect
from MavunoDigital.forms import UserRegistrationForm, ProductForm, MessageForm, VerificationForm
from MavunoDigital.models import Product, Message, Farmer, CartItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
from requests.auth import HTTPBasicAuth
import json
from django.http import JsonResponse
from django.views import View
from . credentials import MpesaAccessToken, LipanaMpesaPpassword


def home(request):
    show_product = Product.objects.all()
    return render(request, "index.html", {'show_product': show_product})


def f_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'farmer_dashboard.html')
        else:
            return render(request, 'farmer_login.html')

    else:
        return render(request, 'farmer_login.html')


def c_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'dashboard.html')
        else:
            return render(request, 'consumer_login.html')

    else:
        return render(request, 'consumer_login.html')


def farmer(request):
    submitted = False
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password1']
            return render(request, "farmer_login.html")
    else:
        user_form = UserRegistrationForm()
    return render(request, 'sell_on.html', {'user_form': user_form, 'submitted': submitted})


def consumer(request):
    submitted = False
    if request.method == "POST":
        consumer_form = UserRegistrationForm(request.POST)
        if consumer_form.is_valid():
            consumer_form.save()
            username = consumer_form.cleaned_data['username']
            password = consumer_form.cleaned_data['password1']
            return render(request, "consumer_login.html")
    else:
        consumer_form = UserRegistrationForm()
    return render(request, 'consumer_register.html', {'consumer_form': consumer_form, 'submitted': submitted})


def product_add(request):
    submitted = False
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, "farmer_dashboard.html")
    else:
        form = ProductForm
        if 'submitted' in request.GET:
            submitted = True
        return render(request, 'product_form.html', {'form': form, 'submitted': submitted})

    form = ProductForm
    return render(request, 'product_form.html', {'form': form})



from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404
from .models import Product, CartItem

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(product=product)
        if not created:
            cart_item.quantity += 1  # Increment the quantity directly
            cart_item.save()
    else:
        pass
    
    # Set the price field value before saving the CartItem instance
    cart_item.price = product.price
    
    try:
        cart_item.save()
    except IntegrityError as e:
        # Handle the IntegrityError (e.g., log the error, display a message to the user)
        pass
    
    return redirect('cart_view')



def cart_view(request):
    cart_items = CartItem.objects.filter()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def payment(request):
    cart_items = CartItem.objects.filter()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'payment.html', {'total_price': total_price})

def delete_item(request, item_id):
    # Retrieve the cart item object
    cart_item = get_object_or_404(CartItem, pk=item_id)
    
    # Check if the request method is POST (to avoid accidental deletions)
    if request.method == 'POST':
        # Delete the cart item
        cart_item.delete()
        # Redirect to the cart view
        return redirect('cart_view')
    else:
        # If the request method is not POST, handle it accordingly (e.g., show an error message)
        pass

def verification(request):
    submitted = False
    if request.method == "POST":
        v_form = VerificationForm(request.POST, request.FILES)
        if v_form.is_valid():
            v_form.save()
            return redirect('f_dash')
    else:
        v_form = VerificationForm
        if 'submitted' in request.GET:
            submitted = True
        return render(request, 'farmer_verification.html', {'v_form': v_form, 'submitted': submitted})

    v_form = VerificationForm
    return render(request, 'farmer_verification.html', {'v_form':v_form})


def verify_farmer(request):
    user = Farmer.objects.all()
    if user == Farmer.VERIFIED:
        return render(request, 'product_form.html')
    else:
        return render(request, 'farmer_verification.html', {'user': user})


def orders(request):
    return render(request, 'consumer_orders.html')


def contact(request):
    return render(request, 'contact.html')


def vegetables(request):
    vegetable_list = Product.objects.filter(product_category='Vegetable')
    return render(request, "vegetables.html",{'vegetable_list': vegetable_list})


def fruits(request):
    fruits_list = Product.objects.filter(product_category='Fruits')
    return render(request, "fruits.html",{'fruits_list': fruits_list})


def cereals(request):
    grain_list = Product.objects.filter(product_category='Grains')
    return render(request, "cereals.html",{'grain_list': grain_list})


def f_dashboard(request):
    return render(request, 'farmer_dashboard.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'inbox.html')
    else:
        form = MessageForm()
    return render(request, 'send_message.html', {'form':form})


def inbox(request):
    received_message = Message.objects.filter(recipient=request.user.first_name)
    sent_messages = Message.objects.filter(sender=request.user.first_name)
    return render(request, 'inbox.html', {'received_message':received_message, 'sent_messages':sent_messages})

###Mpesa intergration
def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})



def pay(request):
    if request.method =="POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "MavunoDigital",
            "TransactionDesc": "MavunoDigital Charges"
        }

        



    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse("success")


def stk(request):
    return render(request, 'pay.html', {'navbar':'stk'})
