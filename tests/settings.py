from os import path

DEBUG = True
TEMPLATE_DEBUG = True
USE_TZ = True

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "test.db"}}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework.authtoken",
    "zapier.triggers",
)

MIDDLEWARE = [
    # default django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

PROJECT_DIR = path.abspath(path.join(path.dirname(__file__)))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
            ]
        },
    }
]

STATIC_URL = "/static/"

SECRET_KEY = "secret"  # noqa: S105

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {"handlers": ["console"], "propagate": True, "level": "DEBUG"},
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        #     'level': 'WARNING',
        # },
        "faker": {"level": "WARNING"},
        "factory": {"level": "WARNING"},
    },
}

ROOT_URLCONF = "tests.urls"

if not DEBUG:
    raise Exception("This settings file can only be used with DEBUG=True")

# ===============


def sample_trigger_func(request):
    return [{"id": 1, "title": "Huckleberry Finn"}]


def empty_trigger_func(request):
    return []


ZAPIER_TRIGGERS = {
    # reject requests where user-agent is not "Zapier"
    "STRICT_MODE": not DEBUG,
    # authenticate inbound requests from Zapier
    "AUTHENTICATOR": "rest_framework.authentication.TokenAuthentication",
    # map of available triggers to list functions
    "TRIGGERS": {
        "new_book": "tests.settings.sample_trigger_func",
        "no_book": "tests.settings.empty_trigger_func",
    },
}
