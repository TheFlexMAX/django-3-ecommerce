from django.db import models


class ProductManager(models.Manager):
    def get_products_for_main_page(self):
        return self.all().order_by('-id')[:10]

    def most_popular(self):
        return self.all().order_by('-id')[:5]

    def get_attributes(self):
        return AttributeValue.objects.filter(category=self.category)


class CategoryManager(models.Manager):
    def get_categories_for_navbar(self):
        return self.all()
