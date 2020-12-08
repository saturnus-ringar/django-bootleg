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
from bootleg.views.generic_model_views import GenericListView, GenericModelCreateView, GenericModelUpdateView, \
    GenericModelCloneView, GenericModelDetailView, GenericModelDeleteView
from bootleg.views.json_views import JSONAutocompleteView, JSONFieldAutocompleteView
from bootleg.views.views import DevNullView, CrashView, ErrorTestView, CreatedView
from bootleg.views.ajax_views import JavascriptErrorView

# setup, indeed
bootleg.setup()

app_name = "bootleg"

urlpatterns = [
    #######################################
    # basic URLs
    #######################################
    # a test URL, to test if the site is working. More or less...
    path("dev-null/", DevNullView.as_view(), name="dev_null"),

    #######################################
    # auth/login
    #######################################
    path("login/", CustomLoginView.as_view(authentication_form=LoginForm, page_title=_("Login")), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # password
    path("password/", change_password, name="change_password"),
    path("password/reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password/reset/done/", PasswordResetBaseView.as_view(extra_text="Instructions on how to reset the password "
                                                                          "has been sent to your email-address."),
         name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/reset/complete/", CustomPasswordResetCompleteView.as_view(),
         name="password_reset_complete"),

    #######################################
    # list view(s)
    #######################################
    path("list/<model_name>/", GenericListView.as_view(), name="list_view"),

    #######################################
    # generic models
    #######################################
    path("create/<model_name>/", GenericModelCreateView.as_view(), name="create_model"),
    path("update/<model_name>/<int:pk>", GenericModelUpdateView.as_view(), name="update_model"),
    path("view/<model_name>/<int:pk>", GenericModelDetailView.as_view(), name="model_detail"),
    path("clone/<model_name>/<int:pk>", GenericModelCloneView.as_view(), name="clone_model"),
    path("delete/<model_name>/<int:pk>", GenericModelDeleteView.as_view(), name="delete_model"),

    #######################################
    # created page
    #######################################
    path("created/<model_name>", CreatedView.as_view(), name="created"),

    #######################################
    # hxr-views
    #######################################
    path("json/<model_name>/", JSONAutocompleteView.as_view(), name="json_autocomplete"),
    path("json/<model_name>/<field_name>", JSONFieldAutocompleteView.as_view(), name="json_field_autocomplete"),
    path("ajax/javascript-error/", JavascriptErrorView.as_view(), name="javascript_error"),

    #######################################
    # misc-ish
    #######################################
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url(bootleg_settings.FAVICON_FILE))),

    #######################################
    # deploy/system info
    #######################################
    path("deploy/info/", DeployInfoView.as_view(), name="deploy_info"),
    path("system/info/", SystemInfoView.as_view(), name="system_info"),

    #######################################
    # error page test
    #######################################
    path("obscurity-by-test/error/<error_code>/", ErrorTestView.as_view(), name="error_test"),

    #######################################
    # crash-url - to test errors
    #######################################
    path("crash/", CrashView.as_view(), name="crash"),

]

if settings.DEBUG:
    media_url = getattr(settings, "MEDIA_URL", None)
    media_root = getattr(settings, "MEDIA_ROOT", None)
    # add media ... if it's debug and we have settings
    if media_url and media_root:
        urlpatterns += static(media_url, document_root=media_root)

