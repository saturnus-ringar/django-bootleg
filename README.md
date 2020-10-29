# django-bootleg
Django additions, tools and ...stuff...

## Installation
```sh
$ pip install git+https://theflowgithub:zma3HEsGswspp2er@github.com/saturnus-ringar/django-bootleg.git
```

## Configure

```python
# settings.py

INSTALLED_APPS = (
    # ...
    'compressor',
    'crispy_forms',
    'django_extensions',
    'django_js_reverse',
    'django_user_agents',
    'django_tables2',
    'bootleg',
)

MIDDLEWARE = [
    # ...
    'bootleg.middleware.LoggingMiddleware',
    'bootleg.middleware.LoginMiddleware',
]

TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'bootleg.context_processors.globals',
            ],
        },
    },
]

BASE_TEMPLATE = "<template_path/name>.html"

AUTHENTICATION_BACKENDS = ('bootleg.backends.EmailOrUsernameModelBackend',)

# must be the last line in settings.py
from bootleg.settings import *
```

```python
# urls.py

urlpatterns = [
    # ...
    path('', include('bootleg.urls')),
]

# must be the last line in urls.py
from bootleg.setup import *
```

## Settings

### Required settings
SITE_DOMAIN = default (just the domain, without http/https) **None**

SITE_NAME = default **None**

NAVIGATION_TEMPLATE - default **None** 

HOME_URL = default **None**
> Just a string. The string will be reverse():ed

### Logging
DJANGO_LOG_LEVEL - default **"ERROR"**

LOG_DIR - default **"/dev/null"**

LOG_DATE_FORMAT - default **"%Y-%m-%d %H:%M:%S"**

LOG_SQL - default **False**

LOG_TO_STDOUT - default **True**

### Errors/exceptions
STORE_LOGGED_EXCEPTIONS - default **True**

STORE_DJANGO_LOG_EXCEPTIONS - default **True** if **DEBUG** is **False** - else **False** 

### Templates/HTML/CSS
BASE_TEMPLATE - default **None**

CONTAINER_CSS_CLASS - default **"container-fluid bg-dark"**

CSS_FILE = default **"bootleg/css/bootstrap.css"**

FAVICON_FILE = default **"bootleg/img/favicon.ico"**

ERROR_400_TEMPLATE - default **"bootleg/errors/400.html"**

ERROR_400_TEMPLATE - default **"bootleg/errors/400.html"**

ERROR_403_TEMPLATE - default **"bootleg/errors/403.html"**

ERROR_404_TEMPLATE - default **"bootleg/errors/404.html"**

ERROR_500_TEMPLATE - default **"bootleg/errors/500.html"**

### Misc-ish
POST_LOGIN_URL = default **reverse("dev_null")**

SITE_ID = default **1**

GOOGLE_ANALYTICS_ACCOUNT - default **None**

ADD_BULITINS - default **False**
> Adds dx and dxv-functions for debug-logging

PRINT_AT_STARTUP - default **True**
