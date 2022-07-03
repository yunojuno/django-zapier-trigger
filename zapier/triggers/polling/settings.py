from django.conf import settings

# max number of objects to return
DEFAULT_PAGE_SIZE = getattr(settings, "ZAPIER_TRIGGER_DEFAULT_PAGE_SIZE", 25)

# value of None, "ALL", or "NON_ZERO" (default) that determines how a
# polling request is logged.
TRIGGER_REQUEST_LOG = getattr(settings, "ZAPIER_TRIGGER_REQUEST_LOG", "NON_ZERO")
