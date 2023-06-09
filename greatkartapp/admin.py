from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
import admin_thumbnails
from .models import category_db, Account,product_db,Cart,cart_item,Variation,Payment,OrderProduct,Order,ReviewRating,UserProfile, ProductGallery


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

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model=ProductGallery
    extra=1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','updated_date','is_available')
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [ProductGalleryInline]

admin.site.register(product_db,ProductAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added')


admin.site.register(Cart,CartAdmin)



class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','user','cart','quantity','is_active')

admin.site.register(cart_item,CartItemAdmin)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')

admin.site.register(Variation,VariationAdmin)


class OrderPoductInline(admin.TabularInline):
    model=OrderProduct
    readonly_fields = ['product','payment','user','quantity','product_price','ordered']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_Number','full_name','phone','email','city','order_total','tax','status')
    list_filter = ('status','is_ordered')
    search_fields = ('order_Number','first_name','last_name','email',)
    list_per_page = 20
    inlines = [OrderPoductInline]


admin.site.register(Order,OrderAdmin)




admin.site.register(OrderProduct)


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="40" height="40"  style=" border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description='Profile Picture'
    list_display = ('thumbnail','user','city','state','country',)

admin.site.register(UserProfile,UserProfileAdmin)



admin.site.register(Payment)



admin.site.register(ReviewRating)



admin.site.register(ProductGallery)






