from core.models import Category
from core.utils import get_active_customer_cart


def get_cart_total_products(request):
    return {
        'total_products': get_active_customer_cart(request).total_products
    }


def get_categories(request):
    return {
        'categories': Category.objects.get_categories_for_navbar()
    }
