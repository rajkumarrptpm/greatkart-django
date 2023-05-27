from django.urls import path
from greatkartapp import views

urlpatterns=[
    path('',views.home,name="home"),
    path('cart/',views.carts,name="carts"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('remove_cart_items/<int:product_id>/',views.remove_cart_items,name="remove_cart_items"),
    path('remove_cart/<int:product_id>/',views.remove_cart,name="remove_cart"),
    path('store/',views.store,name="store"),
    path('store/<slug:category_slug>/',views.store,name="products_by_category"),
    path('store/<slug:category_slug>/<slug:product_slug>/',views.product_details,name="product_details"),
]