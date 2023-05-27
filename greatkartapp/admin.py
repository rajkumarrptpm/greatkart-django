from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import category_db, Account,product_db,Cart,cart_item


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


admin.site.register(category_db, CategoryAdmin)


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)


# Register products to admin

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','updated_date','is_available')
    prepopulated_fields = {'slug':('product_name',)}

admin.site.register(product_db,ProductAdmin)




admin.site.register(Cart)
admin.site.register(cart_item)
