# Django Zapier Triggers

**DO NOT USE IN PRODUCTION - ALPHA RELEASE**

Django app for managing Zapier triggers.

### Version support

This app supports Django 3.2+ (`HttpResponse.headers`), and Python 3.10+.

This app provides the minimal scaffolding required to support a Zapier
trigger in your application. Specifically it supports token-based
authentication and endpoints for RestHook and Polling triggers.

As well as three Django apps (`zapier.contrib.authtoken`,
`zapier.triggers.hooks` and `zapier.triggers.polling`) this project also
includes a working Zapier app (publishable using the Zapier CLI), and a
Demo django project that you can use to test the Zapier integration.
With the Demo app running locally (and available to the internet via
e.g. ngrok) you can test pushing data to a Zapier "zap".

### Prequisites

If you want to run the end-to-end demo you will need:

1. A Zapier account
2. The Zapier CLI
3. ngrok, or some equivalent tunnelling software

## How does it work?



## Usage
