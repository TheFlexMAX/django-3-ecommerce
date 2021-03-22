import json
from operator import attrgetter

from django.db import transaction
from django.db.models import Q
from django.forms import inlineformset_factory, modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from .models import (
    Product,
    ProductImages,
    Category,
    Attribute,
    AttributeValue,
    Customer,
    Cart,
    CartProduct,
    Order,
    ShippingAddress,
    Post
)
from .forms import OrderForm, FilterProductsForm, ShippingAddressForm
from .utils import (
    get_active_customer_cart,
    controller_product_cart,
    get_data_by_page,
    products_by_filters,
    get_products_for_main_page,
    get_most_popular,
    send_order_message,
    create_new_shipping_address,
    create_new_order
)


def base_view(request):
    """ Отправляет базовое представление (главную страницу) пользователю """
    session_key = request.session._session_key
    trend_products = get_products_for_main_page()
    popular_products = get_most_popular(5)
    context = {
        'trend_products': trend_products,
        'popular_products': popular_products
    }
    return render(request, 'base.html', context)


def product_detail_view(request, category, slug):
    """ Отправляет подробоную страницу описания товара """
    product = Product.objects.get(category__slug=category, slug=slug)
    product_images = None
    product_main_img = None
    product_attributes_unique = None
    product_attributes_category = None
    product_attributes_values_category = None
    if product:
        product_images = ProductImages.objects.filter(product=product)
        if product_images:
            product_main_img = product.get_main_img()
        category_obj = Category.objects.get(slug=category)
        if category_obj:
            product_attributes_category = Attribute.objects.filter(category=category_obj)
            product_attributes_values_category = AttributeValue.objects.filter(attribute__in=product_attributes_category)

    context = {
        'product': product,
        'product_main_img': product_main_img,
        'product_images': product_images[0:],
        'product_attributes_unique': product_attributes_unique,
        'product_attributes_category': product_attributes_category,
        'product_attributes_values_category': product_attributes_values_category,
    }
    return render(
        request,
        'shop/product_detail.html',
        context
    )


def categories_view(request):
    """ Отправляет страницу с набором категорий """
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(
        request,
        'shop/categories.html',
        context
    )


def category_detail_view(request, slug):
    """ Отправляет страницу товаров по категории """

    if request.method == 'POST':
        # формируем форме фильтрации товаров
        filter_form = FilterProductsForm(data=request.POST or None, category_slug=slug)

        category = Category.objects.get(slug=slug)
        category_products = Product.objects.filter(category=category).all()

        if filter_form.is_valid():
            category_products = products_by_filters(filter_form, category, category_products)
            category_products_on_page = get_data_by_page(request, category_products)
            context = {
                'category': category,
                'category_products': category_products_on_page,
                'filter_form': filter_form,
            }
            return render(
                request,
                'shop/category_detail.html',
                context
            )

        category_products_on_page = get_data_by_page(request, category_products)
        context = {
            'category': category_products_on_page['category'],
            'category_products': category_products_on_page['products'],
            'queryset': category_products_on_page['products'],
            'filter_form': filter_form,
        }
        return render(
            request,
            'shop/category_detail.html',
            context
        )

    elif request.method == 'GET':
        filter_form = FilterProductsForm(data=request.POST or None, category_slug=slug)

        category = Category.objects.get(slug=slug)
        category_products = Product.objects.filter(category=category).all()

        category_products_on_page = get_data_by_page(request, category_products)
        context = {
            'category': category,
            'category_products': category_products_on_page,
            'queryset': category_products_on_page,
            'filter_form': filter_form,
        }
        return render(
            request,
            'shop/category_detail.html',
            context
        )


def about_view(request):
    """
    Присылает страницу о нас
    """
    context = {}
    return render(request, 'shop/about.html', {})


