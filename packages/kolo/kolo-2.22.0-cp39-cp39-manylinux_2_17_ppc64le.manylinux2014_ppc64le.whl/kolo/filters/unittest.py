from __future__ import annotations

import ulid

EVENT_TYPES = {
    "startTest": "start_test",
    "stopTest": "end_test",
}


def call_unittest(frame, event, arg, context):
    return event == "call"  # pragma: no cover


def process_unittest(frame, event, arg, context):  # pragma: no cover
    frame_ids = context["frame_ids"]
    testcase = frame.f_locals["test"]
    co_name = frame.f_code.co_name
    if co_name == "startTest":
        frame_id = f"frm_{ulid.new()}"
        frame_ids[id(testcase)] = frame_id
    else:
        frame_id = frame_ids[id(testcase)]
    return {
        "frame_id": frame_id,
        "type": EVENT_TYPES[co_name],
        "test_name": testcase._testMethodName,
        "test_class": testcase.__class__.__qualname__,
    }


def build_context(config):
    return {"frame_ids": {}}


unittest = {
    "co_names": tuple(EVENT_TYPES),
    "path_fragment": "unittest/result.py",
    "call": call_unittest,
    "call_type": "",
    "return_type": "",
    "process": process_unittest,
    "build_context": build_context,
}
