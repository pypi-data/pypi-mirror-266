import dataclasses
import datetime
import decimal
import json
from typing import Any

from pydantic import BaseModel


def str_as_date(date_str: str, date_format: str = "%Y-%m-%d") -> datetime.date:
    datetime_object = datetime.datetime.strptime(date_str, date_format)
    return datetime_object.date()


def str_as_date_or_none(date_str: str | None, date_format: str = "%Y-%m-%d") -> datetime.date | None:
    if not isinstance(date_str, str):
        return None
    try:
        return str_as_date(date_str, date_format)
    except (ValueError, TypeError):
        return None


def as_decimal(decimal_str: str | int | float) -> decimal.Decimal:
    return decimal.Decimal(str(decimal_str))


def as_decimal_or_none(decimal_str: str | int | float | None) -> decimal.Decimal | None:
    if not isinstance(decimal_str, (str | int | float)):
        return None
    try:
        return as_decimal(decimal_str)
    except (decimal.DecimalException, TypeError):
        return None


class SetechJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        try:
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            if isinstance(obj, BaseModel):
                return obj.model_dump_json()
            if isinstance(obj, datetime.timedelta):
                return dict(__type__="timedelta", total_seconds=obj.total_seconds())
            if hasattr(obj, "as_dict"):
                if callable(getattr(obj, "as_dict")):
                    return super().default(obj.as_dict())
                return super().default(obj.as_dict)
            if dataclasses.is_dataclass(obj):
                return super().default(dataclasses.asdict(obj))
            if isinstance(obj, set):
                return list(obj)
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return super().default(obj)
        except TypeError as exc:
            if "not JSON serializable" in str(exc):
                return str(obj)
            raise exc
