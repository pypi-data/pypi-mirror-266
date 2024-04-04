from __future__ import annotations

import types

import ulid

EVENT_TYPES = {
    "pytest_runtest_logstart": "start_test",
    "pytest_runtest_logfinish": "end_test",
}


def pytest_generated_filter(frame: types.FrameType, event: str, arg: object) -> bool:
    """
    Ignore pytest generated code

    When using the `-k` or `-m` command line argument, pytest compiles
    code with a custom filename:

        <pytest match expression>

    https://github.com/pytest-dev/pytest/blob/9454fc38d3636b79ee657d6cacf7477eb8acee52/src/_pytest/mark/expression.py#L208

    Since this is library code, we want to filter it out.
    """
    return frame.f_code.co_filename == "<pytest match expression>"


def call_pytest(frame, event, arg, context):
    return event == "call"  # pragma: no cover


def build_context(config):
    return {"frame_ids": {}}


def process_pytest(frame, event, arg, context):  # pragma: no cover
    frame_ids = context["frame_ids"]
    co_name = frame.f_code.co_name
    location = frame.f_locals["location"]
    if co_name == "pytest_runtest_logstart":
        frame_id = f"frm_{ulid.new()}"
        frame_ids[id(location)] = frame_id
    else:
        frame_id = frame_ids[id(location)]

    filename, lineno, test = location
    test_class, _sep, test_name = test.rpartition(".")
    return {
        "frame_id": frame_id,
        "type": EVENT_TYPES[co_name],
        "test_name": test_name,
        "test_class": test_class if test_class else None,
    }


pytest = {
    "co_names": tuple(EVENT_TYPES),
    "path_fragment": "kolo/pytest_plugin.py",
    "call": call_pytest,
    "call_type": "",
    "return_type": "",
    "process": process_pytest,
    "build_context": build_context,
}
