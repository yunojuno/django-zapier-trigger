from django.contrib import admin
from django.urls import include, path
from django.views import debug

import zapier.authtoken.urls
import zapier.hooks.urls
from demo.views import NewBooksById, NewBooksByTimestamp, receive_webhook
from demo.views import test as test_view

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("zapier/", include(zapier.authtoken.urls, namespace="zapier_auth")),
    path("zapier/", include(zapier.hooks.urls, namespace="zapier_hooks")),
    path("demo/test/<int:number>/", test_view, name="test"),
    path("demo/books/id/", NewBooksById.as_view()),
    path("demo/books/timestamp/", NewBooksByTimestamp.as_view()),
    path("demo/webhook/", receive_webhook),
]
