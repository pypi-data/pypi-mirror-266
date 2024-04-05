import asyncio
from collections import defaultdict
import functools
from volstreet.config import token_exchange_dict, logger
from volstreet.angel_interface.active_session import ActiveSession


def retry_on_error(func):
    """Only for async functions. Retries the function 5 times with exponential backoff if an error occurs."""

    @functools.wraps(func)
    async def async_wrapped(*args, **kwargs):
        sleep_time = 1
        for attempt in range(5):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                message = (
                    f"Attempt {attempt + 1} function {func.__name__} failed with error {e}. "
                    f"Retrying in {sleep_time} seconds."
                )
                if attempt < 4:
                    logger.warning(message, exc_info=True)
                    await asyncio.sleep(sleep_time)
                    sleep_time *= 1.2  # Exponential backoff
                else:
                    logger.error(f"Max attempts reached. {message}")
                    raise e

    return async_wrapped


@retry_on_error
async def get_ltp_async(params: dict, session=None):
    response = await ActiveSession.obj.async_get_ltp(params, session)
    return response["data"]["ltp"]


@retry_on_error
async def get_quotes_async(
    tokens: list, mode: str = "FULL", return_type="dict", session=None
):
    payload = defaultdict(list)
    for token in tokens:
        exchange = token_exchange_dict.get(token)
        if exchange:
            payload[exchange].append(token)
    payload = dict(payload)
    params = {"mode": mode, "exchangeTokens": payload}
    response = await ActiveSession.obj.async_get_quotes(params, session)

    # Formatting the response
    response = response["data"]["fetched"]
    if return_type.lower() == "dict":
        return {entry["symbolToken"]: entry for entry in response}
    elif return_type.lower() == "list":
        return response


@retry_on_error
async def place_order_async(params: dict, session=None):
    response = await ActiveSession.obj.async_place_order(params, session)
    return response["data"]


@retry_on_error
async def unique_order_status_async(unique_order_id: str, session=None):
    response = await ActiveSession.obj.async_unique_order_status(
        unique_order_id, session
    )
    return response["data"]


@retry_on_error
async def modify_order_async(params: dict, session=None):
    return await ActiveSession.obj.async_modify_order(params, session)
