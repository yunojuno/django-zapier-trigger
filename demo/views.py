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

    def get_queryset(self, token: ZapierToken) -> QuerySet:
        if last_obj := token.get_most_recent_object(self.scope):
            return Book.objects.filter(id__gt=last_obj["id"]).values()
        return Book.objects.all().values()


class NewBooksByTimestamp(PollingTriggerView):

    scope = "new_books"

    def get_queryset(self, token: ZapierToken) -> QuerySet:
        if last_obj := token.get_most_recent_object(self.scope):
            return Book.objects.filter(
                published_at__gt=last_obj["published_at"]
            ).values()
        return Book.objects.all().values()
