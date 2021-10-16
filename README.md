# Django Zapier Triggers

Django app for managing Zapier trigger authentication

This app provides the minimal scaffolding required to support a Zapier
trigger in your application. Specifically it supports token-based
authentication for [polling
triggers](https://platform.zapier.com/docs/triggers#polling-trigger).

### Version support

This app supports Django 3.1+, and Python 3.7+.

## How does it work?

The app has a single model that stores an API token (UUID) against a
User. The token object has the concept of "scope" which is an array of
strings representing API triggers that are supported. In effect it uses
the token UUID for authentication, and the token scopes for
authorization.

## Installation

Install the package using pip / poetry

```
pip install django-zapier-triggers
```

## Configuration

1. Add the app to your `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = [
    ...,
    zapier,
]
```

2. Run migrations to add model tables

```
$ python manage.py migrate
```

3. Add a url for the Zapier auth check

```python
# urls.py
urlpatterns = [
    ...
    path(
        "zapier/auth-check/",
        zapier.views.TriggerAuthCheck.as_view(),
        name="zapier_auth_check",
    ),
]
```

4. Configure Zapier trigger

Zapier triggers: https://platform.zapier.com/docs/triggers

This app supports the "API Key" auth model for Zapier apps:
https://platform.zapier.com/docs/apikey

You must configure your Zapier authentication to use API Key
authentication, and in the step "Configure a Test Request & Connection
Label" you should ensure that you are passing the API Key as a request
header called "X-Api-Token", and not in the URL.

NB You will need to host your application somewhere that is visible on
the internet in order to confirm that the authentication works. `ngrok`
is a good option to run the application locally.

## Usage

The app does not automatically add tokens for your users - this is your
responsibility:

```python
# example view function for creating a new token
def add_zapier_token(request: HttpRequest) -> HttpResponse:
    ZapierToken.objects.create(user=request.user, scopes=["default_scope"])
    return HttpReponse("ok")

# example view function for adding a new scope to a token
def add_zapier_token_scope(request: HttpRequest, new_scope: str) -> HttpResponse:
    token = request.user.zapier_token
    token.add_scope(new_scope)
    return HttpReponse("ok")
```

### Creating a polling trigger
