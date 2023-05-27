from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from greatkartapp.models import product_db,category_db,Cart,cart_item

# Create your views here.
def home(request):
    products=product_db.objects.all().filter(is_available=True)# filter(is_available=True) is using the product is availabe or not
    category=category_db.objects.all()
    context={
        'products': products,
        'category': category,
    }

    return render(request,"home.html",context)


def store(request, category_slug=None):
    categories=None
    products=None
    if category_slug != None:
        categories=get_object_or_404(category_db,slug=category_slug)
        products=product_db.objects.filter(category=categories,is_available=True)
        product_count=products.count
    else:
        products = product_db.objects.all().filter(is_available=True)  # filter(is_available=True) is using the product is availabe or not
        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request,'store/store.html',context)



def product_details(request,category_slug,product_slug):
    try:
        single_product=product_db.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    context={
        'single_product':single_product,
    }
    return render(request,'store/product_details.html',context)


def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def add_cart(request,product_id):
    product =product_db.objects.get(id=product_id)# get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))# get the cart using the cart_id present in the sesion
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
           cart_id = _cart_id(request)
        )
    cart.save()
    try:
        Cart_item=cart_item.objects.get(product=product,cart=cart)
        Cart_item.quantity+=1
        Cart_item.save()
    except cart_item.DoesNotExist:
        Cart_item=cart_item.objects.create(
            product=product,
            quantity=1,
            cart=cart,

        )
        Cart_item.save()
    return redirect(carts)





def carts(request,total=0,quantity=0,cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=cart_item.objects.filter(cart=cart,is_active=True)
        for crt_itm in cart_items:
            total+=(crt_itm.product.price*crt_itm.quantity)
            quantity+=crt_itm.quantity
        tax=(9 * total)/100
        grand_total=total+tax
    except ObjectNotExist:
        pass

    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,"store/cart.html",context)


def remove_cart_items(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(product_db,id=product_id)
    cart_items=cart_item.objects.get(product=product,cart=cart)
    if cart_items.quantity>1:
        cart_items.quantity-=1
        cart_items.save()
    else:
        cart_items.delete()
    return redirect('carts')



def remove_cart(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(product_db,id=product_id)
    cart_items=cart_item.objects.get(product=product,cart=cart)
    cart_items.delete()
    return redirect('carts')