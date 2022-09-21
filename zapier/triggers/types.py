# type alias for the "list" view functions
from typing import Callable, TypeAlias

from django.http import HttpResponseNotFound
from rest_framework.request import Request

from zapier.triggers.response import JsonResponse

TriggerData: TypeAlias = list[dict]
TriggerViewFunc: TypeAlias = Callable[[Request], TriggerData]
TriggerViewMethod: TypeAlias = Callable[..., JsonResponse | HttpResponseNotFound]
