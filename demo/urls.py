from django.contrib import admin
from django.urls import include, path
from django.views import debug

# from .views import NewFilms, new_films

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path(
        "zapier/triggers/", include("zapier.triggers.urls", namespace="zapier_triggers")
    ),
    # path("demo/films/v1/", NewFilms.as_view()),
    # path("demo/films/v2/", new_films),
]
