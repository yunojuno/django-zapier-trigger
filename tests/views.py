from django.http import HttpRequest, HttpResponse

from zapier.decorators import zapier_trigger


@zapier_trigger("foo")
def zapier_token_check(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")
