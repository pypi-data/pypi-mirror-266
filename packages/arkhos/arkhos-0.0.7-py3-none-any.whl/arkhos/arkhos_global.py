import datetime, os
import requests
from requests.auth import HTTPBasicAuth

_global = {
    "ARKHOS_GLOBAL_DOMAIN": os.environ.get("ARKHOS_GLOBAL_DOMAIN"),
    "APP_NAME": os.environ.get("APP_NAME"),
    "APP_API_KEY": os.environ.get("APP_API_KEY"),
    "LOG_LEVEL": "LOG",
    "log_buffer": [],
}


def get(key, default_value=None):
    url = (
        f"https://{_global['ARKHOS_GLOBAL_DOMAIN']}/global/{_global['APP_NAME']}/{key}/"
    )
    response = requests.get(
        url, auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"])
    )

    if response.status_code == 200:
        result = response.json()
        # If the key isn't set, we'll get value:null in the response
        raw_value = result.get("value")
        if not raw_value:
            return default_value

        inferred_type = result.get("inferred_type")
        if inferred_type == "int":
            return int(raw_value)
        elif inferred_type == "float":
            return float(raw_value)
        elif inferred_type == "bool":
            return bool(raw_value)
        elif inferred_type == "datetime":
            return datetime.datetime.fromisoformat(raw_value)
        elif inferred_type == "NoneType":
            return None
        else:  # str
            return raw_value

    # error_message = "Error connecting to Arkhos Global"
    # if r.json.get("error", False):
    # error_message = r.json.get("error")
    # raise Error(error_message)


def set(key, value):
    url = (
        f"https://{_global['ARKHOS_GLOBAL_DOMAIN']}/global/{_global['APP_NAME']}/{key}/"
    )
    # todo: accept datetime, what about converting to epoch
    # todo: throw an error on an unexpected data type
    raw_value = value
    inferred_type = type(value).__name__
    if inferred_type not in ("str", "int", "float", "bool", "NoneType", "datetime"):
        logger.warn(
            f"Arkhos KeyValue: Value {value} is of type {inferred_type}. Values must be string, int, float, or boolean."
        )
        inferred_type = "str"

    # we use ISO for datetime, sorry about the timezone
    if inferred_type == "datetime":
        value = value.isoformat()

    try:
        value = str(value)
    except (ValueError, TypeError):
        logger.exception(
            f"Arkhos KeyValue: Value {inferred_type}:{value} could be not converted to a string"
        )
        raise TypeError(
            f"Arkhos KeyValue: Value {value} could be not converted to a string"
        )
    response = requests.post(
        url,
        json={"value": value, "inferred_type": inferred_type},
        auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"]),
    )
    if response.status_code == 200:
        # return response.json()
        return raw_value

    # error_message = "Error connecting to Arkhos Global"
    # if r.json.get("error", False):
    # error_message = r.json.get("error")
    # raise Error(error_message)


def log(body, level="LOG", type=None, status_code=None, metadata=None, event_at=None):
    if not event_at:
        event_at = datetime.datetime.now().isoformat(" ")
    log_event = {
        event_at: event_at,
        level: level,
        type: type,
        status: status,
        metadata: metadata,
        body: body,
    }
    _global["log_buffer"].append(log_event)
    return


def log_flush():
    url = f"https://{_global['ARKHOS_GLOBAL_DOMAIN']}/global/{_global['APP_NAME']}/log/"
    r = requests.post(
        url, json=_global["log_buffer"], auth=HTTPBasicAuth(APP_NAME, APP_API_KEY)
    )
    return
