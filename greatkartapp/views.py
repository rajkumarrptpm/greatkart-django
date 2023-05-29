from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from greatkartapp.models import product_db, category_db, Cart, cart_item, Variation
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


# Create your views here.
def home(request):
    products = product_db.objects.all().filter(
        is_available=True)  # filter(is_available=True) is using the product is availabe or not
    category = category_db.objects.all()
    context = {
        'products': products,
        'category': category,
    }

    return render(request, "home.html", context)


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(category_db, slug=category_slug)
        products = product_db.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 3)  # paginator 5
        page = request.GET.get('page')  # paginator 6
        page_products = paginator.get_page(page)  # paginator 7
        product_count = products.count
    else:
        products = product_db.objects.all().filter(is_available=True).order_by(
            'id')  # filter(is_available=True) is using the product is availabe or not
        paginator = Paginator(products, 6)  # paginator 2
        page = request.GET.get('page')  # paginator 3
        page_products = paginator.get_page(page)  # paginator 4
        product_count = products.count()

    context = {
        'products': page_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):

    try:
        single_product = product_db.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
    }
    return render(request, 'store/product_details.html', context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = product_db.objects.get(id=product_id)  # get the product
    product_variation=[]

    if request.method == "POST":
        for item in request.POST:
            key=item
            value=request.POST[key]

            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass


    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    is_cart_item_exists=cart_item.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        Cart_item = cart_item.objects.filter(product=product, cart=cart)
        # 1.existing variation -> database
        # 2.current variation -> product_variation
        # 3.current_id
        exi_var_list=[]
        id=[]
        for item in Cart_item:
            existing_variation=item.variations.all()
            exi_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in exi_var_list:
            # Increase the cart item quantity
            index=exi_var_list.index(product_variation)
            item_id=id[index]
            item=cart_item.objects.get(product=product,id=item_id)
            item.quantity+=1
            item.save()

        else:
            # create new cart item
            Cart_items=cart_item.objects.create(product=product, quantity=1, cart=cart)

            if len(product_variation) > 0:
                Cart_items.variations.clear()
                Cart_items.variations.add(*product_variation)
            Cart_items.save()
    else:
        Cart_item = cart_item.objects.create(
            product=product,
            quantity=1,
            cart=cart,

        )
        if len(product_variation) > 0:
            Cart_item.variations.clear()
            Cart_item.variations.add(*product_variation)
        Cart_item.save()
    return redirect(carts)


def carts(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = cart_item.objects.filter(cart=cart, is_active=True)
        for crt_itm in cart_items:
            total += (crt_itm.product.price * crt_itm.quantity)
            quantity += crt_itm.quantity
        tax = (9 * total) / 100
        grand_total = total + tax
        grand_total=round(grand_total,2)
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, "store/cart.html", context)


def remove_cart_items(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(product_db, id=product_id)
    try:
        cart_items = cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_items.quantity > 1:
            cart_items.quantity -= 1
            cart_items.save()
        else:
            cart_items.delete()
    except:
        pass
    return redirect('carts')


def remove_cart(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(product_db, id=product_id)
    cart_items = cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_items.delete()
    return redirect('carts')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products=product_db.objects.order_by('-created_date').filter(Q(Description__icontains=keyword) | Q(product_name__icontains = keyword))
            product_count = products.count()
    context={
        'products': products,
        'product_count': product_count,
    }
    return render(request, "store/store.html",context)
