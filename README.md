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
        zapier.views.zapier_token_check,
        name="zapier_auth_check",
    ),
]
```

4. Configure Zapier trigger (https://platform.zapier.com/docs/triggers)

This app supports the "API Key" auth model for Zapier apps
https://platform.zapier.com/docs/apikey

You must configure your Zapier authentication to use API Key
authentication, and in the step "Configure a Test Request & Connection
Label" you should ensure that you are passing the API Key as a request
header called "X-Api-Token", and not in the URL.

NB You will need to host your application somewhere that is visible on
the internet in order to confirm that the authentication works. `ngrok`
is a good option to run the application locally.

## Usage

Now that you have authentication set up, you can create your triggers. A
polling trigger is nothing more that a GET endpoint that supports the
token authentication and that returns an ordered list of JSON objects.
Zapier itself handles deduplication of objects using the `id` property
of each object that is returned - you can read more about deduplication
here - https://zapier.com/help/create/basics/data-deduplication-in-zaps

This package is responsible for the endpoint authentication - everything
else is up to you. You can use the `zapier_trigger` view function
decorator to guard the functions that you set up as triggers. The
decorator takes a required string argument, which is a scope that must
match the incoming `request.auth`. The decorator handles request
authentication, setting the `request.user` and `request.auth`
properties.

```python
# views.py
@zapier.decorators.zapier_trigger("new_books")
def new_books_trigger(request: HttpRequest) -> JsonResponse:
    latest_id = request.auth.get_latest_id("new_books") or -1
    books = Book.objects.filter(id__gt=latest_id).order_by("-id")[:25]
    data = [{"id": book.id, "title": book.title} for book in books]
    return JsonReponse(data)
```
