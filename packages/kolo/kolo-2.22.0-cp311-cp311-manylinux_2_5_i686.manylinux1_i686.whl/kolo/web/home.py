from __future__ import annotations

import logging
from typing import Awaitable, Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]
DjangoAsyncView = Callable[[HttpRequest], Awaitable[HttpResponse]]


def kolo_web_home(request: HttpRequest) -> HttpResponse:
    html = f"""<!DOCTYPE html>
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Kolo</title>

      <link rel="icon" href="/_kolo/favicon.ico">

      <!-- For light mode -->
      <link rel="icon" sizes="16x16" href="/_kolo/static/favicons/favicon-dark-16x16.png" media="(prefers-color-scheme: light)">
      <link rel="icon" sizes="32x32" href="/_kolo/static/favicons/favicon-dark-32x32.png" media="(prefers-color-scheme: light)">

      <!-- For dark mode -->
      <link rel="icon" sizes="16x16" href="/_kolo/static/favicons/favicon-light-16x16.png" media="(prefers-color-scheme: dark)">
      <link rel="icon" sizes="32x32" href="/_kolo/static/favicons/favicon-light-32x32.png" media="(prefers-color-scheme: dark)">

      <link rel="stylesheet" href="/_kolo/static/main.css" />
      <script type="text/javascript">
      window.kolo = {{
        "options": {{
            "mountPoint": "/_kolo/",
            "baseUrl": new URL('/_kolo/', window.location),
            "island": false,
            "local": true
        }}
      }}
    </script>
    </head>
  <body>
    <div id="root"></div>
    <script type="text/javascript" src="/_kolo/static/main.js"></script>
  </body>
"""

    return HttpResponse(html)
