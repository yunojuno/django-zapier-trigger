from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.decorators import csrf

from demo.models import Book
from zapier.authtoken.models import AuthToken
from zapier.polling.views import PollingTriggerView


def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)


class NewBooksById(PollingTriggerView):

    scope = "new_books"

    def get_last_obj(self, request: HttpRequest) -> dict | None:
        token: AuthToken = request.auth
        if log := token.requests.exclude(count=0).last():
            return log.most_recent_object
        return None

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = Book.objects.order_by("-id").values()
        if obj := self.get_last_obj(request):
            return qs.filter(id__gt=obj["id"])
        return qs


class NewBooksByTimestamp(NewBooksById):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = Book.objects.order_by("-id").values()
        if obj := self.get_last_obj(request):
            return qs.filter(published_at__gt=obj["published_at"])
        return qs


@csrf.csrf_exempt
def receive_webhook(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"result": "ok"})
