from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse

from demo.models import Book
from zapier.decorators import polling_trigger
from zapier.models import ZapierToken
from zapier.views import PollingTriggerView


@polling_trigger("test_trigger")
def test(request: HttpRequest, number: int) -> JsonResponse:
    return JsonResponse([{"id": i} for i in reversed(range(number))], safe=False)


class NewBooksById(PollingTriggerView):

    scope = "new_books"

    def get_last_obj(self, request: HttpRequest) -> dict | None:
        token: ZapierToken = request.auth
        if log := token.requests.exclude(count=0).last():
            return log.most_recent_object
        return None

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        if obj := self.get_last_obj(request):
            return Book.objects.filter(id__gt=obj["id"]).values()
        return Book.objects.all().values()


class NewBooksByTimestamp(NewBooksById):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        if obj := self.get_last_obj(request):
            qs = Book.objects.filter(published_at__gt=obj["published_at"])
            return qs.order_by("-published_at").values()
        return Book.objects.all().values()
