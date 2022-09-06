from django.contrib import admin
from django.urls import include, path
from django.views import debug

# import zapier.triggers.hooks.urls
# from demo.views import NewBooksById, NewBooksByTimestamp, receive_webhook
# from demo.views import test as test_view

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("zapier/auth/", include("zapier.contrib.authtoken.urls", namespace="zapier")),
    path("zapier/hooks/", include("zapier.triggers.hooks.urls", namespace="zapier")),
    #     path("demo/test/<int:number>/", test_view, name="test"),
    #     path("demo/books/id/", NewBooksById.as_view()),
    #     path("demo/books/timestamp/", NewBooksByTimestamp.as_view()),
    #     path("demo/webhook/", receive_webhook),
]
