import requests
import hashlib
import datetime

from django.conf import settings


def get(path, payload):
    try:
        return requests.get(
            settings.SALEBOX["API"]["URL"] + path,
            headers=generate_headers(),
            params=payload,
        )
    except:
        return None


def generate_headers():
    pos_id = settings.SALEBOX["API"]["KEY"]
    pos_license = settings.SALEBOX["API"]["LICENSE"]
    timestamp = str(round(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    generated = "".join([pos_id, pos_license, timestamp])
    return {
        "salebox-pos-id": pos_id,
        "salebox-timestamp": timestamp,
        "salebox-secret": hashlib.sha256(generated.encode("utf-8")).hexdigest(),
        "salebox-pos-version": "0.0.257",
    }


def post(path, payload):
    try:
        return requests.post(
            settings.SALEBOX["API"]["URL"] + path,
            headers=generate_headers(),
            json=payload,
        )
    except:
        return None
