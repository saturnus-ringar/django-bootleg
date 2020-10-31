from bootleg.views.system_views import DeployInfoView, SystemInfoView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView

import bootleg
from bootleg.conf import bootleg_settings
from bootleg.forms.auth_forms import LoginForm
from bootleg.views.auth_views import CustomLoginView, LogoutView, change_password, \
    CustomPasswordResetView, PasswordResetBaseView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
from bootleg.views.generic_model_views import GenericListView, GenericModelCreateView, GenericModelUpdateView
from bootleg.views.json_views import JSONSuggestView
from bootleg.views.views import DevNullView
from bootleg.views.xhr_views import JavascriptErrorView

# setup, indeed
bootleg.setup()

app_name = 'bootleg'

urlpatterns = [
    #######################################
    # basic URLs
    #######################################
    path('dev-null/', DevNullView.as_view(), name="dev_null"),

    #######################################
    # auth/login
    #######################################
    path('login/', CustomLoginView.as_view(authentication_form=LoginForm, title=_("Login")), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    # password
    path('password/', change_password, name="change_password"),
    path('password/reset/', CustomPasswordResetView.as_view(), name="password_reset"),
    path('password/reset/done/', PasswordResetBaseView.as_view(extra_text="Instructions on how to reset the password "
                                                                          "has been sent to your email-address."),
         name="password_reset_done"),
    path('password/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password/reset/complete/', CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    #######################################
    # list view(s)
    #######################################
    path('list/<model_name>/', GenericListView.as_view(), name="list_view"),

    #######################################
    # generic model create/update views
    #######################################
    path('create/<model_name>/', GenericModelCreateView.as_view(), name="create_model"),
    path('update/<model_name>/<int:id>', GenericModelUpdateView.as_view(), name="update_model"),

    #######################################
    # hxr-views
    #######################################
    path('json/<model_name>/', JSONSuggestView.as_view(), name='json_suggest'),
    path('xhr/javascript-error/', JavascriptErrorView.as_view(), name='javascript_error'),

    #######################################
    # misc-ish
    #######################################
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url(bootleg_settings.FAVICON_FILE))),

    #######################################
    # deploy/system info
    #######################################
    path('deploy/info/', DeployInfoView.as_view(), name="deploy_info"),
    path('system/info/', SystemInfoView.as_view(), name="system_info"),
]

if settings.DEBUG:
    media_url = getattr(settings, "MEDIA_URL", None)
    media_root = getattr(settings, "MEDIA_ROOT", None)
    # add media ... if it's debug and we have settings
    if media_url and media_root:
        urlpatterns += static(media_url, document_root=media_root)

