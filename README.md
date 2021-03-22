
# Ecommerce

## Installation
First one you should create virtual environment in project <br/>

### Install requirements
You should install requirements. For this you need "freeze" module. 
For installing requirements use this command in terminal:
```Bash
python -m pip install -r requirements.txt
```

### Install ckeditor
In shop/settings.py find this lines and comment it <br/>
```Python
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
```

- Step 1 <br/>
  Uncomment this line
```Python
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

- Step 2 <br/>
End change DEBUG=True To False
```Python
DEBUG=False
```

- Step 3 <br/>
After that make this command in terminal
```Bash
python manage.py collectstatic
```

When terminal ask you that "Are you sure want to do this?" Enter command:
```Bash
yes
```

After this make all steps in reverse beginning from step 2

### Create DB
When ckeditor was installed, now you should create DB. <br/>
For that make this commands:
```Bash
python manage.py makemigrations
python manage.py migrate
```

### Create superuser
After all steps you should create admin for web resource using this command:
```Bash
python manage.py createsuperuser
```

## Goals

Pages:
- [x] Main page
- [x] Product categories
- [x] Product detail
- [x] Profile
- [x] Cart
- [ ] Payment and delivery
- [x] Useful topics
- [ ] Faq
- [x] Sales
- [x] About

Features:
- [x] Search products
- [ ] Sales system
- [x] Sales and income in period
- [x] Admin notification
- [ ] Акции


## Extensions used

- [Pillow](https://github.com/python-pillow/Pillow)
- [Bootstrap](https://github.com/twbs/bootstrap)
- [Crispy forms](https://github.com/django-crispy-forms/django-crispy-forms)
- [Allauth](https://github.com/pennersr/django-allauth)
- [Django extensions](https://github.com/django-extensions/django-extensions)
- [Ckeditor](https://github.com/django-ckeditor/django-ckeditor)
- [Google icons](https://fonts.google.com/icons)
- [otSlider](https://github.com/iniohd/otslider)
- [Splide](https://github.com/Splidejs/splide)
- [Django 3 jet](https://github.com/geex-arts/django-jet)
- [Django debug toolbar](https://github.com/geex-arts/django-jet)
