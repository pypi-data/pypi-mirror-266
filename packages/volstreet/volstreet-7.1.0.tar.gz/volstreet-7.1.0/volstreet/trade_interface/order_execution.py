from itertools import groupby
import asyncio
import threading
import numpy as np
from volstreet import config
from volstreet.utils.core import custom_round
from volstreet.utils.communication import log_error, notifier
from volstreet.config import logger, token_exchange_dict
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.angel_interface.interface import lookup_and_return, place_order_params
from volstreet.angel_interface.async_interface import (
    get_quotes_async,
    place_order_async,
    modify_order_async,
    unique_order_status_async,
)


order_placement_lock = threading.Lock()


def generate_order_params(
    symbol: str,
    token: str,
    qty: int,
    action: str,
    price: float | int,
    order_tag: str = "",
    stop_loss_order: bool = False,
) -> dict:
    """Price can be a str or a float because "market" is an acceptable value for price."""
    action = action.upper()
    order_tag = (
        "Automated Order" if (order_tag == "" or order_tag is None) else order_tag
    )
    exchange = token_exchange_dict[token]
    params = {
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": action,
        "exchange": exchange,
        "producttype": "CARRYFORWARD",
        "duration": "DAY",
        "quantity": int(qty),
        "ordertag": order_tag,
    }

    if stop_loss_order:
        execution_price = (
            price * 1.1
        )  # Hardcoded 10% buffer for execution price in sl orders
        params.update(
            {
                "variety": "STOPLOSS",
                "ordertype": "STOPLOSS_LIMIT",
                "triggerprice": round(price, 1),
                "price": round(execution_price, 1),
            }
        )
    else:
        order_type, execution_price = (
            ("MARKET", 0) if price == "MARKET" else ("LIMIT", price)
        )
        execution_price = custom_round(execution_price)
        params.update(
            {
                "variety": "NORMAL",
                "ordertype": order_type,
                "price": max(execution_price, 0.05),
            }
        )

    return params


def place_order(
    symbol: str,
    token: str,
    qty: int,
    action: str,
    price: str | float,
    order_tag: str = "",
    stop_loss_order: bool = False,
) -> str:
    params = generate_order_params(
        symbol, token, qty, action, price, order_tag, stop_loss_order
    )
    return place_order_params(params)


def update_order_params(
    current_params: dict, market_depth: dict, additional_buffer: float = 0
) -> dict:
    """Additional buffer is a percentage value that can further modify the price of the order.
    Additional buffer can be used when iteratively modifying orders to speed up the execution of persistently
    open orders."""

    action = current_params["transactiontype"]
    target_depth = "buy" if action == "SELL" else "sell"
    market_price = market_depth[target_depth][0]["price"]
    modifier = (
        (1 + config.LIMIT_PRICE_BUFFER + additional_buffer)
        if action == "BUY"
        else (1 - config.LIMIT_PRICE_BUFFER - additional_buffer)
    )

    new_price = market_price * modifier
    new_price = max(0.05, new_price)
    new_price = custom_round(new_price)

    modified_params = current_params.copy()
    modified_params["price"] = new_price
    current_params["price"] = new_price
    modified_params.pop("status")

    return modified_params


@log_error()
def cancel_pending_orders(order_ids, variety="STOPLOSS"):
    if isinstance(order_ids, (list, np.ndarray)):
        for order_id in order_ids:
            ActiveSession.obj.cancelOrder(order_id, variety)
    else:
        ActiveSession.obj.cancelOrder(order_ids, variety)


async def place_orders(list_of_orders: list[dict], session=None) -> list[str]:
    """Designed to be used for a specific action type.
    For example, all orders are BUY orders.
    """
    order_coros = [
        place_order_async(order, session=session) for order in list_of_orders
    ]
    results = await asyncio.gather(*order_coros)
    unique_ids = [result["uniqueorderid"] for result in results]
    return unique_ids


async def fetch_statuses(list_of_unique_ids: list[str], session=None) -> list[dict]:
    status_coros = [
        unique_order_status_async(unique_id, session=session)
        for unique_id in list_of_unique_ids
    ]
    # noinspection PyTypeChecker
    return await asyncio.gather(*status_coros)


