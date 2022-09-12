from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse as DjangoJsonResponse


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data: list | dict, **kwargs: Any) -> None:
        kwargs.setdefault("encoder", DjangoJSONEncoder)
        super().__init__(data, **kwargs)
