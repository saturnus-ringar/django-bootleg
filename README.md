# django-bootleg
Django additions, tools and ...stuff...

## Installation
```sh
$ git+https://saturnus-ringar-bot:5yXMrbdefJfB5Rgu@github.com/saturnus-ringar/django-bootleg.git
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
SITE_DOMAIN = default **None**
> just the domain, without http/https

SITE_NAME = default **None**
> Just a name. It's not used in URLs.

NAVIGATION_TEMPLATE - default **None** 
> Example: "website/includes/navigation.html"

HOME_URL = default **None**
> Just a string. The string will be URL-reverse():ed

### Logging
DJANGO_LOG_LEVEL - default **"ERROR"**
> Valid levels: "DEBUG", "INFO", "ERROR"

LOG_DIR - default **"/dev/null"**
> Example: "/var/log/django-bootleg/"

LOG_DATE_FORMAT - default **"%Y-%m-%d %H:%M:%S"**

LOG_SQL - default **False**
> booean True/False

LOG_TO_STDOUT - default **True**
> booean True/False

### Errors/exceptions
STORE_LOGGED_EXCEPTIONS - default **True**
> booean True/False

STORE_DJANGO_LOG_EXCEPTIONS - default **True** if **DEBUG** is **False** - else **False** 
> booean True/False

### Templates/HTML/CSS
BASE_TEMPLATE - default **None**
> Example: "website/base.html"

CONTAINER_CSS_CLASS - default **"container-fluid bg-dark"**
> Example: "container"

CSS_FILE = default **"bootleg/css/bootstrap.css"**
> Example: "website/css/style.css"

FAVICON_FILE = default **"bootleg/img/favicon.ico"**
> Example: "website/img/favicon.png"

ERROR_400_TEMPLATE - default **"bootleg/errors/400.html"**
> Example: "website/errors/404.html"

ERROR_400_TEMPLATE - default **"bootleg/errors/400.html"**
> Example: "website/errors/400.html"

ERROR_403_TEMPLATE - default **"bootleg/errors/403.html"**
> Example: "website/errors/403.html"

ERROR_404_TEMPLATE - default **"bootleg/errors/404.html"**
> Example: "website/errors/404.html"

ERROR_500_TEMPLATE - default **"bootleg/errors/500.html"**
> Example: "website/errors/500.html"

### Misc-ish
POST_LOGIN_URL = default **reverse("dev_null")**
> Just a string. The string will be URL-reverse():ed

SITE_ID = default **1**
> An integer for the site ID

GOOGLE_ANALYTICS_ACCOUNT - default **None**
> Example: "UA-10876-1"

ADD_BULITINS - default **False**
> booean True/False
> Adds dx, dp and dxv-functions for debug-logging

PRINT_AT_STARTUP - default **True**
> booean True/False
> Prints settings etc. at startup if True
