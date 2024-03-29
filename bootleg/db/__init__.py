from django.db.models import options

# allow some custom Meta attributes on them models
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("visible_fields", "filter_fields", "search_fields",
                                                 "exact_match_fields", "extra_search_fields", "create_url",
                                                 "exclude_from_menu", "cloneable", "disable_create_update",
                                                 "allow_deletion", "prefetch_related", "autocomplete_fields",
                                                 "sequence", "public_listing", "disable_autocomplete", "wide_table",
                                                 "paginator", "input_ordering", "order")
