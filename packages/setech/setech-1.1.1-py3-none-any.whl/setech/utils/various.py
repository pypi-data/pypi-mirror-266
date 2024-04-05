import dataclasses
import json
import logging
from dataclasses import asdict
from typing import Any
from uuid import uuid4

from .parse import SetechJSONEncoder

__all__ = ["get_logger", "get_nonce", "shorten_dict_values", "shortify_log_dict"]


def get_logger(name: str = "service") -> logging.Logger:
    return logging.getLogger(name)


def shorten_dict_values(dct: dict) -> dict:
    res = {}
    for k, v in dct.items():
        if isinstance(v, str) and len(v) > 64:
            v = f"{v[:30]}...{v[-30:]}"
        elif isinstance(v, dict):
            v = shorten_dict_values(v)
        res[k] = v
    return res


def shortify_log_dict(dct: Any) -> dict[str, Any]:
    if dataclasses.is_dataclass(dct):
        dct = asdict(dct)
    return json.loads(json.dumps(shorten_dict_values(dct), cls=SetechJSONEncoder))


def get_nonce() -> str:
    return uuid4().hex[:12]
