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
    'django_user_agents.middleware.UserAgentMiddleware',
    # optional - if you want access-logging
    'bootleg.middleware.logging.LoggingMiddleware',
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

AUTHENTICATION_BACKENDS = ('bootleg.backends.EmailOrUsernameModelBackend',)

# just the domain, without http/https
SITE_DOMAIN = 'sitedomain.com'
# just a name for the site
SITE_NAME = 'site name'

# The home/index URL of the site. Just a string. The string will be URL-reverse():ed
HOME_URL = "<index_page>"

# templates
BASE_TEMPLATE = 'path/template.html'
NAVIGATION_TEMPLATE = 'path/navigation.html'
ERROR_400_TEMPLATE = 'path/400.html'
ERROR_403_TEMPLATE = 'path/403.html'
ERROR_404_TEMPLATE = 'path/404.html'
ERROR_500_TEMPLATE = 'path/500.html'


# log dir
LOG_DIR = '/var/log/project-name?/'

# should be the last line i settings.py
from bootleg.settings import *
```

```python
# urls.py
from bootleg.add_error_handlers import *

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
<script type="text/javascript" src="{% static 'bootleg/js/bootleg.js' %}"></script>
{% endcompress %}
```

## Django settings

MEDIA_ROOT

MEDIA_ROOT
> If these settings are set and DEBUG is True this will be added to urlpatterns in urls.py

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

SYSTEM_TEMPLATE - default **'bootleg/system/system.html'**
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

## More settings

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
