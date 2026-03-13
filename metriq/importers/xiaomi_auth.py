import requests
import hashlib
import json

LOGIN_URL = "https://account.xiaomi.com/pass/serviceLoginAuth2"

def login(username, password):

    password_hash = hashlib.md5(password.encode()).hexdigest().upper()

    payload = {
        "sid": "xiaomiio",
        "hash": password_hash,
        "user": username,
        "_json": "true"
    }

    r = requests.post(LOGIN_URL, data=payload)

    r.raise_for_status()

    # Xiaomi wraps JSON in weird prefix
    text = r.text.replace("&&&START&&&", "")
    data = json.loads(text)

    if "ssecurity" not in data:
        raise Exception("Login failed")

    service_token = r.cookies.get("serviceToken")

    return {
        "userid": data["userId"],
        "serviceToken": service_token
    }