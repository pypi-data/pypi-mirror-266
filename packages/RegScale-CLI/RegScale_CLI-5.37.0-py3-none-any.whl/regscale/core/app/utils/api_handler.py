from os import getenv
from typing import Optional, Dict, Any, List, Union
from urllib import parse
from urllib.parse import urljoin

from regscale.core.app import create_logger
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.login import verify_token, login, parse_user_id_from_jwt

logger = create_logger()


class APIRetrieveError(Exception):
    """Exception raised when there is an error retrieving data via API."""

    pass


class APIInsertionError(Exception):
    """Exception raised when there is an error inserting data into the API."""

    pass


class APIUpdateError(Exception):
    """Exception raised when there is an error updating data in the API."""

    pass


class APIResponseError(Exception):
    """Exception raised when there is an error in the API response."""

    pass


class APIHandler(Application):
    """Class to handle API requests."""

    def __init__(self):
        logger.debug("Instantiating APIHandler")
        super().__init__()
        self.api = Api()
        self.domain = self.config.get("domain")
        self.api = Api(retry=0)
        Application().api_handler = self
        self.endpoint_tracker = {}  # Initialize the endpoint tracker

    def _handle_login_on_401(
        self,
        retry_login: bool = True,
    ) -> bool:
        """
        Handle login on 401.

        :param bool retry_login: Whether to retry login or not, defaults to True
        :return: True if login was successful, False otherwise
        :rtype: bool
        """
        token = self.config.get("token")
        if token and "Bearer " in token:
            token = token.split("Bearer ")[1]
        logger.debug("verifying token")
        is_token_valid = verify_token(app=self, token=token)
        logger.debug(f"is token valid: {is_token_valid}")
        if not is_token_valid:
            logger.debug("getting new token")
            new_token = login(
                app=self,
                str_user=getenv("REGSCALE_USERNAME"),
                str_password=getenv("REGSCALE_PASSWORD"),
                host=self.domain,
            )
            logger.debug("Token: %s", new_token[:20])
            return retry_login
        return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        query: Optional[str] = None,
        files: Optional[List[Any]] = None,
        params: Optional[Any] = None,
        retry_login: bool = True,
    ) -> Any:
        """
        Generic function to make API requests.

        :param str method: HTTP method ('get', 'post', 'put')
        :param str endpoint: API endpoint, domain is added automatically
        :param Dict[str, Any] headers: Optional headers
        :param Union[Dict[str, Any], List[Any]] data: Data to send
        :param Any params: Optional query parameters
        :return: Response data or None
        """
        # Record the endpoint and method, incrementing the call count
        if endpoint not in self.endpoint_tracker:
            self.endpoint_tracker[endpoint] = {"count": 0, "methods": set()}
        self.endpoint_tracker[endpoint]["count"] += 1
        self.endpoint_tracker[endpoint]["methods"].add(method)

        response = None
        try:
            url = urljoin(self.domain, parse.quote(endpoint))
            logger.debug(f"[API_HANDLER] - Making {method.upper()} request to {url}")
            if method == "get":
                response = self.api.get(url, headers=headers, params=params)
            elif method == "delete":
                response = self.api.delete(url, headers=headers)
            elif method == "post" and files:
                response = getattr(self.api, method)(url, headers=headers, data=data, params=params, files=files)
            elif method == "graph":
                response = getattr(self.api, method)(
                    query=query,
                    headers=headers,
                )
            else:
                response = getattr(self.api, method)(url, headers=headers, json=data, params=params)
            if getattr(response, "status_code", 0) == 401:
                self._handle_login_on_401(
                    retry_login=retry_login,
                )
                if retry_login:
                    logger.debug("Retrying request with new token.")
                    return self._make_request(
                        method=method,
                        endpoint=endpoint,
                        headers=headers,
                        data=data,
                        files=files,
                        params=params,
                        retry_login=False,
                    )
            return response
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            if response is not None:
                logger.error(f"Response Code: {response.status_code} - {response.text}")
            return response

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Fetch a record from RegScale.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Any params: Optional query parameters
        :return: Response data or None
        """
        return self._make_request("get", endpoint, headers=headers, params=params)

    def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        files: Optional[List[Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Insert new data into an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Union[Dict[str, Any], List[Any]] data: Data to send
        :param List[Any] files: Files to send
        :param Any params: Optional query parameters
        :return: Response data or None
        """
        return self._make_request(
            "post",
            endpoint,
            headers=headers,
            data=data,
            params=params,
            files=files,
        )

    def put(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        data: Union[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Update existing data in an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Dict[str, Any] data: Data to send
        :param Any params: Optional query parameters
        :return: Response data or None
        """
        return self._make_request("put", endpoint, headers=headers, data=data, params=params)

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Any] = None,
    ) -> Any:
        """
        Delete existing data in an API endpoint.

        :param str endpoint: API endpoint
        :param Dict[str, Any] headers: Optional headers
        :param Any params: Optional query parameters
        :return: Response data or None
        """
        return self._make_request("delete", endpoint, headers=headers, params=params)

    def graph(self, query: str) -> Any:
        """
        Fetch data from the graph API.

        :param str query: GraphQL query
        :return: Response data or None
        :rtype: Any
        """
        return self._make_request("graph", "/graphql", query=query)

    def get_user_id(self) -> str:
        """
        Get the user ID of the current user.

        :return: The user ID of the current user.
        :rtype: str
        """
        return parse_user_id_from_jwt(self, self.config["token"])

    def log_api_summary(self):
        # write the summary, sorting by call count in descending order
        logger.info("APIHandler instance is being destroyed. Summary of API calls:")
        for endpoint, details in sorted(
            self.endpoint_tracker.items(),
            key=lambda item: item[1]["count"],
            reverse=True,
        ):
            methods = ", ".join(details["methods"])
            count = details["count"]
            logger.debug(f"Endpoint '{endpoint}' was called {count} times with methods: {methods}")
