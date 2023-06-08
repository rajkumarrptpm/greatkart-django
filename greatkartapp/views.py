from django.contrib import messages, auth
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from greatkartapp.models import product_db, category_db, Cart, cart_item, Variation, Account, Order, Payment,OrderProduct,ReviewRating
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from greatkartapp.forms import RegistraionForm, OrderForm,ReviewForm
from django.contrib.auth.decorators import login_required

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import datetime,json

import requests


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
        in_cart=cart_item.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()

        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct = None

    # get the reviews
    reviews=ReviewRating.objects.filter(product_id=single_product.id,status=True)

    context = {
        'single_product': single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
    }
    return render(request, 'store/product_details.html', context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = product_db.objects.get(id=product_id)  # get the product
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = cart_item.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            Cart_item = cart_item.objects.filter(product=product, user=current_user)

            exi_var_list = []
            id = []
            for item in Cart_item:
                existing_variation = item.variations.all()
                exi_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in exi_var_list:
                # Increase the cart item quantity
                index = exi_var_list.index(product_variation)
                item_id = id[index]
                item = cart_item.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                # create new cart item
                Cart_items = cart_item.objects.create(product=product, quantity=1, user=current_user)

                if len(product_variation) > 0:
                    Cart_items.variations.clear()
                    Cart_items.variations.add(*product_variation)
                Cart_items.save()
        else:
            Cart_item = cart_item.objects.create(
                product=product,
                quantity=1,
                user=current_user,

            )
            if len(product_variation) > 0:
                Cart_item.variations.clear()
                Cart_item.variations.add(*product_variation)
            Cart_item.save()
        return redirect(carts)
    else:
        product_variation = []

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
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

        is_cart_item_exists = cart_item.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            Cart_item = cart_item.objects.filter(product=product, cart=cart)
            # 1.existing variation -> database
            # 2.current variation -> product_variation
            # 3.current_id
            exi_var_list = []
            id = []
            for item in Cart_item:
                existing_variation = item.variations.all()
                exi_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in exi_var_list:
                # Increase the cart item quantity
                index = exi_var_list.index(product_variation)
                item_id = id[index]
                item = cart_item.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                # create new cart item
                Cart_items = cart_item.objects.create(product=product, quantity=1, cart=cart)

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
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = cart_item.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = cart_item.objects.filter(cart=cart, is_active=True)
        for crt_itm in cart_items:
            total += (crt_itm.product.price * crt_itm.quantity)
            quantity += crt_itm.quantity
        tax = (9 * total) / 100
        grand_total = total + tax
        grand_total = round(grand_total, 2)
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


def remove_cart_items(request, product_id, cart_item_id):
    product = get_object_or_404(product_db, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_items = cart_item.objects.get(product=product, user=request.user, id=cart_item_id)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_items.quantity > 1:
            cart_items.quantity -= 1
            cart_items.save()
        else:
            cart_items.delete()
    except:
        pass
    return redirect('carts')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(product_db, id=product_id)
    if request.user.is_authenticated:
        cart_items = cart_item.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_items.delete()
    return redirect('carts')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product_db.objects.order_by('-created_date').filter(
                Q(Description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, "store/store.html", context)


def register(request):
    if request.method == "POST":
        form = RegistraionForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               phone_number=phone_number, username=username, password=password)
            user.save()

            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your Email'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it')
            return redirect('/accounts/login/?command=verification&email=' + email)


    else:
        form = RegistraionForm()
    context = {
        'form': form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = cart_item.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    Cart_item = cart_item.objects.filter(cart=cart)

                    # Getting the product variation by cart id
                    product_variation = []
                    for item in Cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #     get the cart item from the user to access his product variation
                    Cart_item = cart_item.objects.filter(user=user)
                    exi_var_list = []
                    id = []
                    for item in Cart_item:
                        existing_variation = item.variations.all()
                        exi_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation=[1,2,3,4,5,6,]
                    # exi_var_list=[5,3,2,8]
                    # first check and take common values in product_variation and exi_var_list
                    for prdt in product_variation:
                        if prdt in exi_var_list:
                            index = exi_var_list.index(prdt)
                            item_id = id[index]
                            item = cart_item.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            Cart_item = cart_item.objects.filter(cart=cart)
                            for item in Cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect(home)
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect(login)

    return render(request, "accounts/login.html")


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful")
    return redirect(login)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            # user reset password via email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Password reset mail has been send to your email.")
            return redirect(login)
        else:
            messages.error(request, "Account does not exist")
            return redirect(forgotPassword)
    return render(request, 'accounts/forgot_password.html')


def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset sucessful.')
            return redirect(login)


        else:
            messages.error(request, 'Password does not match.')
            return redirect(resetpassword)
    else:
        return render(request, 'accounts/reset_password.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect(resetpassword)

    else:
        messages.error(request, 'This link has been expired.')
        return redirect(login)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = cart_item.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = cart_item.objects.filter(cart=cart, is_active=True)
        for crt_itm in cart_items:
            total += (crt_itm.product.price * crt_itm.quantity)
            quantity += crt_itm.quantity
        tax = (9 * total) / 100
        grand_total = total + tax
        grand_total = round(grand_total, 2)
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)


def place_order(request, total=0, quantity=0):
    current_user = request.user

    # if the cart count is less than or equal to zero,then redirect back to shop
    cart_items = cart_item.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect(store)

    tax = 0
    grand_total = 0
    for items in cart_items:
        total += (items.product.price * items.quantity)
        quantity += items.quantity
    tax = (9 * total) / 100
    grand_total = total + tax
    grand_total = round(grand_total, 2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside the order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.street = form.cleaned_data['street']
            data.district = form.cleaned_data['district']
            data.postal_code = form.cleaned_data['postal_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #         generate order number

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_Number = order_number
            data.save()
            order =Order.objects.get(user=current_user,is_ordered=False,order_Number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total': total,
                'grand_total': grand_total,
                'tax': tax,
            }
            return render(request,'order/payments.html',context)
        else:
            return redirect(place_order)
    else:
        return redirect(checkout)


def payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user,order_Number=body['orderID'])
    # store transation details in payment model
    payment=Payment(
        user = request.user,
        payment_id=body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status=body['status']
    )
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()

    # Move the cart items to product table
    cart_items=cart_item.objects.filter(user=request.user)
    for items in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=items.product_id
        orderproduct.quantity=items.quantity
        orderproduct.product_price=items.product.price
        orderproduct.ordered=True

        orderproduct.save()

        Cart_items=cart_item.objects.get(id=items.id)

        product_variation=Cart_items.variations.all()
        orderproduct=OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


    # reduce the quantity of sold products

        product=product_db.objects.get(id=items.product_id)
        product.stock-=items.quantity
        product.save()



    # clear the cart
    cart_item.objects.filter(user=request.user).delete()



    # Send the order recieved mail to customer
    mail_subject = 'Thank you for Shopping with us'
    message = render_to_string('order/order_recieved_email.html', {
        'user': request.user,
        'order':order,


    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()



    # send order number and transaction id back to sendData method via json response
    data={
        'order_number': order.order_Number,
        'transID' : payment.payment_id

    }
    return JsonResponse(data)







def order_completed(request):
    order_number= request.GET.get('order_number')
    transID= request.GET.get('payment_id')
    try:
        order=Order.objects.get(order_Number=order_number,is_ordered=True)
        ordered_products=OrderProduct.objects.filter(order_id=order.id)

        sub_total=0

        for i in ordered_products:
            sub_total= i.product_price * i.quantity


        payment=Payment.objects.get(payment_id=transID)
        context={
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_Number,
            'transID':payment.payment_id,
            'payment':payment,
            'sub_total':sub_total,
        }
        return render(request,'order/order_completed.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect(home)


def submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER')
    if request.method=="POST":
        try:
            review=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,"Thank you! Your review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
                return redirect(url)

