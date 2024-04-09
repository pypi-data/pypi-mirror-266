import logging
import os
import re
import sys
from enum import Enum
from typing import Optional

import brainai

brainai_LOG = os.environ.get("brainai_LOG")

logger = logging.getLogger("brainai")

__all__ = [
    "log_info",
    "log_debug",
    "log_warn",
    "logfmt",
]

api_key_to_header = (
    lambda api, key: {"Authorization": f"{key}"}
    if api in (ApiType.RUBIK_AI, ApiType.AZURE_AD)
    else {"api-key": f"{key}"}
)


class ApiType(Enum):
    AZURE = 1
    RUBIK_AI = 2
    AZURE_AD = 3

    @staticmethod
    def from_str(label):
        if label.lower() == "azure":
            return ApiType.AZURE
        elif label.lower() in ("azure_ad", "azuread"):
            return ApiType.AZURE_AD
        elif label.lower() in ("rubik_ai", "brainai"):
            return ApiType.RUBIK_AI
        else:
            raise brainai.error.InvalidAPIType(
                "The API type provided in invalid. Please select one of the supported API types: 'azure', 'azure_ad', 'rubik_ai'"
            )


def _console_log_level():
    if brainai.log in ["debug", "info"]:
        return brainai.log
    elif brainai_LOG in ["debug", "info"]:
        return brainai_LOG
    else:
        return None


def log_debug(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def log_info(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)
    logger.info(msg)


def log_warn(message, **params):
    msg = logfmt(dict(message=message, **params))
    print(msg, file=sys.stderr)
    logger.warn(msg)


def logfmt(props):
    def fmt(key, val):
        # Handle case where val is a bytes or bytesarray
        if hasattr(val, "decode"):
            val = val.decode("utf-8")
        # Check if val is already a string to avoid re-encoding into ascii.
        if not isinstance(val, str):
            val = str(val)
        if re.search(r"\s", val):
            val = repr(val)
        # key should already be a string
        if re.search(r"\s", key):
            key = repr(key)
        return "{key}={val}".format(key=key, val=val)

    return " ".join([fmt(key, val) for key, val in sorted(props.items())])


def get_object_classes():
    # This is here to avoid a circular dependency
    from brainai.object_classes import OBJECT_CLASSES

    return OBJECT_CLASSES


def convert_to_brainai_object(
    resp,
    api_key=None,
    api_version=None,
    organization=None,
    engine=None,
    plain_old_data=False,
):
    # If we get a brainaiResponse, we'll want to return a brainaiObject.
    response_ms: Optional[int] = None
    if isinstance(resp, brainai.brainai_response.brainaiResponse):
        organization = resp.organization
        response_ms = resp.response_ms
        resp = resp.data

    if plain_old_data:
        return resp
    elif isinstance(resp, list):
        return [
            convert_to_brainai_object(
                i, api_key, api_version, organization, engine=engine
            )
            for i in resp
        ]
    elif isinstance(resp, dict) and not isinstance(resp, brainai.rebik_object.brainaiObject):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, str):
            klass = get_object_classes().get(klass_name, brainai.rebik_object.brainaiObject)
        else:
            klass = brainai.rebik_object.brainaiObject

        return klass.construct_from(
            resp,
            api_key=api_key,
            api_version=api_version,
            organization=organization,
            response_ms=response_ms,
            engine=engine,
        )
    else:
        return resp


def convert_to_dict(obj):
    """Converts a brainaiObject back to a regular dict.

    Nested brainaiObjects are also converted back to regular dicts.

    :param obj: The brainaiObject to convert.

    :returns: The brainaiObject as a dict.
    """
    if isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    # This works by virtue of the fact that brainaiObjects _are_ dicts. The dict
    # comprehension returns a regular dict and recursively applies the
    # conversion to each value.
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    else:
        return obj


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def default_api_key() -> str:
    if brainai.api_key_path:
        with open(brainai.api_key_path, "rt") as k:
            api_key = k.read().strip()
            if not api_key.startswith("sk-"):
                raise ValueError(f"Malformed API key in {brainai.api_key_path}.")
            return api_key
    elif brainai.api_key is not None:
        return brainai.api_key
    else:
        raise brainai.error.AuthenticationError(
            "No API key provided. You can set your API key in code using 'brainai.api_key = <API-KEY>', or you can set the environment variable brainai_API_KEY=<API-KEY>). If your API key is stored in a file, you can point the brainai module at it with 'brainai.api_key_path = <PATH>'. You can generate API keys in the brainai web interface. See https://platform.brainai.com/account/api-keys for details."
        )
