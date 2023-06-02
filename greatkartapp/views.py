from django.contrib import messages, auth
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse

from greatkartapp.models import product_db, category_db, Cart, cart_item, Variation, Account
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from greatkartapp.forms import RegistraionForm
from django.contrib.auth.decorators import login_required

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

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


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(product_db, id=product_id)
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
            current_site=get_current_site(request)
            mail_subject='Please activate your Email'
            message=render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),

            })
            to_email=email
            send_email=EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it')
            return redirect('/accounts/login/?command=verification&email='+email)
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
            auth.login(request, user)
            # messages.success(request,'You are now logged in')
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
        user.is_active=True
        user.save()
        messages.success(request,'Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')


def dashboard(request):
    return render(request,'accounts/dashboard.html')



def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__iexact=email)

            # user reset password via email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,"Password reset mail has been send to your email.")
            return redirect(login)
        else:
            messages.error(request,"Account does not exist")
            return redirect(forgotPassword)
    return render(request,'accounts/forgot_password.html')

def resetpassword(request):
    if request.method == "POST":
        password =request.POST['password']
        confirm_password =request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset sucessful.')
            return redirect(login)


        else:
            messages.error(request,'Password does not match.')
            return redirect(resetpassword)
    else:
        return render(request,'accounts/reset_password.html')


def resetpassword_validate(request,  uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect(resetpassword)

    else:
        messages.error(request,'This link has been expired.')
        return redirect(login)