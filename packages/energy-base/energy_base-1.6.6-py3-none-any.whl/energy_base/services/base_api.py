from typing import Callable, Any

import requests
from requests import Response


class BaseServiceAPI:
    name: str = None
    base_url: str = None
    default_response_processor: Callable[[Response], Any] = None

    def request(self, method, path, data=None, json=None, params=None, headers=None,
                authenticator: Callable[[dict], dict] | None = 'default',
                response_processor: Callable[[Response], Any] | None = 'default'):
        """
        Make an HTTP request using the requests' library.

        Args:
            method: The HTTP method (GET, POST, PUT, DELETE, etc.).
            path: The API endpoint path.
            data: Dictionary or bytes to be sent in the body of the request (for form data).
            json: JSON serializable data to be sent in the body of the request (for JSON data).
            params: Query parameters as a dictionary.
            headers: Headers to be included in the request.
            authenticator: Optional authenticator function to handle authentication with headers.
                This function should modify the headers for authentication purposes.
                Example authenticator function:
                def my_authenticator(headers):
                    headers['Authorization'] = 'Bearer YOUR_ACCESS_TOKEN'
                    return headers

            response_processor: Optional function to process the response data.
                This function should take the requests.Response object as input and return processed data.
                Example response processor function:
                def process_response(response):
                    return response.json()

        Returns:
            The response data, processed if a response processor is provided.
        """

        if headers is None:
            headers = {}

        if callable(authenticator):
            headers = authenticator(headers)

        if authenticator == 'default' and hasattr(self, 'authenticate') and callable(self.authenticate):
            headers = self.authenticate(headers)

        response = requests.request(
            method=method,
            url=self.base_url + path,
            data=data,
            json=json,
            params=params,
            headers=headers,
            verify=False
        )

        if response_processor == 'default':
            if self.__class__.default_response_processor is not None:
                return self.__class__.default_response_processor(response)
            return response

        if response_processor is not None:
            return response_processor(response)

        return response

    def authenticate(self, headers: dict) -> dict:
        """
        Example authenticate method:
            authenticate(self, headers):
                headers['Authorization'] = 'Bearer YOUR_ACCESS_TOKEN'
                return headers
        :param headers:
        :return:
        """
        return headers

    def get(self, path, data=None, json=None, params=None, headers=None,
            authenticator: Callable[[dict], dict] | None = 'default',
            response_processor: Callable[[Response], Any] | None = 'default'):
        return self.request('get', path, data, json, params, headers, authenticator, response_processor)

    def post(self, path, data=None, json=None, params=None, headers=None,
             authenticator: Callable[[dict], dict] | None = 'default',
             response_processor: Callable[[Response], Any] | None = 'default'):
        return self.request('post', path, data, json, params, headers, authenticator, response_processor)

    def put(self, path, data=None, json=None, params=None, headers=None,
            authenticator: Callable[[dict], dict] | None = 'default',
            response_processor: Callable[[Response], Any] | None = 'default'):
        return self.request('put', path, data, json, params, headers, authenticator, response_processor)

    def patch(self, path, data=None, json=None, params=None, headers=None,
              authenticator: Callable[[dict], dict] | None = 'default',
              response_processor: Callable[[Response], Any] | None = 'default'):
        return self.request('patch', path, data, json, params, headers, authenticator, response_processor)
