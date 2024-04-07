from logging import getLogger
from typing import Any, Literal

import requests

from .utils import get_service_request_headers

logger = getLogger(__file__)


service_headers: dict[str, Any] = get_service_request_headers()

TYPE_SERVICES = Literal["learn", "iam", "payment", "media", "notify"]


def post(url, data=None, json=None, **kwargs):
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs["headers"] = {
        **service_headers,
        **kwargs.get("headers", {}),
    }
    return requests.post(url, data=data, json=json, **kwargs)


def get(url, params=None, **kwargs):
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs["headers"] = {
        **service_headers,
        **kwargs.get("headers", {}),
    }
    return requests.get(url, params=params, **kwargs)


def put(url, data=None, **kwargs):
    r"""Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs["headers"] = {
        **service_headers,
        **kwargs.get("headers", {}),
    }
    return requests.put(url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs["headers"] = {
        **service_headers,
        **kwargs.get("headers", {}),
    }
    return requests.patch(url, data=data, **kwargs)


def delete(url, **kwargs):
    r"""Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs["headers"] = {
        **service_headers,
        **kwargs.get("headers", {}),
    }
    return requests.delete(url, **kwargs)


class ServiceRequest:
    """
    Help to construct request with request headers for service request
    """

    def __init__(
        self, base_url: str, service: TYPE_SERVICES = "iam", version: str = "v1"
    ) -> None:
        self.service = service
        self.version = version
        self.base_url = base_url

    def construct_url(self, path: str) -> str:
        """generate service url with

        url = f"{base_url}/{service}/{version}/services/{path}/"

        Args:
            path (str): _description_

        Returns:
            str: _description_
        """
        base_url = self.base_url.rstrip("/")
        path = path.strip("/")
        url = f"{base_url}/{self.service}/{self.version}/services/{path}/"
        return url

    def post(self, path, data=None, json=None, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return post(self.construct_url(path), data=data, json=json, **kwargs)

    def get(self, path, params=None, **kwargs):
        r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return get(self.construct_url(path), params=params, **kwargs)

    def put(self, path: str, data=None, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return put(self.construct_url(path), data=data, **kwargs)

    def patch(self, path, data=None, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return patch(self.construct_url(path), data=data, **kwargs)

    def delete(self, path, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return delete(self.construct_url(path), **kwargs)
