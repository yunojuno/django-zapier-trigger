from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html, mark_safe


def format_json_for_admin(data: dict) -> str:
    """
    Pretty-print JSON data in admin site.

    Take entity context JSON, indent it, order the keys and then present
    it as a <code> block. That's about as good as we can get until
    someone builds a custom syntax function.

    """
    pretty = json.dumps(
        data, cls=DjangoJSONEncoder, sort_keys=True, indent=4, separators=(",", ": ")
    )
    # https://docs.djangoproject.com/en/1.11/ref/utils/#django.utils.html.format_html
    # this is a fudge to get around the fact that we cannot put a <pre> inside a <p>,
    # but we want the <p> formatting (.align CSS). We can either use a <pre> and an
    # inline style to mimic the CSS, or forego the <pre> and put the spaces
    # and linebreaks in as HTML.
    pretty = pretty.replace(" ", "&nbsp;").replace("\n", "<br/>")
    return format_html("<code>{}</code>", mark_safe(pretty))
