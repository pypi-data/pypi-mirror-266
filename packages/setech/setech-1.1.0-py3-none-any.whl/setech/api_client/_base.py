import logging
from abc import ABC, abstractmethod
from typing import Any, Coroutine

import httpx
from pydantic import HttpUrl

from setech.utils import get_logger, get_nonce, shortify_log_dict

_TypeSyncAsyncResponse = httpx.Response | Coroutine[Any, Any, httpx.Response]


class BaseClient(ABC):
    base_url: HttpUrl
    _session: httpx._client.BaseClient
    _nonce: str
    _logger: logging.Logger

    def __init__(self, nonce: str = "", session: httpx._client.BaseClient | None = None):
        self._nonce = nonce or get_nonce()
        self._session = session or httpx.Client()
        self._logger = get_logger("APIClient")

    @abstractmethod
    def get(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def post(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def put(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def patch(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def delete(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def head(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def options(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def trace(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def connect(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def _request(self, method: str, endpoint: str, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    def _make_full_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def prepare_authentication(self, request: httpx.Request) -> httpx.Request:
        return request

    def _prepare_request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Request:
        full_url = self._make_full_url(endpoint)

        self._debug_log_request(method, full_url)
        request: httpx.Request = self._session.build_request(method=method, url=full_url, **kwargs)
        self._debug_log_prepared_request(request)
        self._debug(f"Prepared {request.method} request to '{request.url}'", extra=request.__dict__)

        self._info_log_request_sending(
            request, kwargs.get("content") or kwargs.get("files") or kwargs.get("data") or kwargs.get("json")
        )
        return request

    def _debug_log_request(self, method: str, full_url: str) -> None:
        self._debug(f"Preparing {method} request for '{full_url}'")

    def _debug_log_prepared_request(self, request: httpx.Request) -> None:
        self._debug(f"Prepared {request.method} request to '{request.url}'", extra=request.__dict__)

    def _info_log_request_sending(self, request: httpx.Request, log_payload: Any) -> None:
        self._info(
            f"Sending {request.method} request to '{request.url}' with payload={shortify_log_dict(log_payload)!r}",
            extra={"payload": shortify_log_dict(log_payload)},
        )

    def _info_log_response(self, response: httpx.Response) -> None:
        str_repr_content = response.content.decode("utf8")[:500]
        self._info(
            f"Response {response.status_code=} {str_repr_content=}",
            extra={"status_code": response.status_code, "content": str_repr_content},
        )

    def _info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("INFO", f"[{self._nonce}] {msg}", *args, **kwargs)

    def _debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("DEBUG", f"[{self._nonce}] {msg}", *args, **kwargs)

    def _warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("WARNING", f"[{self._nonce}] {msg}", *args, **kwargs)

    def _error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("ERROR", f"[{self._nonce}] {msg}", *args, **kwargs)

    def _critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("CRITICAL", f"[{self._nonce}] {msg}", *args, **kwargs)

    def _log(
        self, level: str, msg: object, *args: object, stacklevel: int = 5, extra: dict | None = None, **kwargs: Any
    ) -> None:
        extra = extra or {}
        extra.update(nonce=self._nonce)
        self._logger.log(
            logging.getLevelNamesMapping()[level], msg, *args, stacklevel=stacklevel, extra=extra, **kwargs
        )
