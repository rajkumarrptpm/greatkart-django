from greatkartapp.models import category_db

def menu_links(request):
    links=category_db.objects.all()
    return dict(links=links)