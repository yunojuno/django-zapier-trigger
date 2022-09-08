import json

from django.http import JsonResponse

from zapier.exceptions import JsonResponseError


def parse_response(response: JsonResponse) -> list | dict:
    """
    Parse JsonResponse content into JSON (list or dict).

    This is a utility function for parsing JsonResponse content into
    something that can be saved to the PollingTriggerRequest model.

    """
    try:
        return json.loads(response.content)
    except json.decoder.JSONDecodeError as ex:
        raise JsonResponseError("Invalid JSON") from ex
