from greatkartapp.models import category_db,Cart,cart_item
from greatkartapp.views import _cart_id
def menu_links(request):
    links=category_db.objects.all()
    return dict(links=links)

def counter(request):
    cart_count=0
    if 'admin' in request.path:
        return ()
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = cart_item.objects.all().filter(user=request.user)
            else:
                cart_items =cart_item.objects.all().filter(cart=cart[:1])
            for count in cart_items:
                cart_count+=count.quantity
        except Cart.DoesNotExist:
            cart_count=0
    return dict(cart_count=cart_count)


