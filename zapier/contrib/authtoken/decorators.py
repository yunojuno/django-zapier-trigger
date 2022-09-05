# from __future__ import annotations

# from typing import Callable

# from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse

# from zapier.contrib.authtoken.models import AuthToken, ZapierUser

# from .exceptions import MissingTokenHeader, TokenAuthError, TokenUserError, UnknownToken


# def extract_bearer_token(request: HttpRequest) -> AuthToken:
#     """Return token from 'Authorization: Bearer {{token}}' request header."""
#     if bearer_key := request.headers.get("Authorization", ""):
#         if not bearer_key.startswith("Bearer "):
#             raise MissingTokenHeader(
#                 "Authorization header must be in the form: "
#                 "Authorization: 'Bearer {API_KEY}'"
#             )
#         api_key = bearer_key.split(" ", 1)[1]
#         try:
#             return AuthToken.objects.get(api_key=api_key)
#         except AuthToken.DoesNotExist:
#             raise UnknownToken("No token was found for supplied api_key.")
#     raise MissingTokenHeader(
#         "Request must include valid Authorization header in the form "
#         "Authorization: 'Bearer {API_KEY}'"
#     )


# def authenticate_request(request: HttpRequest) -> None:
#     """
#     Authenticate X-Api-Token request header.

#     Sets request.user (ZapierUser) and request.auth (AuthToken) from the
#     AuthToken that matches the header.

#     Raises TokenAuthenticationError if the token is invalid / missing.

#     """
#     if hasattr(request, "user") and request.user.is_authenticated:
#         raise TokenUserError("This does not look like a Zapier request")
#     auth_token = extract_bearer_token(request)
#     if not auth_token.user.is_active:
#         raise TokenUserError("Auth token user is inactive.")
#     request.auth = auth_token
#     request.user = ZapierUser()


# def authenticate_zapier_view(view_func) -> Callable:
#     """Authenticate token requests."""
#     def decorated_func(
#         request: HttpRequest, *view_args: object, **view_kwargs: object
#     ) -> HttpResponse:
#         try:
#             authenticate_request(request)
#             return view_func(request, *view_args, **view_kwargs)
#         except TokenAuthError as ex:
#             return HttpResponseForbidden(ex)
#     return decorated_func
