from __future__ import annotations

import time
import types
from contextlib import suppress

from ..serialize import get_content, get_request_body


def process_django(
    frame: types.FrameType,
    event: str,
    arg: object,
    context,
):
    if event == "call":
        context["timestamp"] = time.time()
        request = frame.f_locals["request"]
        return {
            "body": get_request_body(request),
            "headers": dict(request.headers),
            "method": request.method,
            "path_info": request.path_info,
            # dict(request.POST) can give confusing results due to MultivalueDict
            "post_data": dict(request.POST),
            "query_params": dict(request.GET),
            "scheme": request.scheme,
            # Override the timestamp in PluginProcessor because consistency with
            # ms_duration is more important.
            "timestamp": context["timestamp"],
        }
    elif event == "return":  # pragma: no branch
        timestamp = time.time()
        duration = timestamp - context["timestamp"]
        ms_duration = round(duration * 1000, 2)

        request = frame.f_locals["request"]
        match = request.resolver_match
        if match:  # match is None if this is a 404
            # TODO(later): We should record the urlconf used, if it's not ROOT_URLCONF
            # TODO(later): We should report on whether it was a `path` or `re_path` if we can;
            #  we might have to look in `tried` or go up a frame to find the pattern object?
            url_pattern = {
                "namespace": match.namespace,
                "route": match.route,
                "url_name": match.url_name,
                "view_qualname": match._func_path,
            }
        else:
            url_pattern = None

        response = frame.f_locals["response"]
        return {
            "ms_duration": ms_duration,
            "status_code": response.status_code,
            "content": get_content(response),
            "headers": dict(response.items()),
            "url_pattern": url_pattern,
            # Override the timestamp in PluginProcessor because consistency with
            # ms_duration is more important.
            "timestamp": timestamp,
        }


def process_django_template(
    frame: types.FrameType,
    event: str,
    arg: object,
    context,
):
    template_context = frame.f_locals["context"]
    with suppress(AttributeError):
        template_context = template_context.flatten()

    return {
        "context": template_context,
        "template": frame.f_locals["self"].template.name,
    }


django = {
    "co_names": ("get_response",),
    "path_fragment": "/kolo/middleware.py",
    "call_type": "django_request",
    "return_type": "django_response",
    "process": process_django,
}

django_template = {
    "co_names": ("render",),
    "path_fragment": "django/template/backends/django.py",
    "call_type": "django_template_start",
    "return_type": "django_template_end",
    "process": process_django_template,
}

django_setup = {
    "co_names": ("setup",),
    "path_fragment": "django/__init__.py",
    "call_type": "django_setup_start",
    "return_type": "django_setup_end",
    "process": None,
}

django_checks = {
    "co_names": ("run_checks",),
    "path_fragment": "django/core/checks/registry.py",
    "call_type": "django_checks_start",
    "return_type": "django_checks_end",
    "process": None,
}

django_test_db = {
    "co_names": ("create_test_db",),
    "path_fragment": "django/db/backends/base/creation.py",
    "call_type": "django_create_test_db_start",
    "return_type": "django_create_test_db_end",
    "process": None,
}
