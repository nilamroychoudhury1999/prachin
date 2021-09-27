from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.Product_list,name="Product_list"),
    path('',views.Base,name="Base"),
    path('',views.Home,name="Home"),
    path('cart',views.Cart,name="Cart"),
    path('orders',views.Orders,name="Orders"),
    path('checkout',views.Checkout,name="Checkout"),
    path('login',views.Login,name="Login"),
    path('signup',views.SignUp,name="SignUp"),
    path('logout',views.handleLogout,name="handleLogout"),
    path('sell',views.Sell,name="sell"),  
    path('pay',views.verifyPayment,name="verifyPayment"),
]