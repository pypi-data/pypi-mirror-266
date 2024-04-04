from __future__ import annotations

import time
import types
from typing import Any


def call_sql(frame, event, arg, context):
    # Doing the import once and binding is substantially faster than going
    # through the import system every time.
    # See:
    # https://github.com/django/asgiref/issues/269
    # https://github.com/django/asgiref/pull/288
    # A more battle-tested (slightly slower/more complex) alternative would be:
    # https://github.com/django/django/pull/14850
    # https://github.com/django/django/pull/14858
    # https://github.com/django/django/pull/14931
    if "class" not in context:
        from django.db.models.sql.compiler import SQLUpdateCompiler

        context["class"] = SQLUpdateCompiler
    return frame.f_code is not context["class"].execute_sql.__code__


def process_sql(
    frame: types.FrameType,
    event: str,
    arg: Any,
    context,
):
    timestamp = time.time()
    database = frame.f_locals["self"].connection.vendor
    if event == "call":
        return {
            "database": database,
            "call_timestamp": timestamp,
        }

    assert event == "return"

    try:
        sql = frame.f_locals["sql"]
        params = frame.f_locals["params"]
    except KeyError:
        query_template = None
        query = None
    else:
        if sql == "":
            query_template = None
            query = None
        else:
            cursor = frame.f_locals["cursor"]
            ops = frame.f_locals["self"].connection.ops
            query_template = sql.strip()
            query = ops.last_executed_query(cursor, sql, params).strip()

    return {
        "database": database,
        "return_timestamp": timestamp,
        "query_template": query_template,
        "query": query,
        "query_data": arg,
    }


sql = {
    "co_names": ("execute_sql",),
    "path_fragment": "/django/db/models/sql/compiler.py",
    "call": call_sql,
    "call_type": "start_sql_query",
    "return_type": "end_sql_query",
    "process": process_sql,
}
