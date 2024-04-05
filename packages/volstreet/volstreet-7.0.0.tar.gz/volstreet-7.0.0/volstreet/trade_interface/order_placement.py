from time import sleep
import numpy as np
import itertools
import asyncio
from volstreet.decorators import timeit
from volstreet import config
from volstreet.config import logger, order_placed
from volstreet.utils.core import time_to_expiry
from volstreet.utils.communication import notifier
from volstreet.angel_interface.interface import (
    fetch_book,
    lookup_and_return,
    fetch_quotes,
)
from volstreet.trade_interface.instruments import (
    Option,
    Strangle,
    Straddle,
    SyntheticFuture,
    Action,
)
from volstreet.trade_interface.order_execution import execute_orders


@timeit()
def place_option_order_and_notify(
    instrument: Option | Strangle | Straddle | SyntheticFuture,
    action: Action | str,
    qty_in_lots: int,
    prices: str | int | float | tuple | list | np.ndarray = "LIMIT",
    order_tag: str = "",
    webhook_url=None,
    stop_loss_order: bool = False,
    target_status: str = "complete",
    return_avg_price: bool = True,
    square_off_order: bool = False,
    **kwargs,
) -> list | tuple | float | None:
    """Returns either a list of order ids or a tuple of avg prices or a float of avg price"""

    def return_avg_price_from_orderbook(
        orderbook: list, ids: list | tuple | np.ndarray
    ):
        avg_prices = lookup_and_return(
            orderbook, ["orderid", "status"], [ids, "complete"], "averageprice"
        )
        return avg_prices.astype(float).mean() if avg_prices.size > 0 else None

    action = action.value if isinstance(action, Action) else action

    # If square_off_order is True, check if the expiry is within 3 minutes
    if square_off_order and time_to_expiry(instrument.expiry, in_days=True) < (
        3 / (24 * 60)
    ):
        logger.info(
            f"Square off order not placed for {instrument} as expiry is within 5 minutes"
        )
        return instrument.fetch_ltp() if return_avg_price else None

    notify_dict = {
        "order_tag": order_tag,
        "Underlying": instrument.underlying,
        "Action": action,
        "Expiry": instrument.expiry,
        "Qty": qty_in_lots,
    }

    order_params = {
        "transaction_type": action,
        "quantity_in_lots": qty_in_lots,
        "stop_loss_order": stop_loss_order,
        "order_tag": order_tag,
    }

    if isinstance(instrument, (Strangle, Straddle, SyntheticFuture)):
        notify_dict.update({"Strikes": [instrument.call_strike, instrument.put_strike]})
        order_params.update({"prices": prices})
    elif isinstance(instrument, Option):
        notify_dict.update(
            {"Strike": instrument.strike, "OptionType": instrument.option_type.value}
        )
        order_params.update({"price": prices})
    else:
        raise ValueError("Invalid instrument type")

    notify_dict.update(kwargs)

    if stop_loss_order:
        assert isinstance(
            prices, (int, float, tuple, list, np.ndarray)
        ), "Stop loss order requires a price"
        target_status = "trigger pending"

    # Placing the order
    order_ids = instrument.place_order(**order_params)

    if isinstance(order_ids, tuple):  # Strangle/Straddle/SyntheticFuture
        call_order_ids, put_order_ids = order_ids[0], order_ids[1]
        order_ids = list(itertools.chain(call_order_ids, put_order_ids))
    else:  # Option
        call_order_ids, put_order_ids = False, False

    order_placed.set()

    # Waiting for the orders to reflect
    sleep(0.5)

    order_book = fetch_book("orderbook")
    order_statuses_ = lookup_and_return(order_book, "orderid", order_ids, "status")
    if isinstance(order_statuses_, np.ndarray) and order_statuses_.size > 0:
        check_and_notify_order_placement_statuses(
            statuses=order_statuses_,
            target_status=target_status,
            webhook_url=webhook_url,
            **notify_dict,
        )
    else:
        notifier(
            f"Unable to check statuses. Order statuses is {order_statuses_} for orderid(s) {order_ids}. "
            f"Please confirm execution.",
            webhook_url,
            "ERROR",
        )

    if return_avg_price:
        if call_order_ids and put_order_ids:  # Strangle/Straddle/SyntheticFuture
            call_avg_price = (
                return_avg_price_from_orderbook(order_book, call_order_ids)
                or instrument.call_option.fetch_ltp()
            )
            put_avg_price = (
                return_avg_price_from_orderbook(order_book, put_order_ids)
                or instrument.put_option.fetch_ltp()
            )
            result = call_avg_price, put_avg_price
        else:  # Option
            avg_price = (
                return_avg_price_from_orderbook(order_book, order_ids)
                or instrument.fetch_ltp()
            )
            result = avg_price
        return result

    return order_ids


