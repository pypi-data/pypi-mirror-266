import gzip
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("kolo")


def upload_to_dashboard(trace: bytes, upload_key: Optional[str] = None):
    base_url = os.environ.get("KOLO_BASE_URL", "https://my.kolo.app")
    url = f"{base_url}/api/traces/"
    payload = gzip.compress(trace)
    if upload_key:
        data = {"token": upload_key}
    else:
        data = None
    return httpx.post(url, data=data, files={"data": payload})
