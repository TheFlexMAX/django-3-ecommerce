from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db.models import Avg, Count, Min, Sum
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.conf import settings
from django.contrib.auth.models import User

from .models import Category, Product, CartProduct, Customer, Cart, Attribute, AttributeValue, MainPost, ShippingAddress


def parse_filter_data(cleaned_data):
    """
    Собирает данные из формы фильтрации
    """
    parsed_data = {
        'brands': cleaned_data.get('brand'),
        'price_min': cleaned_data.get('price_min'),
        'price_max': cleaned_data.get('price_max'),
        'dynamic': []
    }
    for i, data in enumerate(cleaned_data):
        if i > 2:
            parsed_data['dynamic'].append({
                'key': data[data.find('_')+1:],
                'value': cleaned_data[data]
            })
    return parsed_data


def get_active_customer_cart(request):
    """ Получает корзину для текущего пользователя """
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        session_key = request.session._session_key
        cart = Cart.objects.filter(for_anonymous_user=True, session_key=session_key).first()
        if not cart:
            cart = Cart.objects.create(for_anonymous_user=True, session_key=session_key)
    return cart


def recalculate_cart(cart):
    """ Делает перерасчет суммарной стоимости заказа, а также кол-ва товара """
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Sum('qty'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    if cart_data.get('qty__sum'):
        cart.total_products = cart_data['qty__sum']
    else:
        cart.total_products = 0
    cart.save()


def controller_product_cart(request, category, slug, action):
    """ Осуществляет управление продуктами в корзине """
    category_obj = Category.objects.get(slug=category)
    product_obj = Product.objects.get(slug=slug)
    cart = get_active_customer_cart(request)
    if request.user.is_anonymous:
        cart_product, is_created = CartProduct.objects.get_or_create(
            session_key=request.session._session_key,
            cart=cart,
            product=product_obj
        )
    else:
        cart_product, is_created = CartProduct.objects.get_or_create(
            user=cart.owner,
            cart=cart,
            product=product_obj
        )
    if action == 'add':
        if is_created:
            cart.products.add(cart_product)
        recalculate_cart(cart)
    elif action == 'remove':
        cart.products.remove(cart_product)
        cart_product.delete()
        recalculate_cart(cart)
    elif action == 'change_qty':
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalculate_cart(cart)


def get_data_by_page(request, data):
    """
    Возвращает набор фиксированных данные по странице для переданного набора данных
    """
    paginator = Paginator(data, 1)
    page_num = request.GET.get('page', None)
    if page_num is None:
        page_num = request.GET.get('page', 1)

    try:
        data_on_page = paginator.page(page_num)
    except EmptyPage:
        data_on_page = paginator.page(1)
    return data_on_page


def products_by_filters(filter_form, category, category_products):
    cleaned_data = filter_form.cleaned_data

    parsed_data = parse_filter_data(cleaned_data)

    # Являются ли динамичекие поля (атрибуты) пустыми
    is_empty = True
    for data in parsed_data["dynamic"]:
        data_len = len(data['value'])
        if data_len != 0:
            is_empty = False

    if (not is_empty or (parsed_data['price_min'] is not None and parsed_data['price_max'] is not None) or
            len(parsed_data['brands']) != 0):

        # Отсев по брендам
        if parsed_data['brands'].count() != 0 and parsed_data['brands'] is not None:
            category_products = category_products.filter(brand__in=parsed_data['brands'])

        # Собираем новые данные для ответа и отображаем клиенту
        attributes_category = Attribute.objects.filter(use_in_filter=True, category=category)
        attributes_values_category = AttributeValue.objects.filter(attribute__in=attributes_category)

        filtered_attributes_values = AttributeValue.objects.none()
        for data in parsed_data['dynamic']:
            new_filtered_attributes_values = attributes_values_category.filter(id__in=data.get('value'))
            filtered_attributes_values = filtered_attributes_values | new_filtered_attributes_values

        filtered_products_by_attributes_values = Product.objects.none()
        for attr_value in filtered_attributes_values:
            new_filtered_products = category_products.filter(id=attr_value.product.id)
            filtered_products_by_attributes_values = filtered_products_by_attributes_values | new_filtered_products
        category_products = filtered_products_by_attributes_values

        # Отсев по цене
        if parsed_data['price_min'] is not None and parsed_data['price_max'] is not None:
            category_products = category_products.filter(price__range=(parsed_data['price_min'], parsed_data['price_max']))
            category_products = category_products | filtered_products_by_attributes_values
    return category_products


def get_products_for_main_page():
    return MainPost.objects.filter(is_active=True).order_by('-show_order')


def get_most_popular(qty):
    """
    Получает набор самых покупаемых товаров
    """
    cart_products = list(CartProduct.objects.values('product__id').all().annotate(Sum('qty')).order_by('qty__sum'))[:5]
    ids = [id['product__id'] for id in cart_products]
    cart_products = Product.objects.filter(id__in=ids)
    return cart_products


def create_new_shipping_address(request):
    """
    Создает новый адресс для заказа
    """
    customer = Customer.objects.get(user=request.user)

    shipping_address_form_set = modelformset_factory(
        ShippingAddress,
        fields=('address', 'city', 'region', 'zipcode'),
        extra=1
    )
    formset = shipping_address_form_set(request.POST or None)
    clean_data_formset = formset.cleaned_data[0]

    shipping_address = ShippingAddress.objects.filter(
        region=clean_data_formset['region'],
        city=clean_data_formset['city'],
        address=clean_data_formset['address'],
        customer=customer
    ).first()
    if not shipping_address:
        shipping_address = ShippingAddress.objects.create(
            region=clean_data_formset['region'],
            city=clean_data_formset['city'],
            address=clean_data_formset['address'],
            customer=customer
        )
        shipping_address.save()
    return shipping_address


def create_new_order(customer, form, cart, shipping_address):
    """
    Создает новый заказ
    """
    # Создаем новый заказ
    cleaned_data = form.cleaned_data

    new_order = form.save(commit=False)
    new_order.first_name = cleaned_data['first_name']
    new_order.last_name = cleaned_data['last_name']
    new_order.phone = cleaned_data['phone']
    new_order.cart = cart
    new_order.shipping_address = shipping_address
    new_order.comment = cleaned_data['comment']
    if cart.for_anonymous_user:
        new_order.customer = None
    else:
        new_order.customer = customer
    new_order.save()

    cart.in_order = True
    cart.save()

    return new_order


def get_active_staff_emails():
    """
    Получает указанную электронную почту для персонала
    """
    return User.objects.filter(is_staff=True, is_active=True).values_list('email')


def send_order_message(order):
    """
    Отправляет письма администраторам о получении нового заказа
    """

    order_data = {
        'id': order.id,
        'date': order.date_created,
        'first_name': order.first_name,
        'last_name': order.last_name,
        'email': '111@gmail.com',
        'phone': order.phone,
        'region': order.shipping_address.region,
        'city': order.shipping_address.city,
        'address': order.shipping_address.address,
        'zipcode': order.shipping_address.zipcode,
        'products': order.cart.products.all(),
        'final_price': order.cart.final_price
    }
    subject = f'Новый заказ #{order.id}'
    message = render_to_string('email/email_new_order_admin.html', order_data)

    connection = get_connection(
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        fail_silently=False
    )
    emails = []
    for staff_email in get_active_staff_emails():
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=staff_email
        )
        email.attach_alternative(message, "text/html")
        emails.append(email)
    connection.send_messages(emails)
