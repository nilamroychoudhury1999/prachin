from .models import Product,Order
from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from time import time
from django.views.decorators.csrf import csrf_exempt
# for razorpay
import razorpay
client = razorpay.Client(auth=("rzp_test_s1GJSXv7cJJcGE","koYO8WATTmVmXAYKChFPnnYT"))


def cart_quantity(product,cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return cart.get(id)
    return 0
def price_total(product,cart):
    return product.price * cart_quantity(product , cart)
def Amount(products,cart):
    sum = 0 
    for p in products:
        sum += price_total(p , cart)
    return sum
def details(request):
    customer_id = request.session.get('customer_id')
    cart = request.session.get('cart')
    ids = list(request.session.get('cart').keys())
    products = Product.objects.filter(id__in =ids)
    return([customer_id,cart,ids,products])
# Create your views here.
def Base(request):
    return render(request,"home.html")
def Home(request):
    return render(request,"home.html")
def Product_list(request):
    prod = Product.objects.all()
    if request.method == "POST":
        print("session_id :",request.session.session_key)
        print("user id:",request.session.get('customer_id'))
        print("user name:",request.session.get('name'))
        prod_id = request.POST.get('prod_id')
        cart = request.session.get('cart')
        remove = request.POST.get('remove')
        if cart:
            quantity = cart.get(prod_id)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(prod_id)
                    else:
                        cart[prod_id]  = quantity-1
                else:
                    cart[prod_id]  = quantity+1
            else:
                cart[prod_id] = 1
        else:
            cart = {}
            cart[prod_id] = 1
        request.session['cart'] = cart
        print('cart :' , request.session['cart'])
        return redirect("Product_list")
    else:
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
        return render(request,"Product_list.html",{'products':prod})
def Orders(request):
    customer_id = request.session.get('customer_id')
    orders = Order.objects.filter(customer=customer_id).order_by('-date')
    return render(request,"orders.html",{"orders":orders})
def Sell(request):
    return render(request,"sell.html")
def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        myuser = authenticate(username=username,password=password)
        if myuser is not None:
            login(request,myuser)
            request.session['customer_id'] = myuser.id
            request.session['name'] = myuser.get_username()
            messages.success(request,"login Successfull")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
    return render(request,"login.html")
def SignUp(request):
    if request.method == "POST":
        username=request.POST.get('username')
        firstname=request.POST.get('fname')
        lastname=request.POST.get('lname')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        print(firstname)
        if pass1!=pass2:
            messages.info(request,"Password is not Matching")
            return redirect('/signup')
        try:
            if User.objects.get(username=username):
                messages.warning(request,"UserName is Taken")
                return redirect('/signup')
        except Exception as identifier:
            pass
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email is Taken")
                return redirect('/signup')
        except Exception as identifier:
            pass
        user = User.objects.create_user(username,email,pass1)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        messages.success(request,"User is Created Please Login")
        return redirect('/login')
    return render(request,"signup.html")
def handleLogout(request):
    for instance in Order.objects.filter(order_id = request.session.session_key):
        instance.delete()
    logout(request)
    messages.success(request,"Logout Success")    
    return redirect('/login')

def Cart(request):
    customer_id = request.session.get('customer_id')
    cart = request.session.get('cart')
    ids = list(request.session.get('cart').keys())
    products = Product.objects.filter(id__in =ids)
    print("Products are",products)
    print("cart is",cart)
    print("ids",ids)
    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        currently_ordered = Order.objects.filter(order_id = request.session.session_key)
        if currently_ordered is None:
            for product in products:
                order = Order(product = product, customer = User(id=customer_id),order_id=request.session.session_key,
                            quantity = cart.get(str(product.product_id)),
                            price = product.price, address = address, phone = phone)
                order.save()
        else:
            for product in products:
                if Order.objects.filter(product = product.product_id):
                    for instance in currently_ordered:
                        if instance.product.id == product.product_id:
                            instance.quantity = cart.get(str(product.product_id))
                            instance.save()
                else:
                    order = Order(product = product, customer = User(id=customer_id),order_id=request.session.session_key,
                            quantity = cart.get(str(product.product_id)),
                            price = product.price, address = address, phone = phone)
                    order.save()
        
            print("currently",currently_ordered) 
            for instance in currently_ordered:
                instance.phone = phone
                instance.address = address
                instance.save()
                if str(instance.product.product_id) not in ids:
                    instance.delete()

            print("currently",currently_ordered) 

        return redirect('Checkout')
    return render(request,"cart.html",{'products':products})

@login_required(login_url="/login")
def Checkout(request):
    print(request.session.get('cart'))
    cart = request.session.get('cart')
    ids = list(request.session.get('cart').keys())
    products = Product.objects.filter(id__in =ids)
    customer_id = request.session.get('customer_id')
    action = request.GET.get('action')
    create_order = None
    phone_no = Order.objects.filter(customer_id = customer_id).values_list('phone')[::-1][0][0]
    if action == "create_payment":
        Data = {
            'amount' : int(Amount(products,cart) * 100) ,
            'currency' : "INR",
            'receipt' : f"{request.session.session_key[15:]}{int(time())}",
            'notes' :{
                'email' : request.user.email,
                'phone' : phone_no
                }
        }
        create_order = client.order.create(data=Data)
    return render(request,"checkout.html",{"products":products,"order_object":create_order,"phone_number":phone_no})


@csrf_exempt
def verifyPayment(request):
    if request.method == "POST":
        data = request.POST
        print(data)
        try:
            client.utility.verify_payment_signature(data)
            payment = Order.objects.filter(order_id = request.session.session_key)
            for p in payment:
                print(p.order_id)
                print(p.status)
                p.status = True
                p.save()
            request.session['cart'] = {}
            logout(request)
            return redirect('/')
        except:
            return HttpResponse("Payment Failed")
    