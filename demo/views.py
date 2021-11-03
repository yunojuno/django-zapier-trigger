from django.http import HttpRequest, JsonResponse

from zapier.decorators import polling_trigger


@polling_trigger("test_trigger")
def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)
