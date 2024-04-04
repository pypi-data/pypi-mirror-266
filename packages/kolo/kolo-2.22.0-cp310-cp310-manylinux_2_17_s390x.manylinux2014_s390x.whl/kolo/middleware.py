from __future__ import annotations

import logging
import mimetypes
import os
import sqlite3
import sys
import threading
from itertools import chain
from typing import Awaitable, Callable

import httpx
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    JsonResponse,
)

from .config import load_config
from .db import list_traces_from_db, setup_db
from .profiler import KoloProfiler
from .serialize import monkeypatch_queryset_repr
from .upload import upload_to_dashboard
from .web.home import kolo_web_home

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]
DjangoAsyncView = Callable[[HttpRequest], Awaitable[HttpResponse]]


class KoloMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: DjangoView | DjangoAsyncView) -> None:
        self._is_coroutine = iscoroutinefunction(get_response)
        if self._is_coroutine:
            markcoroutinefunction(self)
        self._get_response = get_response
        self.config = load_config()
        self.upload_token = self.get_upload_token()
        self.enabled = self.should_enable()
        if self.enabled:
            self.db_path = setup_db()

            # TODO: Put the full URL here not just the /_kolo/ path
            if self.config.get("web_experience", False):
                print("\nView recent requests at /_kolo/")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_coroutine:
            # TODO: Handle _kolo/ for asgi???
            get_response = self.aget_response
        else:
            if request.path.startswith("/_kolo"):
                return kolo_web_router(request)

            get_response = self.get_response  # type: ignore

        # WARNING: Because Django's runserver uses threading, we need
        # to be careful about thread safety here.
        if not self.enabled or self.check_for_third_party_profiler():
            return get_response(request)  # type: ignore

        filter_config = self.config.get("filters", {})
        ignore_request_paths = filter_config.get("ignore_request_paths", [])
        for path in ignore_request_paths:
            if path in request.path:
                return get_response(request)  # type: ignore

        # Don't store the KoloProfiler on self to avoid threadsafety
        # bugs. If a different thread gets this instance of KoloProfiler
        # at the wrong time, we lose the original profiler's trace.
        profiler = KoloProfiler(
            self.db_path, config=self.config, source="kolo.middleware.KoloMiddleware"
        )

        monkeypatch_queryset_repr()
        if self._is_coroutine:
            return self.aprofile_response(request, profiler)
        else:
            return self.profile_response(request, profiler)

    def profile_response(self, request, profiler):
        with profiler:
            response = self.get_response(request)
        self.save_trace(profiler)
        return response

    async def aprofile_response(self, request, profiler):
        with profiler:
            response = await self.aget_response(request)
        self.save_trace(profiler)
        return response

    async def aget_response(self, request: HttpRequest) -> HttpResponse:
        response = await self._get_response(request)  # type: ignore
        return response

    def get_response(self, request: HttpRequest) -> HttpResponse:
        response = self._get_response(request)
        return response  # type: ignore

    def save_trace(self, profiler):
        if settings.DEBUG is False and self.upload_token:

            def upload():
                trace = profiler.build_trace()
                try:
                    response = upload_to_dashboard(trace, self.upload_token)
                    response.raise_for_status()
                except httpx.HTTPError:
                    logger.exception("Failed to upload trace to Kolo dashboard.")

            name = "kolo-upload_to_dashboard"
            threading.Thread(target=upload, name=name).start()
        else:
            name = "kolo-save_request_in_db"
            threading.Thread(target=profiler.save_request_in_db, name=name).start()

    def check_for_third_party_profiler(self) -> bool:
        profiler = sys.getprofile()
        if profiler:
            logger.warning("Profiler %s is active, disabling KoloMiddleware", profiler)
            return True
        if self.config.get("threading", False):
            try:
                profiler = threading.getprofile()  # type: ignore[attr-defined]
            except AttributeError:
                profiler = threading._profile_hook
            if profiler:  # pragma: no branch
                logger.warning(
                    "Profiler %s is active, disabling KoloMiddleware", profiler
                )
                return True
        return False

    def should_enable(self) -> bool:
        if settings.DEBUG is False and self.upload_token is None:
            logger.debug("DEBUG mode is off, disabling KoloMiddleware")
            return False

        if os.environ.get("KOLO_DISABLE", "false").lower() not in ["false", "0"]:
            logger.debug("KOLO_DISABLE is set, disabling KoloMiddleware")
            return False

        if self.check_for_third_party_profiler():
            return False

        return True

    def get_upload_token(self):
        if not self.config.get("production_beta", False):
            return None

        upload_token = os.environ.get("KOLO_API_TOKEN", None)
        if upload_token is None:
            logging.warning(
                "Kolo production beta is enabled, but `KOLO_API_TOKEN` environment variable is not set."
            )
            return None

        if upload_token.startswith("kolo_prod_"):
            return upload_token

        logging.warning("`KOLO_API_TOKEN` is invalid.")
        return None