def check_and_notify_order_placement_statuses(
    statuses, target_status="complete", webhook_url=None, **kwargs
):
    order_prefix = (
        f"{kwargs['order_tag']}: "
        if ("order_tag" in kwargs and kwargs["order_tag"])
        else ""
    )
    order_message = [f"{k}-{v}" for k, v in kwargs.items() if k != "order_tag"]
    order_message = ", ".join(order_message)

    if all(statuses == target_status):
        logger.info(f"{order_prefix}Order(s) placed successfully for {order_message}")
    elif any(statuses == "rejected"):
        if all(statuses == "rejected"):
            notifier(
                f"{order_prefix}All orders rejected for {order_message}",
                [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
                "ERROR",
            )
            raise Exception("Orders rejected")
        notifier(
            f"{order_prefix}Some orders rejected for {order_message}. Please repair.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "CRUCIAL",
        )
    elif any(["open" in status or "modi" in status for status in statuses]):
        logger.info(
            f"{order_prefix}Orders open for {order_message}. Awaiting modification."
        )
    elif any(statuses == target_status):
        notifier(
            f"{order_prefix}Some orders successful for {order_message}. Please repair the remaining orders.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "CRUCIAL",
        )
    else:
        notifier(
            f"{order_prefix}No orders successful. Please intervene.",
            [config.ERROR_NOTIFICATION_SETTINGS["url"], webhook_url],
            "ERROR",
        )
        raise Exception("No orders successful")


def generate_bulk_params(
    instructions: dict[Option | Strangle | Straddle | SyntheticFuture, dict]
) -> list[dict]:

    def fetch_market_depth(instruments):
        option_tokens = {
            instrument.token
            for instrument in instruments
            if isinstance(instrument, Option)
        }
        strangle_tokens = {
            token
            for instrument in instruments
            if isinstance(instrument, (Strangle, Straddle, SyntheticFuture))
            for token in (instrument.call_token, instrument.put_token)
        }
        tokens = option_tokens | strangle_tokens
        return fetch_quotes(tokens, structure="dict")

    order_params = []

    # if all params contain "price" key, then we don't need to fetch ltp_cache
    if not all("price" in params for params in instructions.values()):
        ltp_cache = fetch_market_depth(
            [
                instr
                for instr in instructions.keys()
                if "price" not in instructions[instr]
            ]
        )
    else:
        ltp_cache = {}

    for instr, params in instructions.items():
        action = params["action"]

        if isinstance(instr, Option):
            target_depth = (~action).value.lower()
            price = params.pop(
                "price", ltp_cache[instr.token]["depth"][target_depth][0]["price"]
            )
            modifier = (
                (1 + config.LIMIT_PRICE_BUFFER)
                if action == Action.BUY
                else (1 - config.LIMIT_PRICE_BUFFER)
            )
            price *= modifier
            order_params.extend(instr.generate_order_params(**params, price=price))

        elif isinstance(instr, (Strangle, Straddle, SyntheticFuture)):
            call_target_depth = (~action).value.lower()
            put_target_depth = (
                action.value.lower()
                if isinstance(instr, SyntheticFuture)
                else (~action).value.lower()
            )
            call_price, put_price = (
                ltp_cache[instr.call_token]["depth"][call_target_depth][0]["price"],
                ltp_cache[instr.put_token]["depth"][put_target_depth][0]["price"],
            )
            if isinstance(instr, SyntheticFuture):
                call_modifier, put_modifier = (
                    (1 + config.LIMIT_PRICE_BUFFER, 1 - config.LIMIT_PRICE_BUFFER)
                    if action == Action.BUY
                    else (1 - config.LIMIT_PRICE_BUFFER, 1 + config.LIMIT_PRICE_BUFFER)
                )
            else:
                call_modifier = put_modifier = (
                    (1 + config.LIMIT_PRICE_BUFFER)
                    if action == Action.BUY
                    else (1 - config.LIMIT_PRICE_BUFFER)
                )

            call_price, put_price = call_price * call_modifier, put_price * put_modifier
            order_params.extend(
                instr.generate_order_params(**params, price=(call_price, put_price))
            )

    return order_params


@timeit()
def execute_instructions(
    instructions: dict[Option | Strangle | Straddle | SyntheticFuture, dict]
) -> dict[Option | Strangle | Straddle | SyntheticFuture, float]:
    """Executes orders for a given set of instructions.
    Instructions is a dictionary where the keys are Instrument objects and
    the values are dictionaries containing the order parameters.
    The order parameters MUST contain the following keys:
    - action: Action.BUY or Action.SELL
    - quantity_in_lots: int
    - order_tag: str (optional)
    """

    def identify_average_prices(instruments, avg_prices: dict[str, float]) -> dict:

        average_price_dict = {}  # The new dict to be returned
        for instr in instruments:
            if isinstance(instr, Option):
                average_price_dict[instr] = avg_prices[instr.symbol]
            else:
                call_instr, put_instr = instr.call_option, instr.put_option
                average_price_dict[instr] = (
                    avg_prices[call_instr.symbol],
                    avg_prices[put_instr.symbol],
                )

        return average_price_dict

    # Filtering out close to expiry options (defined by less than 5 minutes)
    # if their instructions contain square_off_order=True
    # But we need to store the original instructions so that we can add closing prices
    # as average prices
    og_instructions = instructions.copy()
    instructions = {
        instr: params
        for instr, params in instructions.items()
        if not (
            params.pop("square_off_order", False)
            and time_to_expiry(instr.expiry, in_days=True) < (5 / (24 * 60))
        )
    }
    order_params = generate_bulk_params(instructions)
    average_prices = asyncio.run(execute_orders(order_params))
    average_prices = identify_average_prices(instructions.keys(), average_prices)

    average_prices.update(
        {
            instr: instr.fetch_ltp()
            for instr in og_instructions
            if instr not in instructions
        }
    )
    return average_prices
