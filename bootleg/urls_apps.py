from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# have to include these separately. If i include them in urls.py the namespaces will be messed up due to the
# app_name in urls.py

urlpatterns = [
    #######################################
    # django admin
    #######################################
    path('django-admin/', admin.site.urls),


]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
