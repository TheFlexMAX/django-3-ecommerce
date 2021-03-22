from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.db.models import Count, Sum, DateTimeField, Min, Max, DateField
from django.db.models.functions import Trunc
from django.utils.safestring import mark_safe

from .models import *


from django.contrib import admin

from .models import (
    Category,
    Attribute,
    AttributeValue,
    Brand,
    ProductImages,
    Product,
    Customer,
    CartProduct,
    Cart,
    Specifications,
    ShippingAddress,
    Order,
    Faq,
    Post
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'name', 'slug', 'keywords')
    search_fields = ('name', 'slug')
    readonly_fields = ['image_tag']
    prepopulated_fields = {'slug': ['name']}

    def image_tag(self, obj):
        if obj.category_photo:
            return mark_safe('<img src="{url}" width="40" height=40 />'.format(url=obj.category_photo.url))

    image_tag.short_description = 'Фото'


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'description',
        'use_in_filter',
        'unit',
    )
    list_filter = ('category', 'use_in_filter')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ['name']}
    inlines = [AttributeValueInline]


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'name', 'description', 'product')
    list_filter = ('attribute', 'product')
    search_fields = ('name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand_description')
    search_fields = ('name',)


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'product', 'image', 'date_created')
    readonly_fields = ['image_tag']
    list_filter = ('product', 'date_created')

    def image_tag(self, obj):
        if obj.category_photo:
            return mark_safe('<img src="{url}" width="40" height=40 />'.format(url=obj.image.url))

    image_tag.short_description = 'Фото'


class ProductAdminForm(forms.ModelForm):
    """
    Форма редактирования товара для администратора
    """
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Product
        fields = '__all__'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    list_display = (
        'id',
        'image_tag',
        'category',
        'title',
        'slug',
        'description',
        'price',
        'discount_price',
        'brand',
        'is_active',
        'date_created',
        'date_updated',
        'expired_date',
        'keywords',
    )
    readonly_fields = ['image_tag']
    list_filter = (
        'category',
        'brand',
        'is_active',
        'date_created',
        'date_updated',
        'expired_date',
    )
    search_fields = ('title', 'category')
    prepopulated_fields = {'slug': ['title']}

    def image_tag(self, obj):
        if not obj.get_main_img() is None:
            return mark_safe('<img src="{url}" width="40" height=40 />'.format(url=obj.get_main_img().url))

    image_tag.short_description = 'Фото'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone')
    list_filter = ('user',)
    raw_id_fields = ('orders',)


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'
    if date_hierarchy + '__month' in request.GET:
        return 'day'
    if date_hierarchy + '__year' in request.GET:
        return 'week'
    return 'month'


@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    """
    Отображает графики о суммарных продажах
    """
    change_list_template = 'admin/order_summary_change_list.html'
    date_hierarchy = 'date_created'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'total': Count('cart__products__product__title'),
            'total_sales': Sum('cart__final_price'),
        }
        response.context_data['summary'] = list(
            qs
                .values('cart__products__product__title')
                .annotate(**metrics)
                .order_by('-total_sales')
        )
        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period

        summary_over_time = qs.annotate(
            period=Trunc('date_created', period, output_field=DateTimeField()),
        ).values('period').annotate(total=Sum('cart__final_price')).order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)
        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'pct': ((x['total'] or 0) - low) / (high - low) * 100
            if high > low else 0,
        } for x in summary_over_time]

        return response


@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'image_tag',
        'user',
        'cart',
        'product',
        'qty',
        'final_price',
        'session_key',
    )
    readonly_fields = ['image_tag']
    list_filter = ('user', 'cart', 'product', 'final_price')

    def image_tag(self, obj):
        if obj.category_photo:
            return mark_safe('<img src="{url}" width="40" height=40 />'.format(url=obj.get_main_img().url))

    image_tag.short_description = 'Фото'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'total_products',
        'final_price',
        'date_created',
        'in_order',
        'for_anonymous_user',
        'session_key',
    )
    list_filter = ('owner', 'date_created', 'in_order', 'for_anonymous_user')
    raw_id_fields = ('products',)


@admin.register(Specifications)
class SpecificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'name')
    list_filter = ('content_type',)
    search_fields = ('name',)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'region',
        'city',
        'address',
        'zipcode',
        'date_added',
    )
    list_filter = ('customer', 'date_added')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'first_name',
        'last_name',
        'phone',
        'cart',
        'shipping_address',
        'status',
        'comment',
        'date_created',
        'date_order',
    )
    list_filter = (
        'customer',
        'cart',
        'shipping_address',
        'date_created',
        'date_order',
    )


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')


class PostAdminForm(forms.ModelForm):
    """
    Форма редактирования поста блога для администратора
    """
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Post
        fields = '__all__'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

    list_display = (
        'id',
        'title',
        'date_created',
        'content',
        'preview_content',
        'preview_img',
    )
    list_filter = ('date_created',)


@admin.register(MainPost)
class MainPostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'content',
        'banner_img',
        'show_order',
        'date_created',
        'is_active',
    )
    list_filter = ('product', 'date_created', 'is_active')


admin.site.site_header = 'Интернет-магазин'
admin.site.site_title = 'Интернет-магазин'
