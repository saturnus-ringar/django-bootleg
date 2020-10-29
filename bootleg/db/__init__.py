from django.db.models import options

# allow some custom Meta attributes on them models
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("visible_fields", "create_url", "search_fields", "admin_class",
                                                 "autocomplete_field")
