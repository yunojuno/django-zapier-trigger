from django.urls import path

from .views import polling_trigger_view

app_name = "zapier_polling"

urlpatterns = [
    path("<str:scope>/", polling_trigger_view, name="polling_trigger_view"),
]
