from django.urls import path
from greatkartapp import views

urlpatterns=[
    path('',views.home,name="home"),
    path('cart/',views.carts,name="carts"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('remove_cart_items/<int:product_id>/<int:cart_item_id>',views.remove_cart_items,name="remove_cart_items"),
    path('remove_cart/<int:product_id>/<int:cart_item_id>',views.remove_cart,name="remove_cart"),

    path('store/',views.store,name="store"),
    path('store/category/<slug:category_slug>/',views.store,name="products_by_category"),
    path('store/category/<slug:category_slug>/<slug:product_slug>/',views.product_details,name="product_details"),
    path('search/', views.search, name="search"),

    path('accounts/register/', views.register, name="register"),
    path('accounts/dashboard/', views.dashboard, name="dashboard"),
    path('accounts/', views.dashboard, name="dashboard"),
    path('accounts/login/', views.login, name="login"),
    path('accounts/logout/', views.logout, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),



    path('forgotPassword/', views.forgotPassword, name="forgotPassword"),
    path('resetpassword/', views.resetpassword, name="resetpassword"),
    path('resetpassword_validate/<uidb64>/<token>', views.resetpassword_validate, name="resetpassword_validate"),
    path('checkout/', views.checkout, name="checkout"),

]