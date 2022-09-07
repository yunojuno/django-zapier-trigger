from django.conf import settings

# max number of objects to return
DEFAULT_PAGE_SIZE = getattr(settings, "ZAPIER_TRIGGER_DEFAULT_PAGE_SIZE", 25)

# dict mapping trigger scope to a view function
VIEW_FUNC_MAP = getattr(settings, "ZAPIER_TRIGGER_VIEW_FUNC_MAP", {})
