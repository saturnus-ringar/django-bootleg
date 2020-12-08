from django.db.models import options

# allow some custom Meta attributes on them models
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("visible_fields", "filter_fields", "extra_search_fields", "create_url",
                                                 "exclude_from_menu", "cloneable", "disable_create_update",
                                                 "allow_deletion")
