from django.urls import path

from .views import (
    base_view,
    product_detail_view,
    categories_view,
    category_detail_view,
    about_view,
    search_view,
    product_discount_view,
    cart_view,
    add_to_cart_view,
    delete_from_cart_view,
    change_qty_cart_view,
    checkout_view,
    make_order_view,
    blog_view,
    blog_post_detail_view,
    profile_view,
)

urlpatterns = [
    # Navigation
    path('', base_view, name='base'),
    path('products/<str:category>/<str:slug>/', product_detail_view, name='product_detail'),
    path('categories/', categories_view, name='categories'),
    path('category/discount/', product_discount_view, name='product_discount'),
    path('category/<str:slug>/', category_detail_view, name='category_detail'),
    path('about/', about_view, name='about'),
    path('search/', search_view, name='search'),
    # Cart
    path('cart/', cart_view, name='cart'),
    path('add-to-cart/<str:category>/<str:slug>/', add_to_cart_view, name='add_to_cart'),
    path('remove-from-cart/<str:category>/<str:slug>/', delete_from_cart_view, name='delete_from_cart'),
    path('change-qty-cart/<str:category>/<str:slug>/', change_qty_cart_view, name='change_qty_cart'),
    # Orders
    path('checkout/', checkout_view, name='checkout'),
    path('make-order/', make_order_view, name='make_order'),
    # blog
    path('blog/', blog_view, name='blog'),
    path('blog/post/<int:id>', blog_post_detail_view, name='blog_detail'),
    # User
    path('profile/', profile_view, name='profile'),
]