def search_view(request):
    query = request.GET.get('search', None)
    if query:
        products = Product.objects.filter(Q(title__icontains=query) | Q(category__name__icontains=query)).order_by('-date_created')
        products_on_page = get_data_by_page(request, products)
        context = {
            'products': products_on_page,
            'queryset': products_on_page,
            'search': query
        }
        return render(request, 'shop/search.html', context)
    else:
        return HttpResponseRedirect('/')


def product_discount_view(request):
    """
    Отправляет страницу товаров со скидками
    """
    products = Product.objects.filter(discount_price__isnull=False)
    category_products_on_page = get_data_by_page(request, products)
    context = {
        'category_products': category_products_on_page,
        'queryset': category_products_on_page,
    }
    return render(request, 'shop/products_discount.html', context)


def cart_view(request):
    """ Отправляет страницу корзины товаров """
    cart = get_active_customer_cart(request)
    cart_products = cart.products.all()
    context = {
        'cart_products': cart_products,
        'cart': cart
    }
    return render(request, 'shop/cart.html', context)


def add_to_cart_view(request, category, slug):
    """ Добавляет товар в корзину пользователя """
    controller_product_cart(request, category, slug, 'add')
    messages.add_message(request, messages.INFO, 'Товар добавлен в корзину')
    return HttpResponseRedirect('/cart/')


def delete_from_cart_view(request, category, slug):
    """ Удаляет товар из корзины пользователя """
    controller_product_cart(request, category, slug, 'remove')
    messages.add_message(request, messages.INFO, 'Товар удален из корзины')
    return HttpResponseRedirect('/cart/')


@require_http_methods(["POST"])
def change_qty_cart_view(request, category, slug):
    """ Метод уменьшения количества заказанных товаров """
    controller_product_cart(request, category, slug, 'change_qty')
    messages.add_message(request, messages.INFO, 'Количество изменено')
    return HttpResponseRedirect('/cart/')


def checkout_view(request):
    """ Страница оформления заказа """
    customer = request.user
    cart = get_active_customer_cart(request)
    categories = Category.objects.get_categories_for_navbar()
    cart_products = cart.products.all()

    ShippingAddressFormSet = modelformset_factory(
        ShippingAddress,
        fields=('address', 'city', 'region', 'zipcode'),
        form=ShippingAddressForm,
        extra=0)
    formset = ShippingAddressFormSet(request.POST or None)
    form = OrderForm(request.POST or None)
    context = {
        'cart': cart,
        'categories': categories,
        'cart_products': cart_products,
        'form': form,
        'formset': formset
    }
    return render(request, 'shop/checkout.html', context)


@transaction.atomic
def make_order_view(request):
    """ Осуществляет подтверждение заказа от пользователя """
    cart = get_active_customer_cart(request)
    form = OrderForm(request.POST or None)
    customer = Customer.objects.get(user=request.user)

    if form.is_valid():
        shipping_address = create_new_shipping_address(request)
        new_order = create_new_order(customer, form, cart, shipping_address)
        customer.orders.add(new_order)
        # Отправляем письмо администраторам
        send_order_message(order=new_order)

        return HttpResponseRedirect('/')

    context = {
        'cart': cart,
        'form': form
    }
    return HttpResponseRedirect('/checkout/')


def blog_view(request):
    """
    Запрашивает блог
    """
    posts = Post.objects.all().order_by('-date_created')
    posts_on_page = get_data_by_page(request, posts)
    context = {
        'posts': posts_on_page,
        'queryset': posts_on_page,
    }
    return render(request, 'shop/blog.html', context)


def blog_post_detail_view(request, id):
    """
    Запрашивает пост блога
    """
    post = Post.objects.filter(id=id).first()
    context = {
        'post': post
    }
    return render(request, 'shop/blog_post.html', context)


def profile_view(request):
    if request.user.is_authenticated:
        cart = get_active_customer_cart(request)
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-date_created')
        context = {
            'orders': orders,
            'cart': cart
        }
        return render(request, 'shop/profile.html', context)
    else:
        return render(request, 'account/login.html', {})
