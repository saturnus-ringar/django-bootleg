# django-bootleg
Django additions, tools and ...stuff...

## Features
- It adds django debug toolbar - https://github.com/jazzband/django-debug-toolbar

... #todo ...


## Installation
```sh
$ pip install git+https://saturnus-ringar-bot:5yXMrbdefJfB5Rgu@github.com/saturnus-ringar/django-bootleg.git
```

## Configure

```python

# settings.py

INSTALLED_APPS = (
    # ...
    'django.contrib.sites',
    'django.contrib.humanize',
    'compressor',
    'crispy_forms',
    'debug_toolbar',
    'django_extensions',
    'django_user_agents',
    'django_tables2',
    'bootleg',
    # django admin - must be after bootleg (for template-overriding)
    'django.contrib.admin',

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

# a Django settings that's used
LOGIN_REDIRECT_URL = 'url-string-that-will-be-reversed'

# just the domain, without http/https
SITE_DOMAIN = 'sitedomain.com'
# just a name for the site
SITE_NAME = 'site name'

# The home/index URL of the site. Just a string. The string will be URL-reverse():ed
HOME_URL = "<index_page>"

# templates
BASE_TEMPLATE = 'path/template.html'
NAVIGATION_TEMPLATE = 'path/navigation.html'

# log dir
LOG_DIR = '/var/log/project-name?/'

# should be the last line in settings.py
from bootleg.settings import *
```

```python

# urls.py

from bootleg.add_error_handlers import *
from django.urls import include

urlpatterns = [
    # ...
    path('', include('bootleg.urls')),
    path('', include('bootleg.urls_apps')),
]
```

## Log errors in manage.py

```python

# manage.py

import logging

#...
try:
    execute_from_command_line(sys.argv)
except Exception:
    logging.getLogger("django").error('manage.py error: %s', ' '.join(sys.argv), exc_info=sys.exc_info())
```

### Include javascript in your template (if you're not extending bootleg/base.html) - jquery is required
```python
{% compress js %}
# ...
<script type="text/javascript" src="{% static 'bootleg/js/bootleg.js' %}"></script>
{% endcompress %}
```

## Django settings (optional)

MEDIA_ROOT - will default to "/media/" if it's not added to the settings

STATIC_ROOT - will default to "/static/" if it's not added to the settings

> If these settings are set and DEBUG is True this will be added to urlpatterns in urls.py

## An example of rendering bootleg (bootstrap) menu

> Use the tag render_navigation

```html
{% load static i18n bootleg %}

<nav class="navbar navbar-expand-md navbar-dark bg-primary fixed-top">
    <ul class="navbar-nav ml-auto">
        <li class="nav-item">
            <a class="nav-link" href="{% url 'index'">{% trans "Home" %}</a>
        </li>
        {% render_navigation request %}
    </ul>
</nav>
```

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

### CSS and images

CONTAINER_CSS_CLASS - default **'container-fluid bg-dark'**
> Example: 'container'

CSS_FILES = default **['bootleg/css/vendor/bootstrap.css']**
> Example, a list
> CSS_FILES = [
    'website/css/bootstrap.min.css',
    'website/css/style.css'
]

FAVICON_FILE = default **'bootleg/img/favicon.ico'**
> Example: 'website/img/favicon.png'

BRANDING_LOGO = default **None**
> Used in Django admin - Example: 'website/img/logo.png'


WRAP_FORMS = default **True**
> Will wrap the forms with bg-light

### Errors/exceptions
STORE_LOGGED_EXCEPTIONS - default **True**
> booean True/False

STORE_DJANGO_LOG_EXCEPTIONS - default **True** if **DEBUG** is **False** - else **False** 
> booean True/False

### Error templates
ERROR_400_TEMPLATE - default **"bootleg/error/400.html"**

ERROR_403_TEMPLATE - default **"bootleg/error/403.html"**

ERROR_404_TEMPLATE - default **"bootleg/error/404.html"**

ERROR_500_TEMPLATE - default **"bootleg/error/500.html"**

### Javascript
JS_DATE_FORMAT - default **"yyyy-MM-DD"**
JS_DATETIME_FORMAT - default **"yyyy-MM-DD hh:ss"**

### Misc-ish
POST_LOGIN_URL = default **reverse("dev_null")**
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

## User Profiles

To add properties to users, more or less, create a Profile-model that extends Profile. An example:

```python
from bootleg.db.models.profile import Profile

class Profile(Profile):
    customer = ForeignKey("Customer", blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Customer"))
```

And add the model to the PROFILE_MODEL-setting:

```python
# settings.py
PROFILE_MODEL = "core.UserProfile"
```

## Add custom settings that will be printed at startup

```python
# settings.py

SETTINGS_TO_PRINT = {
    "CUSTOM_SETTING": CUSTOM_SETTING,
    "CUSTOM_SETTING_ONCE_AGAIN": "This will be printed"
}
```

## Bash aliases
bootleg generates an <project_name>aliases.sh-file in the users home directory. Source that file in your .bashrc to use the aliases. The alias file is only created when manage.py is run. So in case you want to update/create the alias files, just run any manage.py command.

Use the PROJECT_ABBR-setting to prefix the aliases and, for development, set your local user account to MAIN_USER to generate the alias files.

PROJECT_ABBR - default **None**

```bash
# .bashrc

source /home/nbcab/aliases_<project_name>.sh

```

## Fix messed upp file permissions
```bash

sudo /home/<project_name>/env/bin/python3 manage.py setup

```
