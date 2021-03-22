from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField

from allauth.account.forms import SignupForm

from .models import Order, ShippingAddress, Brand, Category, Product, Attribute, AttributeValue, Customer


class FilterModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class OrderForm(forms.ModelForm):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['date_order'].label = 'Дата получения заказа'
    #
    # date_order = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Номер тел.'}))
    comment = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Комментарий'}))

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'comment'
        )


class ShippingAddressForm(forms.ModelForm):

    class Meta:
        model = ShippingAddress
        fields = (
            'region', 'city', 'address', 'zipcode'
        )

    def __init__( self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__( *args, **kwargs)
        self.fields['address'].widget.attrs['placeholder'] = "Улица"
        self.fields['city'].widget.attrs['placeholder'] = "Город"
        self.fields['region'].widget.attrs['placeholder'] = "Область"
        self.fields['zipcode'].widget.attrs['placeholder'] = "Почтовый индекс"


class FilterProductsForm(forms.Form):
    """
    Форма для фильтрации товаров в определенной категории
    """
    brand = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.all(),
        required=False
    )
    brand.label = 'Бренд'
    price_min = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False
    )
    price_min.label = 'Цена минимальная'
    price_max = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False
    )
    price_max.label = 'Цена максимальная'

    def __init__(self, category_slug=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brands_of_product = Product.objects.filter(category__slug=category_slug).values('brand')
        self.fields['brand'].queryset = Brand.objects.filter(id__in=brands_of_product)
        attributes_category = Attribute.objects.filter(use_in_filter=True, category__slug=category_slug)

        for i, attribute in enumerate(attributes_category):
            self.fields[f'parameter_{attribute.slug}'] = FilterModelMultipleChoiceField(
                queryset=attribute.related_attributevalue.all(),
                required=False
            )
            self.fields[f'parameter_{attribute.slug}'].label = attribute.name


class UserSignupForm(SignupForm):
    """
    Расширение формы регистрации для пользователя
    """
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Номер телефона'})
    )
    first_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'})
    )

    # Put in custom signup logic
    def custom_signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        new_customer = Customer.objects.create(user=user)
        new_customer.phone = self.cleaned_data["phone"]
        new_customer.save()
        new_customer.user = user
        # Save the user's type to their database record
        user.save()
        return user
