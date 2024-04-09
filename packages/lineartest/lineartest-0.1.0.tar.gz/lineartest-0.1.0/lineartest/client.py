from collections.abc import Callable, Mapping
from typing import IO, Any

from starlette.testclient import TestClient

from ._log import LoggerBase
from ._type import BaseModelType, DefaultResponse


class LinearClient(LoggerBase):
    """The main entrypoint to use LinearTest."""

    def __init__(self, test_client: TestClient | None = None):
        """
        Initialize the `LinearClient` instance.
        :param test_client: the Starlette TestClient instance
        """
        super().__init__()
        self.test_client = test_client

    def _log(self, func: Callable, prefix: str, dct: dict[str, Any]):
        def inner(prefix: str, dct: dict[str, Any]):
            for key, value in dct.items():
                if isinstance(value, dict):
                    func(f'{prefix}{key}:')
                    inner(prefix + '  ', value)
                else:
                    func(f'{prefix}{key}={value!r}')

        inner(prefix, dct)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, IO[bytes]] | None = None,
        json: Mapping[str, Any] = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        follow_redirects: bool | None = None,
        allow_redirects: bool | None = None,
        response_model: type[BaseModelType] | None = None,
        **extra,
    ) -> BaseModelType | DefaultResponse:
        """
        Perform a request using the `TestClient` instance.
        :param method: the HTTP method to use
        :param url: the URL to request
        :param params: the query parameters to send
        :param data: the form data to send
        :param files: the files to send
        :param json: the JSON data to send
        :param headers: the headers to send
        :param cookies: the cookies to send
        :param follow_redirects: whether to follow redirects
        :param allow_redirects: whether to allow redirects
        :param response_model: the Pydantic model to validate the response
        :param extra: extra arguments to pass to the `TestClient` request method
        :return: the parsed response data in the type of given model or a default one
        """
        # log the start of the request
        self.info(f' REQUEST START: {method} {url} '.center(self.logging_width, '-'))

        # log prefix
        prefix = '------+ '

        # log params
        if params:
            self.info('>>> Request params:')
            self._log(self.info, prefix, params)

        # log data
        if data:
            self.info('>>> Request data:')
            self._log(self.info, prefix, data)

        # log files
        if files:
            self.info('>>> Request files:')
            self._log(self.info, prefix, {file.name for file in files})

        # log json
        if json:
            self.info('>>> Request JSON:')
            self._log(self.info, prefix, json)

        # log headers
        if headers:
            self.info('>>> Request headers:')
            self._log(self.info, prefix, headers)

        # log cookies
        if cookies:
            self.info('>>> Request cookies:')
            self._log(self.info, prefix, cookies)

        # use TestClient to perform the request
        response = self.test_client.request(
            method,
            url,
            params=params,
            data=data,
            files=files,
            json=json,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            allow_redirects=allow_redirects,
            **extra,
        )

        # check if response is JSON
        content_type = response.headers.get('Content-Type')
        error_message = f'expected response type to be "application/json", got {content_type} instead.'
        assert content_type == 'application/json', error_message
        response_dict = response.json()

        # log response
        self.info('<<< Response JSON:')
        self._log(self.info, prefix, response_dict)

        # log the end of the request
        self.info(f' REQUEST END: {method} {url} '.center(self.logging_width, '-'))

        # use the default response model if response_model not speficied
        if response_model is None:
            response_model = DefaultResponse

        # parse the json dictionary to response_model
        return response_model.parse_obj(response_dict)

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        follow_redirects: bool | None = None,
        allow_redirects: bool | None = None,
        response_model: type[BaseModelType] | None = None,
        **extra,
    ) -> BaseModelType | DefaultResponse:
        """
        Perform a GET request using the `TestClient` instance.
        :param url: the URL to request
        :param params: the query parameters to send
        :param headers: the headers to send
        :param cookies: the cookies to send
        :param follow_redirects: whether to follow redirects
        :param allow_redirects: whether to allow redirects
        :param response_model: the Pydantic model to validate the response
        :param extra: extra arguments to pass to the `TestClient` request method
        :return: the parsed response data in the type of given model or a default one
        """
        return self.request(
            'GET',
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            allow_redirects=allow_redirects,
            response_model=response_model,
            **extra,
        )

    def post(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, IO[bytes]] | None = None,
        json: Mapping[str, Any] = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        follow_redirects: bool | None = None,
        allow_redirects: bool | None = None,
        response_model: type[BaseModelType] | None = None,
        **extra,
    ) -> BaseModelType | DefaultResponse:
        """
        Perform a POST request using the `TestClient` instance.
        :param url: the URL to request
        :param params: the query parameters to send
        :param data: the form data to send
        :param files: the files to send
        :param json: the JSON data to send
        :param headers: the headers to send
        :param cookies: the cookies to send
        :param follow_redirects: whether to follow redirects
        :param allow_redirects: whether to allow redirects
        :param response_model: the Pydantic model to validate the response
        :param extra: extra arguments to pass to the `TestClient` request method
        :return: the parsed response data in the type of given model or a default one
        """
        return self.request(
            'POST',
            url,
            params=params,
            data=data,
            files=files,
            json=json,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            allow_redirects=allow_redirects,
            response_model=response_model,
            **extra,
        )
