from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

from .managers import *

User = get_user_model()


class Category(models.Model):
    """ Модель продаваемых категорий товаров """
    name = models.CharField(
        max_length=255,
        verbose_name='Имя категории'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True
    )
    keywords = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name='Набор ключевых слов для внутренней поисковой системы'
    )
    category_photo = models.ImageField(
        null=True,
        blank=True,
        verbose_name='Фотография для категории'
    )
    objects = CategoryManager()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Attribute(models.Model):
    """ Модель шаблонов характеристик товаров """
    name = models.CharField(
        max_length=1024,
        verbose_name='Наименование атрибута'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name='Категория'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    use_in_filter = models.BooleanField(
        default=False,
        verbose_name='Использование характеристики для фильтра'
    )
    unit = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Единица измерения',
    )
    slug = models.SlugField(
        max_length=255
    )

    class Meta:
        unique_together = ('category', 'name',)
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'

    def __str__(self):
        return f"{self.category.name} | {self.name}"
    #TODO: сделать сортировку поумолчанию


class AttributeValue(models.Model):
    """
    Модель значений параметров для товаров
    """
    attribute = models.ForeignKey(
        Attribute,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='related_attributevalue',
        verbose_name='Атрибут'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Значение атрибута'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание значения'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='related_attributevalue',
        verbose_name='Продукт'
    )

    class Meta:
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибутов'

    def __str__(self):
        return f'{self.attribute} | {self.name}'
    #TODO: сделать сортировку поумолчанию


class Brand(models.Model):
    """ Модель производителей для товаров """
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование'
    )
    brand_description = models.TextField(
        verbose_name='Описание бренда'
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name


class ProductImages(models.Model):
    """ Модель изображений для товаров """
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    image = models.ImageField(
        verbose_name='Изображение'
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return str(self.image)


class Product(models.Model):
    """ Модель продаваемых товаров """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='related_products',
        verbose_name='Категория'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Наименование'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name='Цена'
    )
    discount_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Цена со скидкой'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Имя бренда',
        default=None,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='В продаже'
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата добавления'
    )
    date_updated = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата обновления'
    )
    expired_date = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name='Ограниченное предложение'
    )
    keywords = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name='Набор ключевых слов для внутренней поисковой системы'
    )
    objects = ProductManager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'category': self.category.slug, 'slug': self.slug})

    def get_main_img(self):
        pi = ProductImages.objects.filter(product=self).order_by('id').first()
        if pi is not None:
            return pi.image
        return pi


class Customer(models.Model):
    """ Модель покупателей товаров """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='customer',
        unique=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Номер',
        null=True,
        blank=True
    )
    orders = models.ManyToManyField(
        'Order',
        related_name='related_customer',
        verbose_name='Заказы покупателя',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return f'Покупатель {self.user.first_name} {self.user.last_name}'


class CartProduct(models.Model):
    """ Модель товаров для корзины """
    user = models.ForeignKey(
        'Customer',
        verbose_name='Покупатель',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    cart = models.ForeignKey(
        'Cart',
        verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='related_products'
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE
    )
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name='Общая цена'
    )
    session_key = models.CharField(
        max_length=255,
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Товар корзины'
        verbose_name_plural = 'Товары корзин'

    def __str__(self):
        return f'Продукт: {self.product.title} (корзина)'

    def save(self, *args, **kwargs):
        if self.product.discount_price is not None:
            self.final_price = self.qty * self.product.discount_price
        else:
            self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    """ Модель корзины товаров """
    owner = models.ForeignKey(
        'Customer', verbose_name='Владелец',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    products = models.ManyToManyField(
        CartProduct,
        blank=True,
        related_name='related_cart'
    )
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(
        default=0,
        max_digits=9,
        decimal_places=2,
        verbose_name='Общая цена'
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата создания'
    )
    in_order = models.BooleanField(
        default=False,
        verbose_name='Находится в заказе'
    )
    for_anonymous_user = models.BooleanField(
        default=False,
        verbose_name='Для анонимного пользователя'
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {str(self.owner)}'


class Specifications(models.Model):
    """ Модель уникальных характеристик для товара """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255, verbose_name='Имя товара для карактеристик')

    class Meta:
        verbose_name = 'Спецификация'
        verbose_name_plural = 'Спецификации'

    def __str__(self):
        return f'Характеристики для товара {self.name}'


class ShippingAddress(models.Model):
    """ Модель адресов доставки """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    region = models.CharField(
        max_length=255,
        verbose_name='Область'
    )
    city = models.CharField(
        max_length=255,
        verbose_name='Город'
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес'
    )
    zipcode = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Почтовый индекс'
    )
    date_added = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f'{self.city} {self.address}'


class Order(models.Model):
    """ Модель заказа товаров """
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETE = 'complete'

    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_READY, 'ready'),
        (STATUS_COMPLETE, 'complete'),
    )

    customer = models.ForeignKey(
        Customer,
        related_name='related_orders',
        verbose_name='Покупатель',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя покупателя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия покупателя'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Номер телефона'
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name='Корзина'
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.CASCADE,
        verbose_name='Адрес доставки'
    )
    status = models.CharField(
        max_length=128,
        verbose_name='Статус заказа',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата заказа'
    )
    date_order = models.DateField(
        default=timezone.now,
        verbose_name='Дата получения заказа',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id} - Номер заказа'


class OrderSummary(Order):
    """
    Для подсчета суммарного количества продаж за периоді
    """
    class Meta:
        proxy = True
        verbose_name = 'Продажа суммарно'
        verbose_name_plural = 'Продажи суммарно'


class Faq(models.Model):
    """
    Записи используемые для отображения на странице частых вопросов
    """
    question = models.CharField(
        max_length=255,
        verbose_name='Вопрос'
    )
    answer = models.CharField(
        max_length=2048,
        verbose_name='Ответ'
    )

    class Meta:
        verbose_name = 'Вопрос - ответ'
        verbose_name_plural = 'Вопросы - ответы'

    def __str__(self):
        return self.question


class Post(models.Model):
    """ Запись для блога """
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата создания'
    )
    content = models.TextField(
        max_length=10000,
        verbose_name='Содержание записи'
    )
    preview_content = models.TextField(
        default=None,
        null=True,
        blank=True,
        verbose_name='Краткое содержание'
    )
    preview_img = models.ImageField(
        verbose_name='Изображение для предпросмотра',
        null=True,
        default=True
    )

    class Meta:
        verbose_name = 'Запись блога'
        verbose_name_plural = 'Записи блога'

    def __str__(self):
        return f'{self.id} | {self.title}'


class MainPost(models.Model):
    """
    Запись для главной страницы
    """
    product = models.ForeignKey(
        Product,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        verbose_name='Описываемый продукт'
    )
    content = models.TextField(
        max_length=1000,
        verbose_name='Содержание записи'
    )
    banner_img = models.ImageField(
        null=False,
        blank=False,
        verbose_name='Изображение'
    )
    show_order = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name='Очередность отображения записи среди других'
    )
    date_created = models.DateTimeField(
        default=timezone.now(),
        verbose_name='Дата создания'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Отображать на странице'
    )

    class Meta:
        verbose_name = 'Запись на главной'
        verbose_name_plural = 'Записи на главной'

    def __str__(self):
        return f'{self.show_order} | {self.content.title}'

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'id': self.id})