def kolo_web_router(request: HttpRequest) -> HttpResponse:
    path = request.path
    if path == "/_kolo/" or path == "/_kolo" or path.startswith("/_kolo/traces/"):
        return kolo_web_home(request)
    elif path.startswith("/_kolo/static/"):
        static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
        file_path = os.path.join(static_dir, request.path[len("/_kolo/static/") :])

        if os.path.exists(file_path):
            mime_type, encoding = mimetypes.guess_type(file_path)
            return FileResponse(  # type: ignore # seems iffy and difficult to fix with little benefit
                open(file_path, "rb"),
                content_type=mime_type or "application/octet-stream",
            )
        else:
            return HttpResponseNotFound("File not found")
    elif path.startswith("/_kolo/api/generate-test/"):
        return kolo_web_api_generate_test(request)
    elif path.startswith("/_kolo/api/traces/"):
        return kolo_web_api_get_trace(request)
    elif path.startswith("/_kolo/api/latest-traces/"):
        return kolo_web_api_latest_traces(request)
    else:
        return HttpResponseNotFound("Kolo Web: Not Found")


def kolo_web_api_generate_test(request: HttpRequest) -> HttpResponse:
    trace_id = request.path.replace("/_kolo/api/generate-test/", "").replace("/", "")

    from .generate_tests import generate_from_trace_ids

    test_code = generate_from_trace_ids(
        trace_id, test_class="MyTestCase", test_name="test_my_view"
    )

    return JsonResponse({"test_code": test_code})


def kolo_web_api_get_trace(request: HttpRequest) -> HttpResponse:
    trace_id = request.path.replace("/_kolo/api/traces/", "").replace("/", "")

    from .db import load_trace_from_db

    db_path = setup_db()

    msgpack_data, json_data = load_trace_from_db(db_path, trace_id)
    if json_data:
        return HttpResponse(json_data, content_type="application/json")
    else:
        return HttpResponse(msgpack_data, content_type="application/msgpack")


def kolo_web_api_latest_traces(request: HttpRequest) -> HttpResponse:
    from .db import db_connection

    db_path = setup_db()

    with db_connection(db_path) as connection:
        needs_reversed_order = False
        reached_top = False

        if "anchor" in request.GET and "showNext" in request.GET:
            # this is a pagination request

            anchor = request.GET["anchor"]
            show_next = int(request.GET["showNext"])

            limit = abs(show_next)

            # Positive show_next value means we're going back in time (loading _more_ traces),
            # negative value is for going forward in time (loading traces the user has previously seen before going back).

            if show_next > 0:
                # going back in time, trying to access older traces than the anchor

                query = "SELECT id FROM traces WHERE id < ? ORDER BY id desc LIMIT ?"
                cursor = connection.execute(query, (anchor, limit))
                rows = cursor.fetchall()
            else:
                # going forward in time, trying to access newer traces than the anchor

                query = "SELECT id FROM traces WHERE id > ? ORDER BY id LIMIT ?"
                needs_reversed_order = True
                # In order to get 10 newer traces, they need to be sorted in ascending order.
                # They have to be reversed later because the endpoint should always return traces from newest to oldest.

                cursor = connection.execute(query, (anchor, limit))
                rows = cursor.fetchall()

                if len(rows) < abs(limit):
                    # If there are less than 10 newer traces, we need to fetch some older traces to fill up the response.
                    cursor = connection.execute(
                        "SELECT id FROM traces ORDER BY id desc LIMIT ?", (abs(limit),)
                    )
                    rows = cursor.fetchall()

                    reached_top = True
                    needs_reversed_order = False
        else:
            # not a pagination request, we just want N latest traces

            limit = int(request.GET.get("showNext", 10))
            cursor = connection.execute(
                "SELECT id FROM traces ORDER BY id desc LIMIT ?", (limit,)
            )

            rows = cursor.fetchall()
            reached_top = True

        traces = list(chain.from_iterable(rows))

        if needs_reversed_order:
            traces = traces[::-1]

    return JsonResponse({"traces": traces, "isTop": reached_top})
