import aiohttp
import json
import functools
from SmartApi.smartConnect import SmartConnect, urljoin
from volstreet.config import logger
from volstreet.angel_interface.access_rate_handlers import access_rate_handler


def log_request(func):
    """Only for async functions. Logs the request and response of the function."""

    @functools.wraps(func)
    async def async_wrapped(smart_connect, *args, **kwargs):
        logger.debug(f"Requesting {func.__name__} with args {args} and kwargs {kwargs}")
        response = await func(smart_connect, *args, **kwargs)
        logger.debug(f"Response from {func.__name__}: {response}")
        return response

    return async_wrapped


class AsyncSmartConnect(SmartConnect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def async_session(self):
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=self.ssl_context)
        )

    async def _async_request(
        self, route, method, parameters=None, appendage="", session=None
    ):
        if session is None:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_context)
            ) as session:
                return await self._async_request(
                    route, method, parameters, appendage, session
                )

        if appendage:
            url = urljoin(self._rootUrl, self._routes[route] + appendage)
            params = {}
        else:
            params = parameters.copy() if parameters else {}
            uri = self._routes[route].format(**params)
            url = urljoin(self.root, uri)

        headers = self.requestHeaders()

        if self.access_token:
            auth_header = self.access_token
            headers["Authorization"] = f"Bearer {auth_header}"

        try:
            async with session.request(
                method,
                url,
                data=json.dumps(params) if method in ["POST", "PUT"] else None,
                params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                headers=headers,
                verify_ssl=not self.disable_ssl,
                timeout=self.timeout,
            ) as response:
                try:
                    data = await response.json()
                    return data
                except Exception as e:
                    logger.error(
                        f"Error occurred while converting response. Response text: {await response.text()}, "
                    )
                    raise e

        except Exception as e:
            logger.error(
                f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}"
            )
            raise e

    async def async_delete_request(self, route, parameters=None, session=None):
        return await self._async_request(
            route, "DELETE", parameters, appendage="", session=session
        )

    async def async_get_request(self, route, parameters=None, session=None):
        return await self._async_request(
            route, "GET", parameters, appendage="", session=session
        )

    async def async_post_request(self, route, parameters=None, session=None):
        return await self._async_request(
            route, "POST", parameters, appendage="", session=session
        )

    async def async_put_request(self, route, parameters=None, session=None):
        return await self._async_request(
            route, "PUT", parameters, appendage="", session=session
        )

    async def async_login(self, user, password, totp, session=None):
        params = {"clientcode": user, "password": password, "totp": totp}
        login_result = await self.async_post_request("api.login", params, session)

        if login_result["status"] is True:
            self.setAccessToken(login_result["data"]["jwtToken"])
            self.setRefreshToken(login_result["data"]["refreshToken"])
            self.setFeedToken(login_result["data"]["feedToken"])
            user = self.getProfile(self.refresh_token)
            user_id = user["data"]["clientcode"]
            self.setUserId(user_id)
            user["data"]["jwtToken"] = "Bearer " + self.access_token
            user["data"]["refreshToken"] = self.refresh_token
            user["data"]["feedToken"] = self.feed_token
            return user
        else:
            return login_result

    @access_rate_handler(max_requests=9, per_seconds=1, is_async=True)
    @log_request
    async def async_get_ltp(self, params, session=None):
        response = await self.async_post_request("api.ltp.data", params, session)
        return response

    @access_rate_handler(max_requests=9, per_seconds=1, is_async=True)
    @log_request
    async def async_get_quotes(self, params, session=None):
        response = await self.async_post_request("api.market.data", params, session)
        return response

    @access_rate_handler(max_requests=19, per_seconds=1, is_async=True)
    @log_request
    async def async_place_order(self, order_params, session=None):
        params = {k: v for k, v in order_params.items() if v is not None}

        response = await self.async_post_request("api.order.place", params, session)
        if response is not None and response.get("status", False):
            if (
                "data" in response
                and response["data"] is not None
                and "orderid" in response["data"]
            ):
                return response
            else:
                logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
        return None

    @access_rate_handler(max_requests=19, per_seconds=1, is_async=True)
    @log_request
    async def async_modify_order(self, modified_params, session=None):
        params = modified_params
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.async_post_request("api.order.modify", params, session)
        return response

    @access_rate_handler(max_requests=9, per_seconds=1, is_async=True)
    @log_request
    async def async_unique_order_status(self, unique_order_id, session=None):
        response = await self._async_request(
            "api.individual.order.details",
            "GET",
            appendage=unique_order_id,
            session=session,
        )
        return response
