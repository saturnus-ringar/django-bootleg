# django-bootleg™©℗®
Django additions, tools and ...stuff...

## Features
- It adds django debug toolbar - https://github.com/jazzband/django-debug-toolbar

... todo ...


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
    'debug_toolbar',
    'django_extensions',
    'django_user_agents',
    'django_tables2',
    'bootleg',
)

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # optional - if you want access-logging
    'bootleg.middleware.LoggingMiddleware',
    # optional - if you want to use the login-restriction bits
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

BASE_TEMPLATE = 'path/name.html'

AUTHENTICATION_BACKENDS = ('bootleg.backends.EmailOrUsernameModelBackend',)

```

```python
# urls.py

from bootleg.init import *

urlpatterns = [
    # ...
    path('', include('bootleg.urls')),
    path('', include('bootleg.urls_apps')),
]
```

### Include javascript in your template (if you're not extending bootleg/base.html) - jquery is required
```python
{% compress js %}
# ...
<script src="{% static 'bootleg/js/main.js' %}"></script>
{% endcompress %}
```

## Django settings

MEDIA_ROOT

MEDIA_ROOT
> If these settings are set and DEBUG is True this will be added to urlpatterns in urls.py

## Basic settings

### Required settings
SITE_DOMAIN = default **None**
> just the domain, without http/https

SITE_NAME = default **None**
> Just a name. It's not used in URLs.

HOME_URL = default **None**
> The home/index URL of the site. Just a string. The string will be URL-reverse():ed

### Logging
LOG_DIR - default **'/dev/null'**
> Example: '/var/log/django-bootleg/'

## Reversing URLs
Get the URL to the System info page

```python
{% url "bootleg:system_info" %}

```
Get the URL to the Deployment page

```python
{% url "bootleg:deploy_info" %}

```

## Templates/Template settings

BASE_TEMPLATE - default **None**
> Example: 'website/base.html'

ADMIN_TEMPLATE - default **BASE_TEMPLATE**
> Example: 'webiste_admin/base.html' - if this isn't set the VALUE from BASE_TEMPLATE will be used

**The templates need a content block to be able to render to bootleg-HTML. 
So add this block to your templates:**

```python
{% block content %}
{# bootleg content will be rendered here #}
{% endblock %}
```

SYSTEM_TEMPLATE - default **'bootleg/system_info.html'**
> Example: 'website/system/system_info.html'

> Link to system info: <a href="{% url "bootleg:system_info" %}">{% trans "System" %}</a>

> ...and an example on what the template could look like:
```python
{% extends 'website/base.html' %}
{% block content %}
<h1>{% trans 'System information' %}</h1>
<p>
    {% trans 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. ... up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage...
</p>

{# render system information #}
{% render_system_information %}

{% endblock %}
```

DEPLOYMENT_TEMPLATE - default **'bootleg/system/deployment.html'**
> Example: 'website/system/deployment.html'

> Link to deployment info: <a href="{% url "bootleg:deploy_info" %}">{% trans "Deployment" %}</a>

> ...and an example on what the template could look like:
```python
{% extends 'website/base.html' %}
{% block content %}
<h1>{% trans 'Deployment' %}</h1>
<p>
    {% trans 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. ... up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage...
</p>

{# render deploy information #}
{% render_deploy_info %}

{% endblock %}
```

NAVIGATION_TEMPLATE - default **None** 
> Example: 'website/includes/navigation.html'

> ...and an example on what the template could look like:

```python
{% load i18n static bootleg %}
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
    <a class="navbar-brand" href="/"><img src="{% static 'website/img/logo.png' %}" /></a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar" aria-controls="navbar" aria-expanded="false" aria-label={% trans "Toggle navigation" %}>
        <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbar">
        <ul class="navbar-nav">
            {% if not user.is_authenticated %}
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'login' %}">{% trans "Login" %}</a>
                </li>
            {% endif %}

            {% if user.is_staff %}
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'bootleg:system' %}">{% trans "System info" %}</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'bootleg:deploy_status' %}">{% trans "Deploy status" %}</a>
                </li>
            {% endif %}
        </ul>
        
        {# bootleg navigation #}
        {% render_navigation request %}

</div>
</nav>
```

ERROR_400_TEMPLATE - default **'bootleg/errors/400.html'**
> Example: 'website/errors/404.html'

ERROR_400_TEMPLATE - default **'bootleg/errors/400.html'**
> Example: 'website/errors/400.html'

ERROR_403_TEMPLATE - default **'bootleg/errors/403.html'**
> Example: 'website/errors/403.html'

ERROR_404_TEMPLATE - default **'bootleg/errors/404.html'**
> Example: 'website/errors/404.html'

ERROR_500_TEMPLATE - default **'bootleg/errors/500.html'**
> Example: 'website/errors/500.html'


## More settings

### Logging
DJANGO_LOG_LEVEL - default **'ERROR'** if DEBUG is False - **'INFO'** if DEBUG is True
> Valid levels: 'DEBUG', 'INFO', 'ERROR'

LOG_DATE_FORMAT - default **'%Y-%m-%d %H:%M:%S'**

LOG_SQL - default **False**
> booean True/False

LOG_TO_STDOUT - default **True**
> booean True/False

### CSS

CONTAINER_CSS_CLASS - default **'container-fluid bg-dark'**
> Example: 'container'

CSS_FILE = default **'bootleg/css/bootstrap.css'**
> Example: 'website/css/style.css'

FAVICON_FILE = default **'bootleg/img/favicon.ico'**
> Example: 'website/img/favicon.png'

### Errors/exceptions
STORE_LOGGED_EXCEPTIONS - default **True**
> booean True/False

STORE_DJANGO_LOG_EXCEPTIONS - default **True** if **DEBUG** is **False** - else **False** 
> booean True/False


### Misc-ish
POST_LOGIN_URL = default **reverse('dev_null')**
> Just a string. The string will be URL-reverse():ed

SITE_ID = default **1**
> An integer for the site ID

GOOGLE_ANALYTICS_ACCOUNT - default **None**
> Example: 'UA-10876-1'

ADD_BULITINS - default **False**
> booean True/False
> Adds dx, dp and dxv-functions for debug-logging

PRINT_AT_STARTUP - default **True**
> booean True/False
> Prints settings etc. at startup if True



## Add custom settings that will be printed at startup

```python
# settings.py

SETTINGS_TO_PRINT = {
    "CUSTOM_SETTING": CUSTOM_SETTING,
    "CUSTOM_SETTING_ONCE_AGAIN": "This will be printed"
}
```
