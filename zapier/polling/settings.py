from django.conf import settings

# max number of objects to return
DEFAULT_PAGE_SIZE = getattr(settings, "ZAPIER_TRIGGER_DEFAULT_PAGE_SIZE", 25)
