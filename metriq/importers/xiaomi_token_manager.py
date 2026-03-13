import os
import json
import time
from pathlib import Path

from metriq.importers.xiaomi_auth import login

CACHE_FILE = "/opt/metriq/token_cache.json"


def get_token():

    if Path(CACHE_FILE).exists():

        with open(CACHE_FILE) as f:
            cache = json.load(f)

        if cache["expires"] > time.time():
            return cache

    creds = login(
        os.getenv("MI_USERNAME"),
        os.getenv("MI_PASSWORD")
    )

    token_data = {
        "userid": creds["userid"],
        "apptoken": creds["serviceToken"],
        "expires": time.time() + 21600
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(token_data, f)

    return token_data