async def modify_open_orders(
    open_orders: list[dict], ltp_data: dict, additional_buffer: float = 0, session=None
):
    modified_params = [
        update_order_params(
            order, ltp_data[order["symboltoken"]]["depth"], additional_buffer
        )
        for order in open_orders
    ]
    modify_coros = [modify_order_async(params, session) for params in modified_params]
    await asyncio.gather(*modify_coros)


def check_for_rejection(statuses: list[dict]):
    if any(status["status"] == "rejected" for status in statuses):
        notifier(
            f"One or more orders were rejected in batch: {statuses}",
            config.ERROR_NOTIFICATION_SETTINGS["url"],
            "ERROR",
            send_whatsapp=True,
        )
        raise Exception("One or more orders were rejected in batch.")


def filter_for_open_orders(statuses: list[dict]) -> list[dict]:
    open_order_statuses = ["open", "open pending", "modified", "modify pending", ""]
    open_orders = [
        status for status in statuses if status["status"] in open_order_statuses
    ]
    if not open_orders:
        return []
    open_orders_formatted = [
        {field: status[field] for field in config.modification_fields}
        for status in open_orders
    ]
    return open_orders_formatted


def calculate_average_price(orders: list, ids: list[str]) -> float:
    avg_prices = lookup_and_return(
        orders, ["uniqueorderid", "status"], [ids, "complete"], "averageprice"
    )
    return avg_prices.astype(float).mean() if avg_prices.size > 0 else np.nan


async def execute_orders_per_symbol(orders: list[dict], symbol: str, session=None):
    """
    Used to execute orders for a particular action type and symbol token.
    Executes orders in a loop until all orders are executed.
    Or max iterations are reached.
    Returns the average price of all executed orders.
    """
    if session is None:
        with ActiveSession.obj.async_session() as session:
            await execute_orders_per_symbol(orders, symbol, session)
            return

    order_ids = await place_orders(orders, session)
    statuses = await fetch_statuses(order_ids, session)
    check_for_rejection(statuses)
    open_orders = filter_for_open_orders(statuses)

    iteration = 0
    while open_orders:
        iteration += 1
        if iteration == 10:
            logger.error(f"Max modification iterations reached for symbol {symbol}.")
            break
        additional_buffer = iteration / 100
        ltp_data = await get_quotes_async(
            [order["symboltoken"] for order in open_orders], session=session
        )
        await modify_open_orders(open_orders, ltp_data, additional_buffer, session)
        statuses = await fetch_statuses(order_ids, session)
        check_for_rejection(statuses)
        open_orders = filter_for_open_orders(statuses)

    logger.info(f"Orders successfully executed for symbol {symbol}.")

    avg_price = calculate_average_price(statuses, order_ids)
    return avg_price


async def _execute_orders(orders: list[dict]) -> dict:
    """The difference between this function and execute_order_group is that this function
    can take in orders of different action types and symbols. It groups the orders
    into transaction types and symbol tokens and executes them in parallel, prioritizing
    buy orders to be executed first.
    """
    master_dict = {}
    orders.sort(key=lambda x: x["transactiontype"])
    orders_grouped_by_action = groupby(orders, key=lambda x: x["transactiontype"])

    async with ActiveSession.obj.async_session() as session:
        for action, orders_per_action in orders_grouped_by_action:
            orders_per_action = list(orders_per_action)
            orders_per_action.sort(key=lambda x: x["tradingsymbol"])
            orders_grouped_by_symbol = groupby(
                orders_per_action, key=lambda x: x["tradingsymbol"]
            )
            orders_grouped_by_symbol = {
                symbol: list(orders_per_symbol)
                for symbol, orders_per_symbol in orders_grouped_by_symbol
            }  # Just converting it to a dict
            order_tasks = [
                execute_orders_per_symbol([*orders], symbol, session)
                for symbol, orders in orders_grouped_by_symbol.items()
            ]
            avg_prices = await asyncio.gather(*order_tasks)

            for symbol, avg_price in zip(orders_grouped_by_symbol.keys(), avg_prices):
                # IMPORTANT: If orders contained buy and sell both for a single token
                # then this will overwrite the avg_price for that token with the sell avg_price
                # This is a limitation of the current implementation. It will be fixed in the future.
                master_dict[symbol] = avg_price

    return master_dict


async def execute_orders(orders: list[dict]) -> dict:
    with order_placement_lock:
        logger.info(f"{threading.current_thread().name} is executing orders.")
        result = await _execute_orders(orders)
        return result
