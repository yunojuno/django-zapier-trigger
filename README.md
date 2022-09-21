# Django Zapier Triggers

Django (DRF) app for managing Zapier triggers.

### Version support

This app supports Django 3.2+ and Python 3.10+.

## Background

This app provides the minimal scaffolding required to support Zapier triggers in your Django application. It is based on DRF.

In addition to the `zapier.triggers` Django app, this project includes two additional applications: a complete Zapier CLI application that you can publish to Zapier, and a Demo project that provides the Django support for it. With these two projects you have a complete end-to-end Zapier integration.

## Zapier Triggers

A Zapier trigger is an event source for Zapier workflows ("Zaps"), that can operate in one of two modes - "Instant", or "Polling". Either way the net result is that JSON data objects are received by Zapier and can be used as the first step in a Zap.

There is a _lot_ of documentation online from Zapier about how to create a trigger, and I would strongly recommend reading it before attempting to build your own. Here are a couple of good articles to start with:

- https://platform.zapier.com/docs/start
- https://platform.zapier.com/cli_tutorials/getting-started

### Prequisites

If you want to run the end-to-end demo you will need:

1. A Zapier account
2. The Zapier CLI
3. ngrok, or some equivalent tunnelling software

## What's in the box?

The core implementation detail of this package is the `TriggerView`. This is a DRF `APIView` class that handles `GET`, `POST`, and `DELETE` methods, mapping them to the Zapier trigger methods for polling ("list"), susbscribe and unsubscribe functions.

### `GET /triggers/{{trigger}}/`

When Zapier makes a `GET` request to your application endpoint one of two things is happening. For a REST Hook ("Instant") trigger this is request sample data that Zapier can use to create its Zap builder UI. If your trigger is a push ("Instant") then you can just return static data - as long as it conforms to the same schema as real data. The `demo.views.new_book` view demonstrates this.

If your trigger is a polling trigger then this endpoint should return real data - the `demo.views.new_film` view is an example of this.

The view returns a `200` status code.

### `POST /triggers/{{trigger}}/subscriptions/`

When Zapier makes a `POST` request it is expecting to create a new webhook (rebranded "REST Hook" by Zapier) susbscription. This is handled automatically by the view, which creates a new `TriggerSubscription` object for the user + trigger combination, and returns the `uuid` property to Zapier, which stores it in its `bundle.subscriptionData.id` property.

The view returns a `201` status code.

### `DELETE /triggers/{{trigger}}/subscriptions/{{subscription_id}}`

When Zapier makes a `DELETE` request it is expecting to delete the subscription identified by the `subscription_id` value, which maps to the `uuid` property. We do not delete the subscription but instead mark it as "inactive". This is because we record all of the event data that is sent by a trigger subscription, and we we want to keep this for a period for auditing purposes. If a new `POST` request is made for the same user + trigger combination the subscription is reactivated.

The view returns a `204` status code.

## Settings

The settings are all read in from the Django setting `ZAPIER_TRIGGER`, which is a dict containing the following keys:

* `STRICT_MODE`

The JSON key used to extract the Zapier subscription URL endpoint in the body of the `POST` request - defaults to `hookUrl`.

* `TRIGGERS`

This is a dict containing the name of the trigger and a string path to a view-like function that must accept a single `Request` arg and return a list of JSON-serializable dict objects. Every trigger that your Zapier app supports must be in this setting - otherwise any request made to `/triggers/{{trigger}}` will return a `404`.

## Demo + zapier-app

The easiest way to work out how this all fits together is to run the demo app and push the zapier-app to Zapier under your own account.
